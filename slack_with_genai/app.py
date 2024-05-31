import os
import logging
import re
import json
from textwrap import indent
import requests
from fastapi import APIRouter, Request, Response
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from openai import OpenAI

from service import data_service

logging.basicConfig(level=logging.INFO)

app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)
app_handler = SlackRequestHandler(app=app)

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

import os
import requests

def download_file(file_url, headers):
    response = requests.get(file_url, headers=headers)
    if response.status_code == 200:
        filename = file_url.split("/")[-1]
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"File {filename} downloaded successfully.")
        return filename
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        return None

def upload_file(file_path, upload_url, user):
    headers = {
        'Authorization': f'Bearer {os.getenv("DIFY_API_KEY")}',
    }
    with open(file_path, 'rb') as f:
        files = {
            'file': (os.path.basename(file_path), f, 'image/png'),  # MIMEタイプを適切に設定
        }
        data = {
            'user': user
        }
        response = requests.post(url=upload_url, headers=headers, files=files, data=data)
        print(f"Upload response: {response.text}")
        return response

@app.event("message")
def message_handler(body, say):
    event = body['event']
    text = event['text']
    channel = event['channel']
    user = event['user']
    thread_ts = event.get('thread_ts', event['ts'])
    files = event.get('files', None)

    # Botからのメッセージを無視
    if user == client.auth_test()['user_id']:
        return
    
    headers = {
        'Authorization': f'Bearer {os.getenv("SLACK_USER_TOKEN")}'
    }

    uploaded_files = []
    if files:
        for file_info in files:
            file_url = file_info['url_private']
            file_path = download_file(file_url, headers)
            if file_path:
                uploaded_files.append(file_path)
    
    uploaded_file_id = ""
    # ファイルのアップロード
    # Todo 複数ファイルのアップロードに対応する
    if uploaded_files:
        upload_url = os.getenv("DIFY_FILE_UPLOAD_ENDPOINT")
        # for file_path in uploaded_files:
        #     upload_response = upload_file(file_path, upload_url)
        #     # アップロード後、ローカルファイルを削除する場合
        #     os.remove(file_path)
        upload_response = upload_file(file_path=uploaded_files[0], upload_url=upload_url, user=user)
        uploaded_file_id = upload_response.json().get("id")
    
    # conversation_id の取得
    conversation_id = data_service.get_conversation_id(thread_ts=thread_ts)

    response = call_dify(query=text, user=user, conversation_id=conversation_id, file_id=uploaded_file_id)
    
    if response is None:
        response_body = "Sorry, there was an error processing your request."
    else:
        response_body = response.json().get("answer")
        if conversation_id is None:
            conversation_id = response.json().get("conversation_id")
            # conversation_id の登録
            data_service.insert_thread_mapping(thread_ts=thread_ts, conversation_id=conversation_id)

    say(text=response_body, channel=channel, thread_ts=thread_ts)

# 他の部分はそのまま

def get_thread_history(channel, thread_ts):
    try:
        result = client.conversations_replies(channel=channel, ts=thread_ts, inclusive=True, limit=50)
        messages = result['messages']
        return messages
    except SlackApiError as e:
        logging.error(f"Error fetching conversation history: {e.response['error']}")
        return []

# OpenAI
client_openai = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def call_chat(messages: list) -> str:
    # スレッドのメッセージ履歴をフォーマット
    conversation = []
    for msg in messages:
        print(f"user: {msg['user']}")
        # MemberID でフィルタ
        role = "assistant" if msg['user'] == "U06JCGQGUMA" else "user"
        conversation.append({"role": role, "content": msg['text']})

    # ロギング
    logging.info("Sending the following messages to OpenAI:")
    for msg in conversation:
        logging.info(f"{msg['role']}: {msg['content']}")

    completion = client_openai.chat.completions.create(
        model=os.getenv("CHAT_MODEL_GPT4o"),
        messages=[
            {
                "role": "system",
                "content": f"""あなたは親切で丁寧な対話型アシスタントです。
                    ユーザの質問や要求に対して、もし曖昧な点や複数の解釈が可能な場合は、ユーザの意図を明確にするための質問を返してください。
                    ユーザの真の意図を理解した上で、的確な応答を心がけてください。"""
            }
        ] + conversation
    )

    return completion.choices[0].message.content

api = APIRouter(prefix="/slack")

@api.get("/test")
async def test_endpoint():
    return {"message": "Working!"}

@api.post("/events", name="slack events")
async def events(request: Request) -> Response:
    return await app_handler.handle(request)

def call_dify(query: str, user: str, conversation_id: str, file_id: str):
    # Todo 暫定で、DifyのユーザIDを使用
    # tmp_user = os.getenv("DIFY_TMP_USER")

    url = os.getenv("DIFY_CHAT_ENDPOINT")

    headers = {
        'Authorization': f'Bearer {os.getenv("DIFY_API_KEY")}',
        'Content-Type': 'application/json',
    }

    data = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "conversation_id": conversation_id,
        "user": user
    }

    # files が空でない場合のみ data に追加
    if file_id:
        print(f"upload_file_id: {file_id}")
        data["files"] = [
            {
                "type": "image",
                "transfer_method": "local_file",
                "upload_file_id": file_id
            }
        ]

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    return response

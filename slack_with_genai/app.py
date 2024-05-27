import os
import logging

from fastapi import APIRouter, Request, Response
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)
app_handler = SlackRequestHandler(app=app)

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

@app.event("message")
def message_handler(body, say):
    event = body['event']
    text = event['text']
    channel = event['channel']
    user = event['user']
    thread_ts = event.get('thread_ts', event['ts'])

    # Botからのメッセージを無視
    if user == client.auth_test()['user_id']:
        return

    # スレッドのメッセージ履歴を取得
    messages = get_thread_history(channel, thread_ts)
    response = call_chat(text, messages)
    response_body = f"{response}"

    say(text=response_body, channel=channel, thread_ts=thread_ts)

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

def call_chat(message: str, messages: list) -> str:
    # スレッドのメッセージ履歴をフォーマット
    conversation = []
    for msg in messages:
        print(f"user: {msg['user']}")
        # MemberID でフィルタ
        role = "assistant" if msg['user'] == "U06JCGQGUMA" else "user"
        conversation.append({"role": role, "content": msg['text']})
    
    # conversation.append({
    #     "role": "user",
    #     "content": message
    # })

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


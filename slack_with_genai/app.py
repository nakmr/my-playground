import os 
from dotenv import load_dotenv

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI

load_dotenv()

# Appの初期化
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

@app.event("app_mention")
def mention_handler(body, say):
    mention = body['event']
    text = mention['text']
    channel = mention['channel']
    thread_ts = mention['ts']
    user = mention['user']

    print(f'Mentioned!: {text}')

    response = call_chat(text)
    response_body = f"<@{user}> {response}"

    say(text=response_body, channel=channel, thread_ts=thread_ts)

# OpanAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def call_chat(message: str) -> str:
    completion = client.chat.completions.create(
        model=os.getenv("CHAT_MODEL_GPT4o"),
        messages=[
            {
                "role": "system",
                "content": f"""あなたは親切で丁寧な対話型アシスタントです。
                    ユーザの質問や要求に対して、もし曖昧な点や複数の解釈が可能な場合は、ユーザの意図を明確にするための質問を返してください。
                    ユーザの真の意図を理解した上で、的確な応答を心がけてください。"""
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    return completion.choices[0].message.content


if __name__ == "__main__":
    app.start(port=int(os.getenv("PORT", 3000)))


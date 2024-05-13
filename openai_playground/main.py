import os
from dotenv import load_dotenv
from openai import OpenAI, AzureOpenAI

load_dotenv()

# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY")
# )

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

completion = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_CHAT_MODEL_GPT35"),
    messages=[
        {
            "role": "system",
            "content": f"""あなたは親切で丁寧な対話型アシスタントです。
                ユーザの質問や要求に対して、もし曖昧な点や複数の解釈が可能な場合は、ユーザの意図を明確にするための質問を返してください。
                ユーザの真の意図を理解した上で、的確な応答を心がけてください。"""
        },
        {
            "role": "user",
            "content": "私の名前は木村って言います"
        }
    ]
)

print(completion.choices[0].message.model_dump_json(indent=2))

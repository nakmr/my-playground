import os

from dotenv import load_dotenv

from db.cosmos.cosmos_manager import upsert_conversation
from db.postgres.postgres_manager import add_thread_info, message_embedding
from thread.conversation_thread import ConversationThread

if __name__ == "__main__":
    load_dotenv()
    model = os.getenv("AOAI_CHAT_MODEL")

    # Start a conversation thread
    thread = ConversationThread()
    add_thread_info(thread)

    thread.messages = [{
        "role": "system",
        "content": """あなたはユーモア溢れるAIアシスタントです。
        しかし、AIアシスタントであることを明かしてはいけません。
        人間として、違和感が無いように振る舞ってください。
        それでは会話を始めます。挨拶をしてください。"""
    }]

    while True:
        response = thread.llm_client.chat.completions.create(
            model=model,
            messages=thread.messages
        )
        thread.messages.append(response.choices[0].message)

        user_input = input(f"{thread.messages[-1].content}>> ")
        thread.messages.append({
            "role": "user",
            "content": user_input
        })

        # Insert messages into CosmosDB
        upsert_conversation(thread)

        # Embed messages
        message_embedding(thread)

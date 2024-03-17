import uuid

from azure.cosmos import CosmosClient, PartitionKey
import os
from dotenv import load_dotenv
import azure.cosmos.exceptions as exceptions
from db.cosmos.cosmos_manager import upsert_conversation
from db.postgres.postgres_manager import call_postgres, call_postgres_embedding, add_thread_info
from openai import AzureOpenAI
from thread.conversation_thread import ConversationThread


if __name__ == "__main__":
    load_dotenv()

    thread = ConversationThread()
    add_thread_info(thread)

    client = AzureOpenAI(
        azure_endpoint=os.getenv("AOAI_ENDPOINT"),
        api_key=os.getenv("AOAI_API_KEY"),
        api_version=os.getenv("AOAI_API_VERSION")
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
        {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
        {"role": "user", "content": "Do other Azure AI services support this too?"}
    ]

    # Cosmosを呼び出す
    # call_cosmos()
    upsert_conversation(messages, thread)

    response = client.chat.completions.create(
        model=os.getenv("AOAI_CHAT_MODEL"),
        messages=messages
    )

    messages.append(response.choices[0].message)

    upsert_conversation(messages, thread)


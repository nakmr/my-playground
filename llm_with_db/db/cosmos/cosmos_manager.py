from azure.cosmos import CosmosClient, PartitionKey
import os
import uuid
from openai.types.chat.chat_completion import ChatCompletionMessage


def upsert_conversation(messages: list, thread):
    HOST = os.getenv('COSMOS_HOST')
    COSMOS_ACCOUNT_KEY = os.getenv('COSMOS_ACCOUNT_KEY')
    COSMOS_DATABASE_ID = os.getenv('COSMOS_DATABASE_ID')
    COSMOS_CONTAINER_ID = os.getenv('COSMOS_CONTAINER_ID')

    # CosmosDBクライアントの作成
    client = CosmosClient(HOST, {'masterKey': COSMOS_ACCOUNT_KEY})

    # データベースとコンテナの取得（存在しない場合は作成）
    database_name = client.create_database_if_not_exists(id=COSMOS_DATABASE_ID)

    container_name = database_name.create_container_if_not_exists(
        id=COSMOS_CONTAINER_ID,
        partition_key=PartitionKey(path='/id')
    )

    # Get database and container client
    db = client.get_database_client(database_name)
    container = db.get_container_client(container_name)

    # Create conversation history object
    new_conversation = {
        "id": str(thread.id),
        "user_id": thread.user_id,
        "messages": str(messages)
    }

    try:
        upserted_item = container.upsert_item(new_conversation)
        print(f"Upserted conversation detail with ID: {upserted_item['id']}")
    except Exception as e:
        print(f"Error upserting conversation: {str(e)}")

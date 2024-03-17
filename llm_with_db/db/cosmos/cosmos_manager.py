# -*- coding: utf-8 -*-
"""

CosmosDBとの接続およびデータの操作を行うモジュール。

"""
import os

from azure.cosmos import CosmosClient, PartitionKey, ContainerProxy


def get_container_client() -> ContainerProxy:
    """

    CosmosDBのcontainerクライアントを取得する。

    Returns: ContainerProxy

    """
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
    return db.get_container_client(container_name)


def upsert_conversation(thread) -> None:
    """

    会話履歴をUpsertする。

    Args:
        thread: ConversationThreadオブジェクト

    Returns: None

    """
    container = get_container_client()

    # Create thread detail object
    thread_detail = {
        "id": str(thread.id),
        "user_id": str(thread.user_id),
        "messages": str(thread.messages)
    }

    try:
        upserted_item = container.upsert_item(thread_detail)
        print(f"Upserted conversation detail with ID: {upserted_item['id']}")
    except Exception as e:
        print(f"Error upserting conversation: {str(e)}")

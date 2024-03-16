from azure.cosmos import CosmosClient, PartitionKey
import os

# CosmosDBの接続情報

def call_cosmos():

    HOST = os.getenv('COSMOS_HOST')
    COSMOS_ACCOUNT_KEY = os.getenv('COSMOS_ACCOUNT_KEY')
    COSMOS_DATABASE_ID = os.getenv('COSMOS_DATABASE_ID')
    COSMOS_CONTAINER_ID = os.getenv('COSMOS_CONTAINER_ID')

    # CosmosDBクライアントの作成
    client = CosmosClient(HOST, {'masterKey': COSMOS_ACCOUNT_KEY})

    # データベースとコンテナの取得（存在しない場合は作成）
    database_name = client.create_database_if_not_exists(id=COSMOS_DATABASE_ID)
    print(f"Database with id `{COSMOS_DATABASE_ID}` created")

    container_name = database_name.create_container_if_not_exists(
        id=COSMOS_CONTAINER_ID,
        partition_key=PartitionKey(path='/category')
    )
    print(f"Container with id `{COSMOS_CONTAINER_ID} created")

    # Get database and container client
    db = client.get_database_client(database_name)
    container = db.get_container_client(container_name)

    # Create Data
    new_item = {
        "id": "70b63682-b93a-4c77-aad2-65501347265f",
        "category": "gear-surf-surfboards",
        "name": "Yamba Surfboard",
        "quantity": 12,
        "sale": False,
    }
    created_item = container.upsert_item(new_item)



    # Retrieve Data
    existing_item = container.read_item(
        item="70b63682-b93a-4c77-aad2-65501347265f",
        partition_key="gear-surf-surfboards",
    )

    print(existing_item)

    client.delete_database(database_name)


    print("run_sample done")

    # container = database.create_container_if_not_exists(
    #     id=container_name,
    #     partition_key=PartitionKey(path='/conversation_id')
    # )
    #
    # # 会話の詳細データの作成
    # conversation_detail = {
    #     'conversation_id': 'conv_123',
    #     'user_id': 'user_456',
    #     'messages': [
    #         {
    #             'message_id': 'msg_1',
    #             'text': 'Hello, how can I assist you today?',
    #             'timestamp': '2023-04-25T10:00:00Z',
    #             'sender': 'assistant',
    #             'sentiment': 0.8,
    #             'entities': ['assist'],
    #             'intent': 'greeting'
    #         },
    #         {
    #             'message_id': 'msg_2',
    #             'text': 'I need help with my order.',
    #             'timestamp': '2023-04-25T10:01:00Z',
    #             'sender': 'user',
    #             'sentiment': 0.2,
    #             'entities': ['order', 'help'],
    #             'intent': 'order_assistance'
    #         }
    #     ]
    # }

    # コンテナにデータを追加
    # container.create_item(body=conversation_detail)
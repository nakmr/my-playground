from azure.cosmos import CosmosClient, PartitionKey
import os
from dotenv import load_dotenv
import azure.cosmos.exceptions as exceptions
from db.cosmos.cosmos_manager import call_cosmos
from db.postgres.postgres_manager import call_postgres


if __name__ == "__main__":
    load_dotenv()

    # Cosmosを呼び出す
    # call_cosmos()

    # Postgresを呼び出す
    call_postgres()

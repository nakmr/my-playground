from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AppServices
from diagrams.azure.compute import FunctionApps
from diagrams.azure.database import DatabaseForPostgresqlServers, CosmosDb
from diagrams.azure.storage import BlobStorage
from diagrams.custom import Custom
from diagrams.onprem.client import User

with Diagram("LLM with Message DB", show=False):
    user = User("User")

    with Cluster("Chat App"):
        llm_app = AppServices("LLM App")
        aoai = Custom("Chat & Embedding", icon_path="./openai/openai-logomark.png")
        with Cluster("DB for messages"):
            pg = DatabaseForPostgresqlServers("Thread Info")
            cosmos = CosmosDb("All messages")
            llm_db = [pg, cosmos, aoai]

        # aoai - Edge(label="RAG") - pg
        llm_app >> llm_db
        llm_app << llm_db


    user >> llm_app
    user << llm_app

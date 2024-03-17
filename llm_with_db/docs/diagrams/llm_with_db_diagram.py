from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AppServices
from diagrams.azure.compute import FunctionApps
from diagrams.azure.database import DatabaseForPostgresqlServers, CosmosDb
from diagrams.azure.storage import BlobStorage
from diagrams.custom import Custom
from diagrams.onprem.client import User

with Diagram("LLM with DB Architecture", show=False):
    user = User("User")

    with Cluster("Chat App"):
        llm_app = AppServices("LLM App")
        aoai = Custom("Chat & Embedding", icon_path="./openai/openai-logomark.png")
        with Cluster("DB for messages"):
            pg = DatabaseForPostgresqlServers("Thread Info")
            cosmos = CosmosDb("All messages")
            llm_db = [pg, cosmos, aoai]

    with Cluster("External Data"):
        embedding = Custom("Embedding", icon_path="./openai/openai-logomark.png")
        with Cluster("DB for external files"):
            blob = BlobStorage("External files")
            blob_function = FunctionApps("Functions")
            pg_external = DatabaseForPostgresqlServers("Embedded external files")
            blob >> blob_function >> embedding
            blob_function >> pg_external
            external_data = [blob]
            external_db = [pg_external]

    user >> Edge(label="Chat with LLM App") >> llm_app >> llm_db
    user >> Edge(label="Register external files") >> external_data
    llm_app >> external_db

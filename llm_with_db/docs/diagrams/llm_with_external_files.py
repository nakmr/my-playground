from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AppServices
from diagrams.azure.compute import FunctionApps
from diagrams.azure.database import DatabaseForPostgresqlServers, CosmosDb
from diagrams.azure.storage import BlobStorage
from diagrams.custom import Custom
from diagrams.onprem.client import User

with Diagram("LLM with External Files", show=False):
    user = User("User")

    with Cluster("Chat App"):
        llm_app = AppServices("LLM App")

    with Cluster("External Data"):
        embedding = Custom("Embedding", icon_path="./openai/openai-logomark.png")
        with Cluster("DB for external files"):
            blob = BlobStorage("External files")
            blob_function = FunctionApps("Functions")
            pg_external = DatabaseForPostgresqlServers("Embedded external files")
            blob >> blob_function >> embedding
            blob_function << embedding
            blob_function >> pg_external
            external_data = [blob]
            external_db = [pg_external]

    user >> external_data
    llm_app >> external_db
    llm_app << external_db

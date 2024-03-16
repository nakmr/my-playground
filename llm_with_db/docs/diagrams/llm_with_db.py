from diagrams import Diagram
from diagrams.azure.compute import AppServices
from diagrams.azure.database import DatabaseForPostgresqlServers, CosmosDb
from diagrams.custom import Custom

with Diagram("Azure Architecture", show=False):
    app_service = AppServices("App Service")
    postgresql = DatabaseForPostgresqlServers("PostgreSQL Flexible Server")
    cosmosdb = CosmosDb("CosmosDB")
    cc_openai = Custom("Azure OpenAI", "./openai/openai-logomark.png")

    app_service >> postgresql
    app_service >> cosmosdb
    app_service >> cc_openai

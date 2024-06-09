import os

from crewai import Agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tools import ServerManageTool

load_dotenv()


class ServerManageAgents:

    def server_manage_agent(self):
        return Agent(
            role="Server Management Expert",
            goal="Ensure the server is running and returning web pages",
            backstory="""
                You manage the server, ensuring it can respond to HTTP requests.
                If the server is down, you will check the Docker container status and restart it necessary.
            """,
            tools=[
                ServerManageTool.health_check,
                ServerManageTool.execute_docker_command
            ],
            verbose=True,
            llm=ChatOpenAI(
                model=os.getenv("OPENAI_MODEL_NAME")
            ),
        )
    

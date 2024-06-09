from agents import ServerManageAgents
from crewai import Crew, Process
from tasks import ServerManageTasks


class ServerManageCrew:
    def __init__(self, url, container_name) -> None:
        self.url = url
        self.container_name = container_name        

    def run(self):
        agents = ServerManageAgents()
        tasks = ServerManageTasks()

        # Initiate the agents
        server_manage_agent = agents.server_manage_agent()

        # Initiate the tasks
        check_server_task = tasks.check_server_task(
            agent=server_manage_agent,
            url=self.url
        )

        restart_server_task = tasks.check_container_status_task(
            url=self.url,
            agent=server_manage_agent,
            container_name=self.container_name
        )

        # Initiate Crew
        crew = Crew(
            agents=[
                server_manage_agent
            ],
            tasks=[
                check_server_task,
                restart_server_task
            ],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        return result

if __name__ == "__main__":
    crew = ServerManageCrew(
        url="http://localhost:8000",
        container_name="webserver"
    )

    result = crew.run()

    print("\n\n########################")
    print("## Here is the result ##")
    print("########################\n")
    print(result)

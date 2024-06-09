from textwrap import dedent

from crewai import Task


class ServerManageTasks:

    def check_server_task(self, agent, url):
        return Task(
            description=dedent(f"""
                Check if the server is responding to HTTP requests. 

                Server Web Page URL: {url} 
                """
            ),
            expected_output=dedent(f"""
                Server is up and running or needs to be restarted.
                """
            ),
            agent=agent
        )
    
    def check_container_status_task(self, agent, url, container_name):
        return Task(
            description=dedent(f"""
                Check the status of the Docker container where the server is running.

                Server Web Page URL: {url}
                Server Container Name: {container_name}
                """
            ),
            expected_output=dedent(f"""
                Server has been restarted.
                """
            ),
            agent=agent
        )

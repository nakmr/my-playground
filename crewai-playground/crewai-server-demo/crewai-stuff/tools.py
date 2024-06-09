import subprocess

import httpx
from langchain.tools import tool


class ServerManageTool:

    @tool("Check if a website is up")
    def health_check(url):
        """Useful to check if a website is up and running. The url have to be with port number."""
        try:
            response = httpx.get(url)
            return response.status_code == 200
        except httpx.HTTPStatusError:
            return False

    @tool("Execute a Docker command")
    def execute_docker_command(command):
        """Useful to execute a Docker command on the server"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')
        except subprocess.CalledProcessError as e:
            return "", str(e)


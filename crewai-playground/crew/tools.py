import json
import os
import httpx

from crewai import Agent, Task
from langchain.tools import tool
from unstructured.partition.html import partition_html

class SearchTool:

    @tool("Search the internet")
    def search_internet(query):
        """Useful to search the internet about a given topic and return relevant results"""

        top_result_to_return = 5
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': os.getenv("SERPER_API_KEY"),
            'content-type': 'application/json'
        }

        # Ensure headers are valid strings
        headers = {k: v for k, v in headers.items() if v is not None}

        try:
            response = httpx.post(url, headers=headers, data=payload)
            response.raise_for_status()  # Raise an error for bad status codes
        except httpx.HTTPStatusError as exc:
            return f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}"
        except Exception as exc:
            return f"An error occurred: {str(exc)}"

        response_data = response.json()
        if 'organic' not in response_data:
            return "Sorry, I couldn't find any relevant results for your query."
        else:
            results = response_data['organic']
            string = []
            for result in results[:top_result_to_return]:
                try:
                    string.append('\n'.join([
                        f"Title: {result['title']}",
                        f"Link: {result['link']}",
                        f"Snippet: {result['snippet']}",
                        "\n-----------------"
                    ]))
                except KeyError:
                    continue
            return '\n'.join(string)

class BrowserTool:

    @tool("Scrape website content")
    def scrape_and_summarize_website(website):
        """Useful to scrape and summarize a website content"""

        url = os.getenv("BROWSERLESS_URL")
        payload = json.dumps({"url": website})
        headers = {
            'cache-control': 'no-cache',
            'content-type': 'application/json'
        }
        response = httpx.post(url, headers=headers, data=payload)

        elements = partition_html(text=response.text)
        content = "\n\n".join([str(el) for el in elements])

        content = [content[i:i + 8000] for i in range(0, len(content), 8000)]
        summaries = []
        for chunk in content:
            chunking_agent = Agent(
                role='Principal Researcher',
                goal='Do amainzing researches and summarizes based on the content you are working with',
                backstory='You are a Principal Researcher at a big company and you need to do a research about a given topic',
                allow_delegation=False
            )
            chunking_task = Task(
                agent=chunking_agent,
                description=f"""Analyze and summarize the content bellow, make sure to include the most relevant information in the summary, return only the summary nothing else.
                \n\nCONTENT\n----------\n{chunk}"""
            )
            summary = chunking_task.execute()
            summaries.append(summary)
        return "\n\n".join(summaries)

class CalculatorTool:

    @tool("Make a calculation")
    def calculate(operation):
        """Useful to perform any mathematical calculations,
        like sum, minus, multiplication, division, etc.
        The input to this tool should be a mathematical expression,
        a couple of examples are `200*7` or `5000/2*10`
        """

        try:
            return eval(operation)
        except SyntaxError:
            return "Error: Invalid operation, please provide a valid mathematical expression."

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv("../.env")
    print(os.getenv("SERPER_API_KEY"))
    print(SearchTool.search_internet("How to make a pizza"))


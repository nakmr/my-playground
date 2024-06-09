from crewai import Agent
from tools import BrowserTool, CalculatorTool, SearchTool


class TripAgents:

    def city_selection_agent(self):
        return Agent(
            role="City Selection Expert",
            goal="Select the best city based on weather, season, and prices",
            backstory="An expert i analyzing travle data to pick ideal destinations",
            tools=[
                SearchTool.search_internet,
                BrowserTool.scrape_and_summarize_website,
            ],
            verbose=True,
        )

    def local_expert(self):
        return Agent(
            role="Local Expert at this city",
            goal="Provide the BEST insights about the selected city",
            backstory="A knowledgeable local guide with extensive information about the city, it's attractions and customs",
            tools=[
                SearchTool.search_internet,
                BrowserTool.scrape_and_summarize_website,
            ],
            verbose=True,
        )

    def travel_concierge(self):
        return Agent(
            role="Amazing Travel Concierge",
            goal="Create the most amazing travel itineraries with budget and packing suggestions for the city",
            backstory="Sepcialist in travle planning and logistics with decades of experience",
            tools=[
                SearchTool.search_internet,
                BrowserTool.scrape_and_summarize_website,
                CalculatorTool.calculate,
            ],
            verbose=True,
        )

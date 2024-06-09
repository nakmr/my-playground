from textwrap import dedent

from agents import TripAgents
from crewai import Crew, Process
from dotenv import load_dotenv
from tasks import TripTasks

load_dotenv("./.env")


class TripCrew:
    def __init__(self, origin, cities, date_range, interests):
        self.origin = origin
        self.cities = cities
        self.date_range = date_range
        self.interests = interests
    
    def run(self):
        agents = TripAgents()
        tasks = TripTasks()

        # Initiate the agents
        city_selector_agent = agents.city_selection_agent()
        local_expert_agent = agents.local_expert()
        travel_concierge_agent = agents.travel_concierge()

        # Initiate the tasks
        identify_task = tasks.identify_task(
            agent=city_selector_agent,
            origin=self.origin,
            cities=self.cities,
            interests=self.interests,
            range=self.date_range
        )

        gather_task = tasks.gather_task(
            agent=local_expert_agent,
            origin=self.origin,
            interests=self.interests,
            range=self.date_range
        )

        plan_task = tasks.plan_task(
            agent=travel_concierge_agent,
            origin=self.origin,
            interests=self.interests,
            range=self.date_range
        )

        # Initiate Crew
        crew = Crew(
            agents=[
                city_selector_agent,
                local_expert_agent,
                travel_concierge_agent
            ],
            tasks=[
                identify_task,
                gather_task,
                plan_task
            ],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        return result

if __name__ == '__main__':
    print("## Welcome to Trip Planner Crew ##")
    print("----------")
    location = input(
        dedent("""
            From where will you be traveling from?
        """)
    )
    cities = input(
        dedent("""
            What are the cities you are considering for your trip?
        """)
    )
    date_range = input(
        dedent("""
            What are the dates you are considering for your trip?
        """)
    )
    interests = input(
        dedent("""
            What are some of your high level interests and hobbies?
        """)
    )

    trip_crew = TripCrew(
        origin=location,
        cities=cities,
        date_range=date_range,
        interests=interests
    )
    result = trip_crew.run()

    print("\n\n########################")
    print("## Here is you Trip Plan")
    print("########################\n")
    print(result)

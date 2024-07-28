from config.settings import get_secret
import openai
from openai import OpenAI, api_key
import json

OPEN_AI_API_KEY = get_secret("OPEN_AI_API_KEY")

# Schedule must be empty for 7 hours from bedtime.
#         Do not schedule work periods during bedtime to work start time.
#         Can schedule rest periods during after 7 hours from bedtime to work start time.
#         Create a daily schedule with alternating frequent work and rest periods.
#         The sum of work hours in schedule should be equal to total_work_hours.
#         The sum of rest hours in schedule should be equal to total_rest_hours.
#         Do not exceed the total work hours or total rest hours.
#         You do not have to fill all the hours in a day.

class CreateTimeTable():
    def __init__(self):
        self.client = OpenAI(api_key=OPEN_AI_API_KEY)

    def create_time_table(self, bedtime, work_start_time, total_work_hours, total_rest_hours):
        prompt = f"""
        You are a time management expert. Based on the following inputs:
        Bedtime: {bedtime}
        Work start time: {work_start_time}
        Total work hours: {total_work_hours}
        Total rest hours: {total_rest_hours}
        
        Don't feel the period bedtime after 7hours.
        Create a daily schedule with alternating frequently work and rest periods.
        Sum of work hours must be equal to total_work_hours and must not over the total work hours.
        Sum of rest hours must be equal to total_rest_hours and must not over the total rest hours.
        Don't exceed the total work hours or total rest hours.
        Dont't fill work time and rest time at bedtime to work start time.
        You don't have to fill all the hours in a day.

        Provide the schedule in JSON format with the following structure:
        [
            {{
                "work_start_time": "HH:MM",
                "work_end_time": "HH:MM",
                "rest_start_time": "HH:MM",
                "rest_end_time": "HH:MM"
            }},
            ...
        ]
        """

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f" {bedtime} {work_start_time} {total_work_hours} {total_rest_hours}"},
            ],
            model = "gpt-3.5-turbo",
        )

        print(response.choices[0])
        return response.choices[0]


ctt = CreateTimeTable()
ctt.create_time_table("22:00", "08:00", 9, 6)

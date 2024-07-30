from config.settings import get_secret
import openai
from openai import OpenAI, api_key
import json

OPEN_AI_API_KEY = get_secret("OPEN_AI_API_KEY")

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
        
        Create a daily schedule with alternating work and rest periods. The total work hours must exactly match the "Total work hours," and the total rest hours must exactly match the "Total rest hours."

        Bedtime to 8 hours from Bedtime is reserved for sleeping. Do not schedule any activities during this time.
        Work and rest periods could alternate.
        Ensure that the sum of all work hours equals the Total work hours.
        Ensure that the sum of all rest hours equals the Total rest hours.
        Do not exceed the Total work hours or the Total rest hours.
        Do not schedule any activities from Bedtime until the start of the work period in the morning.
        Both start_time and end_time must be in HH:00 format.
        Do not response with start_time and end_time as null values.
        Do not take into account the general patterns of life in real life; base the schedule solely on the input data.

        Example Input:
        - Bedtime: 24:00
        - Total work hours: 8
        - Total rest hours: 8
        - Start time: 08:00

        Example Output:
        - 08:00-09:00 Work
        - 09:00-10:00 Rest
        - 10:00-11:00 Work
        - ...
        - 24:00-08:00 Sleeping

        Make a schedule that satisfies the input dataset.
        The result schedule is from 00:00 to 24:00.
        Example:
        - 05:00-13:00 Sleeping
        - 13:00-14:00 Work
        - ...
        - 24:00-02:00 Work
        - 02:00-05:00 est
        should be:
        - 00:00-02:00 Work
        - 02:00-05:00 Rest
        - 05:00-13:00 Sleeping
        - 13:00-14:00 Work
        ...
        22:00-24:00 Rest

        Provide the schedule in JSON format with the following structure:
        [
            {{
                "work_start_time": "HH:00",
                "work_end_time": "HH:00"
            }},
            {{
                "rest_start_time": "HH:00",
                "rest_end_time": "HH:00"
            }},
            {{
                "rest_start_time": "HH:00",
                "rest_end_time": "HH:00"
            }}
            ...
        ]
        """

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f" {bedtime} {work_start_time} {total_work_hours} {total_rest_hours}"},
            ],
            model = "gpt-4o",
        )

        print(response.choices[0])
        return response.choices[0]


ctt = CreateTimeTable()
ctt.create_time_table("08:00", "16:00", 6, 10)

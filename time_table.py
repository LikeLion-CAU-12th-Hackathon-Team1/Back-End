from config.settings import get_secret
import openai
from openai import OpenAI, api_key
import json

OPEN_AI_API_KEY = get_secret("OPEN_AI_API_KEY")

class CreateTimeTable():
    def __init__(self):
        self.client = OpenAI(api_key=OPEN_AI_API_KEY)

    def create_time_table(self, sleep_start_time, sleep_end_time, work_start_time, total_work_hours, total_rest_hours):
        prompt = f"""
        You are a time management expert. Based on the following inputs:
        Sleep start time: {sleep_start_time}
        Sleep end time: {sleep_end_time}
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
        Do not have to fill the whole time.
        The schedule can be empty between different periods.

        Make a schedule that satisfies the input dataset.
        The result schedule is from 000000 to 240000.
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
        - 22:00-23:59 Rest

        Example Input:
        - Sleep start time: 2400
        - Sleep end time: 0600
        - Start time: 0800
        - Total work hours: 8
        - Total rest hours: 8

        Output Format: JSON, sort = (1: Work, 2: Rest)
        Return a list of objects with the following
        Example Output:
        "schedule": 
        [
            {{ "sort": 1, "start_time": 80000, "end_time": 110000 }},
            {{ "sort": 2, "start_time": 110000, "end_time": 140000 }},
            {{ "sort": 1, "start_time": 140000, "end_time": 17000 }},
            ...
            {{ "sort": 2, "start_time": 230000, "end_time": 235959 }}
        ]
        """

        response = self.client.chat.completions.create(
            model = "gpt-4o",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f" {sleep_start_time} {sleep_end_time} {work_start_time} {total_work_hours} {total_rest_hours}"},
            ],
        )

        response_msg = response.choices[0].message.content
        data = json.loads(response_msg)
        schedule_list = data['schedule']
        return schedule_list

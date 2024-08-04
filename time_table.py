from config.settings import get_secret
import openai
from openai import OpenAI, api_key
import json

OPEN_AI_API_KEY = get_secret("OPEN_AI_API_KEY")

class CreateTimeTable():
    def __init__(self):
        self.client = OpenAI(api_key=OPEN_AI_API_KEY)

    def create_time_table(self, sleep_start_time, sleep_end_time, work_style, work_rest_balance):
        prompt = f"""
        You are a time management expert. Based on the following inputs:
        Sleep start time: {sleep_start_time}
        Sleep start at 2400 means that the service user goes to bed at 00:00.
        Sleep end time: {sleep_end_time}
        Sleep end at 0600 means that the service user wakes up at 06:00.
        From sleep start time to sleep end time is sleeping time. So you must not fill the time during sleep.
        Work start time: {work_style}
        If work start time is 1, you should start work at 080000.
        If work start time is 2, you should start work at 130000.
        If work start time is 3, you should start work at 160000.
        Work/rest balance: {work_rest_balance}
        If work/rest balance is 1, total work time should be 8 hours and total rest time should be 6 hours.
        If work/rest balance is 2, total work time should be 7 hours and total rest time should be 7 hours.
        If work/rest balance is 3, total work time should be 6 hours and total rest time should be 8 hours.
        Both total work time and rest time must be exactly same with the input data.
        The schedule of the timetable is always set on time.
        The schedule of the timetable do not have to fill the whole day.

        Sleeping time is from Sleep start time to Sleep end time. Do not schedule any activities during this time.
        User will sleep during Sleeping time. So sleeping time must be empty. There will be no work or rest during this time.
        Both sum of work time and rest time must be sams as the total work time and total rest time.
        Create a daily schedule with alternating work and rest periods.
        Work and rest periods could alternate.
        
        The sum of working and resting times should be exactly the same as the total work time and total rest time.
        Do not schedule any work periods from sleep end time until the start of the work period.
        Both start_time and end_time must be in HH0000 format.
        Do not response with start_time and end_time as null values.
        Do not take into account the general patterns of life in real life; base the schedule solely on the input data.
        Start time's minutes and seconds are always 00.
        End time's minutes and seconds are always 00.

        Make a schedule that satisfies the input dataset.
        The result schedule is from 000000 to 240000.
        Example:
        - 05:00:00-13:00:00 Sleeping
        - 13:00:00-14:00:00 Work
        - ...
        - 24:00:00-02:00:00 Work
        - 02:00:00-05:00:00 est
        should be:
        - 00:00:00-02:00:00 Work
        - 02:00:00-05:00:00 Rest
        - 05:00:00-13:00:00 Sleeping
        - 13:00:00-14:00:00 Work
        ...
        - 22:00:00-24:00:00 Rest

        Example Input:
        - Sleep start time: 2400
        - Sleep end time: 0600
        - Start time: 0800
        - Total work hours: 8
        - Total rest hours: 8

        Output Format: JSON, sort = (1: Work, 2: Rest)
        Return a list of objects with the following.
        Output response time must be "HH0000" format.
        Example Output:
        "schedule": 
        [
            {{ "sort": 1, "start_time": "080000", "end_time": "110000" }},
            {{ "sort": 2, "start_time": "110000", "end_time": "140000" }},
            {{ "sort": 1, "start_time": "140000", "end_time": "170000" }},
            ...
            {{ "sort": 2, "start_time": "230000", "end_time": "240000" }}
        ]
        """

        response = self.client.chat.completions.create(
            model = "gpt-4o",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f" {sleep_start_time} {sleep_end_time} {work_style} {work_rest_balance}"},
            ],
        )

        response_msg = response.choices[0].message.content
        data = json.loads(response_msg)
        schedule_list = data['schedule']
        # print(schedule_list)
        return schedule_list

# ctt = CreateTimeTable()
# ctt.create_time_table('040000', '110000', 2, 1)

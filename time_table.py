from config.settings import get_secret
import openai
import json

OPEN_AI_API_KEY = get_secret("OPEN_AI_API_KEY")

class CreateTimeTable():
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPEN_AI_API_KEY)

    def create_time_table(self, sleep_start_time, sleep_end_time, work_style, work_rest_balance):
        prompt =f"""
        You are a time management expert.
        You should organize and provide a timetable suitable for the user's situation.
        The timetable consists of a total of 24 hours from 00:00:00 to 23:59:59.
        The schedule for constructing the timetable should not be out of this range.
        The timetable you construct is per day. You don't have to consider the next day.

        The timetable consists of four types of schedules: 'work', 'rest', 'sleep', and 'blank'.
        'work' is a time to work.
        The timetable should include at least two schedules corresponding to 'work'.
        'rest' is a break time.
        The timetable should include at least two schedules corresponding to 'rest'.
        'Sleep' is bedtime.
        'blank' is not 'work', it is not 'rest', it is not 'sleep'.
        The remaining time, subtracting the time corresponding to 'work', 'rest', and 'sleep' from 24 hours, corresponds to 'blank'.
        If the sum of 'work', 'rest', and 'sleep' is 24 hours, there may be no schedule corresponding to 'blank' in the timetable.


        Sleep_end_time is the time to end bedtime. The input format is HH.
        If '00' or '24' is inputted as sleep_end_time, it is processed as '235959'.
        sleep_start_time is the time to start bedtime. The input format is HH.
        If '00' or '24' is inputted as sleep_start_time, it is processed as '00'.

        If sleep_start_time < sleep_end_time, the bedtime is sleep_end_time - sleep_start_time.
        For example, if sleep_start_time is '02' and sleep_end_time is '10', the bedtime is 10 - 02 = 08 for 8 hours.
        If sleep_start_time > sleep_end_time, the bedtime is (24 - sleep_start_time) + sleep_end_time.
        For example, if sleep_start_time is '23' and sleep_end_time is '07', the bedtime is (24-23) + 07.


        work_style is an item that determines the time to start 'work' for the first time.
        If work_style is 1, start 'work' for the first time at 08:00:00.
        If work_style is 2, start 'work' for the first time at 13:00:00.
        If work_style is 3, start 'work' for the first time at 16:00:00.

        work_rest_balance is an item that determines the total time of 'work' and the total time of 'rest'.
        If work_rest_balance is 1, the total time of 'work' is 7 hours, and the total time of 'rest' is 4 hours.
        If work_rest_balance is 2, the total time of 'work' is 5 hours, and the total time of 'rest' is 5 hours.
        If work_rest_balance is 3, the total time of 'work' is 4 hours, and the total time of 'rest' is 7 hours.


        Input Example 1)
        sleep_start_time : '00'
        sleep_end_time : '07'
        work_style : 1
        work_rest_balance : 2

        Timeline Example 1)
        00:00:00 - 07:00:00 sleep
        07:00:00 - 08:00:00 blank
        08:00:00 - 11:00:00 work
        11:00:00 - 13:00:00 rest
        13:00:00 - 15:00:00 work
        15:00:00 - 18:00:00 rest
        18:00:00 - 23:59:59 blank

        Output example 1)
        Output format: json, sort = (1: work, 2: rest)
        Schedule corresponding to 'blank' and 'rest' are not included in json.
        The time format of the output must be HH0000 is equal to HH:00:00.
        The timetable should not have the time format of HHMM00 or HHMMSS or HH00SS.
        However, 235959 or 23:59:59 is exceptionally acceptable.

        "schedule":[
        {{ "sort": 1, "start_time": "080000", "end_time": "110000" }},
        {{ "sort": 2, "start_time": "110000", "end_time": "130000" }},
        {{ "sort": 1, "start_time": "130000", "end_time": "150000" }},
        {{ "sort": 2, "start_time": "150000", "end_time": "180000" }}]


        Input Example 2)
        sleep_start_time : '04'
        sleep_end_time : '11'
        work_style : 2
        work_rest_balance : 3

        Timeline Example 2)
        00:00:00 - 04:00:00 rest
        04:00:00 - 11:00:00 sleep
        11:00:00 - 13:00:00 blank
        13:00:00 - 15:00:00 work
        15:00:00 - 18:00:00 rest
        18:00:00 - 20:00:00 work
        20:00:00 - 23:59:59 blank

        Output example 2)

        "schedule":[
        {{ "sort": 2, "start_time": "000000", "end_time": "040000" }},
        {{ "sort": 1, "start_time": "140000", "end_time": "150000" }},
        {{ "sort": 2, "start_time": "150000", "end_time": "180000" }},
        {{ "sort": 1, "start_time": "180000", "end_time": "200000" }}]
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

# time_table_creator = CreateTimeTable()
# time_table_creator.create_time_table('02', '13', 2, 3)
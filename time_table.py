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
Configure a timetable that meets the conditions of sleep_start_time, sleep_end_time, work_style, and work_rest_balance provided and output the correct results.
The timetable consists of a total of 24 hours from 00:00:00 to 23:59:59.
Time on the timetable must not be out of this range.
The timetable that you construct is on a daily basis. The next day is not considered.
The timetable do not have to fill the whole day. Empty time periods are acceptable.

The timetable consists of four types of schedules: 'work', 'rest', 'sleep', and 'blank'.
'work' is a time to work.
The timetable should include at least two schedules corresponding to 'work'.
'rest' is a break time.
The timetable should include at least two schedules corresponding to 'rest'.
'sleep' is bedtime.
'blank' is not 'work', it is not 'rest', it is not 'sleep'.
The remaining time, subtracting the time corresponding to 'work', 'rest', and 'sleep' from 24 hours, corresponds to 'blank'.
If the sum of 'work', 'rest', and 'sleep' is 24 hours, there is no schedule that corresponds to 'blank' in the timetable.


The input formats of sleep_end_time and sleep_start_time are HH00 or HHMM.
HH00 and HHMM are numbers.

0 means 00:00:00.
100 means 01:00:00.
1300 means 13:00:00.
0 and 100 and 1300 are HH00.

240 means 02:40:00.
1530 means 15:30:00.
240 and 1530 are HHMM.


sleep_end_time is the time to end bedtime.
If 0 or 2400 is inputted as sleep_end_time, it is processed as 23:59:59.
If the HHMM format is input to sleep_end_time, it is considered as (HH+1)00.
For example, if 240 is input to sleep_end_time, it is considered 300 and processed as 03:00:00.

sleep_start_time is the time to start bedtime.
If 0 or 2400 is inputted as sleep_start_time, it is processed as 00:00:00.
If the HHMM format is input to sleep_start_time, it is considered HH00.
For example, if 1530 is entered in sleep_start_time, it is considered 1500 and processed as 15:00:00.

If sleep_start_time < sleep_end_time, the bedtime is sleep_end_time - sleep_start_time.
For example, if sleep_start_time is 200 and sleep_end_time is 1000, the bedtime is 1000 - 200 = 800, which is 8 hours.
If sleep_start_time > sleep_end_time, the bedtime is (2400 - sleep_start_time) + sleep_end_time.
For example, if sleep_start_time is 2300 and sleep_end_time is 700, the bedtime is (2400 - 2300) + 700, which is 8 hours.

work_style determines the time to start 'work' for the first time since sleep_end_time.
If work_style is 1, start 'work' for the first time since sleep_end_time at 08:00:00.
If work_style is 2, start 'work' for the first time since sleep_end_time at 11:00:00.
If work_style is 3, start 'work' for the first time since sleep_end_time at 14:00:00.

work_rest_balance is an item that determines the total time of 'work' and the total time of 'rest'.
If work_rest_balance is 1, the total time of 'work' is 8 hours, and the total time of 'rest' is 6 hours.
If work_rest_balance is 2, the total time of 'work' is 6 hours, and the total time of 'rest' is 6 hours.
If work_rest_balance is 3, the total time of 'work' is 6 hours, and the total time of 'rest' is 8 hours.


Input Example 1)
sleep_start_time : 0
sleep_end_time : 700
work_style : 1
work_rest_balance : 2

Timeline Example 1)
00:00:00 - 07:00:00 'sleep'
07:00:00 - 08:00:00 'blank'
08:00:00 - 11:00:00 'work'
11:00:00 - 14:00:00 'rest'
14:00:00 - 17:00:00 'work'
17:00:00 - 20:00:00 'rest'
20:00:00 - 23:59:59 'blank'

Output example 1)
Output format: json, sort = (1: work, 2: rest)
Schedule corresponding to 'blank' and 'sleep' are not included in json.
The time format of the output must be 'HH0000'. 'HHH0000' is the same as HH:00:00.
The timetable should not have a time format of 'HHMM00' or 'HHMMSS' or 'HH00SS'.
However, 23:59:59 should be expressed as "235959". Exceptionally acceptable.

"schedule":[
{{ "sort": 1, "start_time": "080000", "end_time": "110000" }},
{{ "sort": 2, "start_time": "110000", "end_time": "140000" }},
{{ "sort": 1, "start_time": "140000", "end_time": "170000" }},
{{ "sort": 2, "start_time": "170000", "end_time": "200000" }}]


Input Example 2)
sleep_start_time : 400
sleep_end_time : 1100
work_style : 2
work_rest_balance : 3

Timeline Example 2)
00:00:00 - 02:00:00 'rest'
02:00:00 - 04:00:00 'blank'
04:00:00 - 11:00:00 'sleep'
11:00:00 - 13:00:00 'work'
13:00:00 - 19:00:00 'rest'
19:00:00 - 23:00:00 'work'
23:00:00 - 23:59:59 'blank'

The total time of 'work' must follow the time specified according to the value of work_rest_balance.
Since work_rest_balnce is 3, the total time of 'work' is 6 hours.
The total time of 'rest' must follow the time specified according to the value of work_rest_balance.
Since work_rest_balance is 3, the total time of 'rest' is 8 hours.

Output example 2)
"schedule":[
{{ "sort": 2, "start_time": "000000", "end_time": "020000" }},
{{ "sort": 1, "start_time": "110000", "end_time": "130000" }},
{{ "sort": 2, "start_time": "130000", "end_time": "190000" }},
{{ "sort": 1, "start_time": "190000", "end_time": "230000" }},
]


Input Example 3)
sleep_start_time : 300
sleep_end_time : 1000
work_style : 1
work_rest_balance : 3

Timeline Example 3)
00:00:00 - 03:00:00 'rest'
03:00:00 - 10:00:00 'sleep'
10:00:00 - 12:00:00 'work'
12:00:00 - 16:00:00 'rest'
16:00:00 - 19:00:00 'blank'
19:00:00 - 23:00:00 'work'
23:00:00 - 23:59:59 'rest'

Since work_style is 1, the time to start 'work' for the first time since sleep_end_time should be 08:00:00.
However, since sleep_end_time is later than 08:00:00, sleep_end_time was designated as the time to start 'work' for the first time.

Output example 3)
"schedule":[
{{ "sort": 2, "start_time": "000000", "end_time": "030000" }},
{{ "sort": 1, "start_time": "100000", "end_time": "120000" }},
{{ "sort": 2, "start_time": "120000", "end_time": "160000" }},
{{ "sort": 1, "start_time": "190000", "end_time": "230000" }},
{{ "sort": 2, "start_time": "230000", "end_time": "235959" }}]


Input Example 4)
sleep_start_time : 600
sleep_end_time : 1300
work_style : 3
work_rest_balance : 1

Timeline Example 4)
00:00:00 - 01:00:00 'rest'
01:00:00 - 04:00:00 'work'
04:00:00 - 06:00:00 'blank'
06:00:00 - 13:00:00 'sleep'
13:00:00 - 14:00:00 'blank'
14:00:00 - 16:00:00 'work'
16:00:00 - 20:00:00 'rest'
20:00:00 - 23:00:00 'work'
23:00:00 - 23:59:59 'rest'

Output example 4)
"schedule":[
{{ "sort": 2, "start_time": "000000", "end_time": "010000" }},
{{ "sort": 1, "start_time": "010000", "end_time": "040000" }},
{{ "sort": 1, "start_time": "140000", "end_time": "160000" }},
{{ "sort": 2, "start_time": "160000", "end_time": "200000" }},
{{ "sort": 1, "start_time": "200000", "end_time": "230000" }},
{{ "sort": 2, "start_time": "230000", "end_time": "235959" }}]

work_style specifies the first 'work' time since sleep_end_time.
'work' can exist before sleep_start_time.
However, the first time the 'work' starts after sleep_end_time must be observed.


Keyword 'schedule' must be included in your response.
If there is no 'schedule' keyword it might be a cause of error.
So if there is no 'schedule' keyword, you must put 'schedule' keyword in your response.
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
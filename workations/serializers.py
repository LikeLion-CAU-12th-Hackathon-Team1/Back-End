from rest_framework import serializers
from .models import *

# 워케이션 등록
class WorkationSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workation_space
        fields = '__all__' # ('space_type',)

class WorkationRestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workation_rest
        fields = '__all__' # ('rest_type',)

class WorkationSerializer(serializers.ModelSerializer):
    space = WorkationSpaceSerializer(many=True)
    rest = WorkationRestSerializer(many=True)

    class Meta:
        model = Workation
        fields = ('workation_id', 'id', 'sigg_id', 'start_date', 'end_date', 'work', 'balance', 'space', 'rest', 'start_sleep', 'end_sleep')


# 워케이션 오늘 일정
## 시간표
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('description', 'complete',)

class TimeTaskSerializer(serializers.ModelSerializer):
    task = TaskSerializer()

    class Meta:
        model = Time_task
        fields = ('time_workation_id', 'task_id', 'task',)

class TimeWorkationSerializer(serializers.ModelSerializer):
    timetask = TimeTaskSerializer()

    class Meta:
        model = Time_workation
        fields = ('start_time', 'end_time', 'sort' ,'timetask',)

class DailyWorkationSerializer(serializers.ModelSerializer):
    timeworkation = TimeWorkationSerializer()

    class Meta:
        model = Daily_workation
        fields = ('workation_id', 'daily_workation_id', 'date', 'timeworkation', 'memo',) # '__all__' # ('Workation_id', 'date', 'timetask', 'task', 'memo')


# 워케이션 전체 일정
## 전체 정보
# class WorkationRegisterDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Workation
#         fields = ('workation_id', 'start_date', 'end_date', )

## 개별 정보
# class DailyWorkationDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Daily_workation
#         fields = ('daily_workation_id', 'date', 'memo',)

# ## 개별 시간표
# class TimeWorkationDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Time_workation
#         fields = ('sort', 'start_time', 'end_time',)

# ## 개별 투두
# class TaskDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Task
#         fields = ('description', 'complete',)

# class WorkationScheduleSerializer(serializers.ModelSerializer):
#     daily = DailyWorkationDataSerializer()
#     time = TimeWorkationDataSerializer()
#     task = TaskDataSerializer()

#     class Meta:
#         model = Workation
#         fields = ('start_date', 'end_date', 'daily_workation_id', 'start_time', 'end_time', 'date', 'memo', 'description', 'sort',)
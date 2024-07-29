from rest_framework import serializers
from .models import *

class WorkationSpaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workation_space_type
        read_only_fields = ('space_id',)
        fields = ('space_type',)
    
class WorkationRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workation_rest_type
        read_only_fields = ('rest_id',)
        fields = ('rest_type',)

## 등록
class WorkationSerializer(serializers.ModelSerializer):
    space = WorkationSpaceSerializer(many=True)
    rest = WorkationRestSerializer(many=True)

    class Meta:
        model = Workation
        read_only_fields = ('workation_id', 'space_id', 'rest_id',)
        fields = ('id', 'sigg_id', 'start_date', 'end_date', 'work', 'balance', 'space', 'rest', 'start_sleep', 'end_sleep',)


# 워케이션 오늘 일정
## 시간표
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('description', 'complete',)

class TimeTaskSerializer(serializers.ModelSerializer):
    task = TaskSerializer(many=True)

    class Meta:
        model = Time_task
        read_only_fields = ('time_workation_id', 'task_id')
        fields = ('task',)

class TimeWorkationSerializer(serializers.ModelSerializer):
    timetask = TimeTaskSerializer() # many=True

    class Meta:
        model = Time_workation
        fields = ('start_time', 'end_time', 'sort' ,'timetask',)

class DailyWorkationSerializer(serializers.ModelSerializer):
    timeworkation = TimeWorkationSerializer() # many=True

    class Meta:
        model = Daily_workation
        read_only_fields = ('workation_id', 'daily_workation_id', 'date', )
        fields = ('timeworkation', 'memo',) # '__all__' # ('Workation_id', 'date', 'timetask', 'task', 'memo')


# 워케이션 전체 일정
class WorkationScheduleSerializer(serializers.ModelSerializer):
    daily = DailyWorkationSerializer() # many=True

    class Meta:
        model = Workation
        read_only_fields = ('id', 'sigg_id', 'start_date', 'end_date', 'work', 'space', )
        exclude = ('start_sleep', 'end_sleep', )
        # fields = '__all__'
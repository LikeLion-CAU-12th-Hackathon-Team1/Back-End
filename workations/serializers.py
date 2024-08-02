from rest_framework import serializers
from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.fields import ReadOnlyField, JSONField
from .models import *
from time_table import CreateTimeTable
# from config.permissions import IsAuthenticatedAndReturnUser
# from rest_framework.response import Response
import datetime

# workation-space 중간 테이블.
class WorkationSpaceSerializer(serializers.ModelSerializer):
    space = PrimaryKeyRelatedField(queryset=Space.objects.all())
    workation = ReadOnlyField(source='workation_id')

    class Meta:
        model = Workation_space
        fields = '__all__'
        depth = 1
    
# workation-rest 중간 테이블.
class WorkationRestSerializer(serializers.ModelSerializer):
    rest = PrimaryKeyRelatedField(queryset=Rest.objects.all())
    workation = ReadOnlyField(source='workation_id')

    class Meta:
        model = Workation_rest
        fields = '__all__'
        depth = 1

# 전체 workation.
class WorkationSerializer(serializers.ModelSerializer):
    sigg = PrimaryKeyRelatedField(queryset=Sigg.objects.all())
    workation2space = WorkationSpaceSerializer(many=True, required=False)
    workation2rest = WorkationRestSerializer(many=True, required=False)
    start_date = serializers.DateField(format='%Y%m%d', input_formats=['%Y%m%d'])
    end_date = serializers.DateField(format='%Y%m%d', input_formats=['%Y%m%d'])

    class Meta:
        model = Workation
        fields = '__all__'

    def create(self, validated_data):
        spaces_data = validated_data.pop('workation2space', [])
        rest_data = validated_data.pop('workation2rest', [])

        workation = Workation.objects.create(**validated_data)

        for space_data in spaces_data:
            Workation_space.objects.create(workation=workation, **space_data)

        for rest_data in rest_data:
            Workation_rest.objects.create(workation=workation, **rest_data)

        time_table_creator = CreateTimeTable()
        base_time_table = time_table_creator.create_time_table(
            validated_data['start_sleep'], 
            validated_data['end_sleep'],
            validated_data['work_style'],
            validated_data['work_purpose']
            )

        current_date = validated_data['start_date']
        end_date = validated_data['end_date']
        while current_date <= end_date:
            serializer = DailyWorkationSerializer(
                data = {
                    'workation': workation.workation_id,
                    'date': current_date,
                    'base_time_table': base_time_table
                    }
                )
            if serializer.is_valid():
                serializer.save()
            current_date += datetime.timedelta(days=1)

        return workation
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # 날짜 필드를 8자리 숫자 문자열로 변환
        ret['start_date'] = instance.start_date.strftime('%Y%m%d')
        ret['end_date'] = instance.end_date.strftime('%Y%m%d')
        return ret
    
    def validate_start_date(self, value):
        if datetime.date.today() > value:
            raise serializers.ValidationError("Start date must be later than today.")
        return value
    
    def validate_end_date(self, value):
        if self.initial_data['start_date'] > self.initial_data['end_date']:
            raise serializers.ValidationError("End date must be later than start date.")
        return value
    
    def validate(self, validated_data):
        user = self.initial_data['user']
        workations = Workation.objects.filter(user=user)
        for workation in workations:
            if workation.start_date <= validated_data['start_date'] < workation.end_date:
                raise serializers.ValidationError("Start date overlaps with existing workation.")
            if workation.start_date < validated_data['end_date'] <= workation.end_date:
                raise serializers.ValidationError("End date overlaps with existing workation.")
            if validated_data['start_date'] <= workation.start_date and validated_data['end_date'] >= workation.end_date:
                raise serializers.ValidationError("Date overlaps with existing workation.")
        return validated_data
    
# 1일 단위 워케이션.
class DailyWorkationSerializer(serializers.ModelSerializer):
    workation = PrimaryKeyRelatedField(queryset=Workation.objects.all())
    base_time_table = JSONField(required=False)
    memo = serializers.CharField(required=False)

    class Meta:
        model = Daily_workation
        fields = '__all__'

    def create(self, validated_data):
        base_time_table = validated_data.pop('base_time_table', None)
        # workation = validated_data.pop('workation')
        # daily_workation = Daily_workation.objects.create(workation=workation, **validated_data)
        daily_workation = super().create(validated_data)
        if base_time_table is not None:
            for time_data in base_time_table:
                time_data['daily_workation'] = daily_workation.daily_workation_id
                # time_data['start_time'] = int(time_data['start_time'])
                # time_data['end_time'] = int(time_data['end_time'])

                hours = int(time_data['start_time'][:2])
                minutes = int(time_data['start_time'][2:4])
                seconds = int(time_data['start_time'][4:])
                time_data['start_time'] = datetime.time(hours, minutes, seconds)
                if time_data['end_time'] == '240000':
                    time_data['end_time'] = datetime.time(23, 59, 59)
                else:
                    hours = int(time_data['end_time'][:2])
                    minutes = int(time_data['end_time'][2:4])
                    seconds = int(time_data['end_time'][4:6])
                    time_data['end_time'] = datetime.time(hours, minutes, seconds)

                serializer = TimeWorkationSerializer(data = time_data)
            if serializer.is_valid():
                serializer.save()
            else:
                raise serializers.ValidationError("Invalid time data.")

        return daily_workation
    
    def update(self, instance, validated_data):
        memo = validated_data.pop('memo', None)
        instance.memo = memo
        instance.save()
        return instance

# 할 일.
class TaskSerializer(serializers.ModelSerializer):
    daily_workation = PrimaryKeyRelatedField(queryset=Daily_workation.objects.all(), required=False)
    time_workation = PrimaryKeyRelatedField(queryset=Time_workation.objects.all(), required=False)
    description = serializers.CharField(required=False)
    complete = serializers.BooleanField(required=False)

    class Meta:
        model = Task
        fields = '__all__'

    def create(self, validated_data):
        time_workation = validated_data.pop('time_workation')
        validated_data['daily_workation'] = time_workation.daily_workation
        task = super().create(validated_data)
        time_task_data = {
            'task': task.task_id,
            'time_workation': time_workation.time_workation_id
        }
        serializer = TimeTaskSerializer(data=time_task_data)
        if serializer.is_valid():
            serializer.save()
        return task
    
    def to_representation(self, instance):
        if instance.complete == 2:
            instance.complete = False
        return super().to_representation(instance)

# 시간 단위 워케이션-할 일 중간 테이블.
class TimeTaskSerializer(serializers.ModelSerializer):
    task = PrimaryKeyRelatedField(queryset=Task.objects.all())
    time_workation = PrimaryKeyRelatedField(queryset=Time_workation.objects.all())

    class Meta:
        model = Time_task
        fields = '__all__'
        depth = 1

    # 같은 daily_workation에 속한 객체만 연결 가능.
    def validate(self, validated_data):
        task = validated_data.get('task')
        time_workation = validated_data.get('time_workation')

        if task.daily_workation != time_workation.daily_workation:
            raise serializers.ValidationError("Task and Time_workation must be related to the same Daily_workation.")
        
        return validated_data

# 시간 단위 워케이션.
class TimeWorkationSerializer(serializers.ModelSerializer):
    daily_workation = PrimaryKeyRelatedField(queryset=Daily_workation.objects.all())
    sort = serializers.IntegerField(required=True)
    start_time = serializers.TimeField(format='%H%M%S', input_formats=['%H%M%S'], required=True)
    end_time = serializers.TimeField(format='%H%M%S', input_formats=['%H%M%S'], required=True)

    class Meta:
        model = Time_workation
        fields = '__all__'

    def get_queryset(self):
        queryset = Time_workation.objects.all()
        daily_workation_id = self.request.get('daily_workation_id', None)
        if daily_workation_id is not None:
            queryset = queryset.filter(daily_workation_id=daily_workation_id)
        return queryset
    
    def create(self, validated_data):
        if type(validated_data['start_time']) != datetime.time:
            start_time = validated_data['start_data']
            hours = int(start_time[:2])
            minutes = int(start_time[2:4])
            seconds = int(start_time[4:6])
            validated_data['start_time'] = datetime.time(hours, minutes, seconds)
            end_time = validated_data['end_time']
            if end_time == "240000":
                validated_data['end_time'] = datetime.time(23, 59, 59)
            else:
                hours = int(end_time[:2])
                minutes = int(end_time[2:4])
                seconds = int(end_time[4:6])
                validated_data['end_time'] = datetime.time(hours, minutes, seconds)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('daily_workation', None)
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['start_time'] = instance.start_time.strftime('%H%M%S')
        representation['end_time'] = instance.end_time.strftime('%H%M%S')
        return representation
    
    def validate(self, validated_data):
        daily_workation = validated_data.get('daily_workation', None)
        start_time = validated_data.get('start_time', None)
        end_time = validated_data.get('end_time', None)

        if daily_workation is not None:
            times = Time_workation.objects.filter(daily_workation=daily_workation)
            for time in times:
                if start_time and time.start_time <= start_time < time.end_time:
                    raise serializers.ValidationError("Start time overlaps with existing time.")
                
                if end_time and time.start_time < end_time <= time.end_time:
                    raise serializers.ValidationError("End time overlaps with existing time.")
                
                if start_time and end_time and validated_data['start_time'] <= time.start_time and validated_data['end_time'] >= time.end_time:
                    raise serializers.ValidationError("Time overlaps with existing time.")
                
        return validated_data

class TodayWorkationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Daily_workation
        fields = '__all__'

class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = '__all__'

class RestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rest
        fields = '__all__'

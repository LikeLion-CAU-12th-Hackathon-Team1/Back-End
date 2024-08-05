from rest_framework import serializers
from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.fields import ReadOnlyField, JSONField
from .models import *
from time_table import CreateTimeTable
import datetime
from django.db.models import Q

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
        space_datas = validated_data.pop('workation2space', [])
        if len(space_datas) == 0:
            raise serializers.ValidationError('space type required')
        rest_datas = validated_data.pop('workation2rest', [])
        if len(rest_datas) == 0:
            raise serializers.ValidationError('rest type required')

        workation = Workation.objects.create(**validated_data)

        # 생성한 워케이션과 입력 받은 선호 작업 공간, 휴식 스타일 매핑
        for space_data in space_datas:
            Workation_space.objects.create(workation=workation, **space_data)

        for rest_data in rest_datas:
            Workation_rest.objects.create(workation=workation, **rest_data)

        # 챗 GPT로 기본 시간표 틀 생성
        time_table_creator = CreateTimeTable()
        base_time_table = time_table_creator.create_time_table(
            validated_data['start_sleep'], validated_data['end_sleep'],
            validated_data['work_style'], validated_data['work_purpose'])

        # 워케이션 일정대로 날짜 별 일일 워케이션 객체 생성
        current_date = validated_data['start_date']
        end_date = validated_data['end_date']
        while current_date <= end_date:
            serializer = DailyWorkationSerializer(
                data = {
                    'workation': workation.workation_id,
                    'date': current_date,
                    'base_time_table': base_time_table
                    })
            if serializer.is_valid():
                serializer.save()
            current_date += datetime.timedelta(days=1)

        return workation
    
    # DateField로 저장하지만 프론트에 데이터를 전달할 때는 8자리 숫자 문자열로 전달
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['start_date'] = instance.start_date.strftime('%Y%m%d')
        ret['end_date'] = instance.end_date.strftime('%Y%m%d')
        return ret
    
    def validate_start_date(self, value):
        user = self.initial_data['user']
        workations = Workation.objects.filter(user=user)

        if datetime.date.today() > value:
            raise serializers.ValidationError("Start date must be later than today.")
        if workations.filter(Q(start_date__lte=value) & Q(end_date__gte=value)).exists():
            raise serializers.ValidationError("Start date overlaps with existing workation.")
        return value
    
    def validate_end_date(self, value):
        user = self.initial_data['user']
        workations = Workation.objects.filter(user=user)

        if self.initial_data['start_date'] > self.initial_data['end_date']:
            raise serializers.ValidationError("End date must be later than start date.")
        if workations.filter(Q(start_date__lte=value) & Q(end_date__gte=value)).exists():
            raise serializers.ValidationError("Start date overlaps with existing workation.")
        return value
    
    def validate(self, validated_data):
        user = self.initial_data['user']
        workations = Workation.objects.filter(user=user)
        
        if workations.filter(Q(start_date__gte=validated_data['start_date']) & Q(end_date__lte=validated_data['end_date'])).exists():
            raise serializers.ValidationError("Start date overlaps with existing workation.")
        if workations.filter(Q(end_date__gte=datetime.date.today())).exists():
            raise serializers.ValidationError("There is workation uncompleted.")
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
        # 시간 테이블을 입력 데이터로 받은 경우
        # 시간 테이블을 생성
        # bulk_create로 리팩토링 해야 함
        base_time_table = validated_data.pop('base_time_table', None)
        daily_workation = super().create(validated_data)
        if base_time_table:
            for time_data in base_time_table:
                time_data['daily_workation'] = daily_workation.daily_workation_id
                if time_data['end_time'] == '240000':
                    time_data['end_time'] = '235959'

                serializer = TimeWorkationSerializer(data=time_data)
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

        # time-task 중간 테이블 연결
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
    daily_workation = PrimaryKeyRelatedField(queryset=Daily_workation.objects.all(), required=False)
    sort = serializers.IntegerField()
    start_time = serializers.TimeField(format='%H%M%S', input_formats=['%H%M%S'])
    end_time = serializers.TimeField(format='%H%M%S', input_formats=['%H%M%S'])

    class Meta:
        model = Time_workation
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['start_time'] = instance.start_time.strftime('%H%M%S')
        representation['end_time'] = instance.end_time.strftime('%H%M%S')
        return representation
    
    def validate_start_time(self, value):
        daily_workation = self.initial_data.get('daily_workation') if not self.instance else self.instance.daily_workation
        if daily_workation:
            time_workations = Time_workation.objects.filter(daily_workation=daily_workation)
        else:
            time_workations = Time_workation.objects.filter(daily_workation=self.instance.daily_workation.daily_workation_id)

        if self.instance:
            time_workations = time_workations.exclude(pk=self.instance.daily_workation_id)
        
        if time_workations.filter(Q(start_time__lte=value) & Q(end_time__gt=value)).exists():
            raise serializers.ValidationError('Start time overlaps with existing time.')
        return value
        
    def validate_end_time(self, value):
        daily_workation = self.initial_data.get('daily_workation') if not self.instance else self.instance.daily_workation
        if daily_workation:
            time_workations = Time_workation.objects.filter(daily_workation=daily_workation)
        else:
            time_workations = Time_workation.objects.filter(daily_workation=self.instance.daily_workation.daily_workation_id)

        if self.instance:
            time_workations = time_workations.exclude(pk=self.instance.daily_workation_id)
        
        if time_workations.filter(Q(start_time__lt=value) & Q(end_time__gte=value)).exists():
            raise serializers.ValidationError('End time overlaps with existing time.')
        return value

    def validate(self, validated_data):
        daily_workation = validated_data.get('daily_workation', None)
        start_time = validated_data.get('start_time', None)
        end_time = validated_data.get('end_time', None)

        if daily_workation is not None:
            time_workations = Time_workation.objects.filter(daily_workation=daily_workation)
            if self.instance:
                time_workations = time_workations.exclude(pk=self.instance.daily_workation_id)
            for time in time_workations:
                if start_time and time.start_time <= start_time < time.end_time:
                    raise serializers.ValidationError("Start time overlaps with existing time.")
                
                if end_time and time.start_time < end_time <= time.end_time:
                    raise serializers.ValidationError("End time overlaps with existing time.")
                
                if start_time and end_time and validated_data['start_time'] <= time.start_time and validated_data['end_time'] >= time.end_time:
                    raise serializers.ValidationError("Time overlaps with existing time.")
                
        return validated_data

class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = '__all__'

class RestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rest
        fields = '__all__'


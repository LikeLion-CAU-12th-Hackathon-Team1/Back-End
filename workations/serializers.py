from rest_framework import serializers
from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.fields import ReadOnlyField, JSONField
from .models import *
from time_table import CreateTimeTable
from config.permissions import IsAuthenticatedAndReturnUser
from rest_framework.response import Response

from django.core.exceptions import ValidationError


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
    # user = PrimaryKeyRelatedField(queryset=User.objects.all())
    sigg = PrimaryKeyRelatedField(queryset=Sigg.objects.all())

    workation2space = WorkationSpaceSerializer(many=True, required=False)
    workation2rest = WorkationRestSerializer(many=True, required=False)

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
            # gpt 프롬프트 수정하고 변경해야 함.
            8, 6, 10)

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
            current_date += 1

        return workation
        
    
# 1일 단위 워케이션.
class DailyWorkationSerializer(serializers.ModelSerializer):
    workation = PrimaryKeyRelatedField(queryset=Workation.objects.all())
    base_time_table = JSONField(required=False)

    class Meta:
        model = Daily_workation
        fields = '__all__'

    def create(self, validated_data):
        workation = validated_data.pop('workation')
        base_time_table = validated_data.pop('base_time_table')
        daily_workation = Daily_workation.objects.create(workation=workation, **validated_data)

        for time_data in base_time_table:
            time_data['daily_workation'] = daily_workation.daily_workation_id
            serializer = TimeWorkationSerializer(data = time_data)
            if serializer.is_valid():
                serializer.save()
            else:
                raise serializers.ValidationError("Invalid time data.")

        return daily_workation


# 1일 단위 워케이션 - 워라벨 그래프
class DailyWorkationBalanceSerializer(serializers.ModelSerializer):
    rest_ratio = serializers.SerializerMethodField()

    class Meta:
        model = Daily_workation
        fields = ('daily_workation_id', 'rest_ratio',)
    
    def get_rest_ratio(self, obj):
        return obj.calculate_rest_ratio()
    

# 할 일.
class TaskSerializer(serializers.ModelSerializer):
    daily_workation = PrimaryKeyRelatedField(queryset=Daily_workation.objects.all(), required=False)
    time_workation = PrimaryKeyRelatedField(queryset=Time_workation.objects.all(), required=True)
    task = serializers.CharField(required=True)
    complete = serializers.BooleanField(required=False)

    class Meta:
        model = Task
        fields = '__all__'

    def create(self, validated_data):
        time_workation = validated_data.pop('time_workation', None)
        if time_workation is None:
            raise serializers.ValidationError("Time_workation must be provided.")
        super().create(validated_data)

        serializer = TimeTaskSerializer(data = time_workation)


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
    start_time = serializers.IntegerField(required=True)
    end_time = serializers.IntegerField(required=True)

    class Meta:
        model = Time_workation
        fields = '__all__'

    def validate(self, data):
        daily_workation = data['daily_workation']
        sort = data['sort']
        start_time = data['start_time']
        end_time = data['end_time']

        # 기존 시간표 가져오기
        existing_timeworks = Time_workation.objects.filter(daily_workation=daily_workation)

        # 1시간 단위로 시간 리스트 생성
        new_reservation_times = [start_time + i * 3600 for i in range((end_time - start_time) // 3600)]

        for timework in existing_timeworks:
            existing_times = [timework.start_time + i * 3600 for i in range((timework.end_time - timework.start_time) // 3600)]
            # 시간이 겹치는지 확인
            if set(new_reservation_times) & set(existing_times):
                raise serializers.ValidationError(f"{'작업' if sort == Time_workation_sort.work else '휴식'} 시간이 겹칩니다.")

        return data


    ## get_queryset 메서드는 일반적으로 뷰셋(ViewSet) 클래스에 정의됩니다.
    ## 시리얼라이저 클래스에서는 get_queryset을 사용하지 않기 때문에, 이를 적절한 뷰셋으로 옮기는 것이 바람직합니다.
    # def get_queryset(self):
    #     queryset = Time_workation.objects.all()
    #     daily_workation_id = self.request.get('daily_workation_id', None)
    #     if daily_workation_id is not None:
    #         queryset = queryset.filter(daily_workation_id=daily_workation_id)
    #     return queryset

    def update(self, instance, validated_data):
        validated_data.pop('daily_workation', None)
        return super().update(instance, validated_data)
    
    # 추가
    # def get_tasks(self, obj):
    #     # Fetch tasks related to the Time_workation through Time_task
    #     time_tasks = Time_task.objects.filter(time_workation=obj)
    #     tasks = [time_task.task for time_task in time_tasks]
    #     return TaskSerializer(tasks, many=True).data
    def get_tasks(self, obj):
        # Get all Time_task entries for this time_workation
        time_tasks = obj.timetask_set.all()
        # Extract the task ids from the time_tasks
        task_ids = time_tasks.values_list('task_id', flat=True)
        # Get the tasks
        tasks = Task.objects.filter(task_id__in=task_ids)
        return TaskSerializer(tasks, many=True).data
from rest_framework import serializers
from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.fields import ReadOnlyField, JSONField
from .models import *
from time_table import CreateTimeTable
from config.permissions import IsAuthenticatedAndReturnUser
from rest_framework.response import Response


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
# class TimeTaskSerializer(serializers.ModelSerializer):
#     task = TaskSerializer(many=True)

#     class Meta:
#         model = Time_task
#         read_only_fields = ('time_workation_id', 'task_id')
#         fields = ('task',)

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
    

# class WorkLifeBalanceSerializer(serializers.ModelSerializer):
#     daily_workation = PrimaryKeyRelatedField(queryset=Daily_workation.objects.all())
#     sort = serializers.IntegerField(required=True)
#     start_time = serializers.IntegerField(required=True)
#     end_time = serializers.IntegerField(required=True)

#     class Meta:
#         model = Time_workation
#         fields = '__all__'

#     def validate(self, data):
#         daily_workation = data['daily_workation']
#         sort = data['sort']
#         start_time = data['start_time']
#         end_time = data['end_time']

#         existing_timeworks = Time_workation.objects.filter(daily_workation=daily_workation)

#         for timework in existing_timeworks:
#             duration = (timework.end_time - timework.start_time) // 3600
#             if timework.sort == 1:  # Assuming 1 is for 'work'
#                 work_time += duration
#             else:
#                 rest_time += duration

#         total_time = work_time + rest_time
#         if total_time > 0:
#             rest_ratio = rest_time / total_time
#         else:
#             rest_ratio = 0  # Avoid division by zero
        
#         data['rest_ratio'] = rest_ratio

#         return data


# from datetime import datetime, timedelta

# class WorkLifeBalanceSerializer(serializers.ModelSerializer):
#     rest_to_total_ratio = serializers.SerializerMethodField()

#     class Meta:
#         model = Time_workation
#         read_only_fields = ('daily_workation',)
#         fields = ('sort', 'start_time', 'end_time', 'rest_to_total_ratio',)
    
#     def get_rest_to_total_ratio(self, obj):
#         work_time = timedelta()
#         rest_time = timedelta()

#         workations = Time_workation.objects.filter(daily_workation=obj.daily_workation)

#         for workation in workations:
#             duration = workation.end_time - workation.start_time
#             if workation.sort == 1:
#                 work_time += duration
#             elif workation.sort == 2:
#                 rest_time += duration

#         if work_time + rest_time == 0:
#             return 0
#         return rest_time / (work_time + rest_time)


#####

    # def get_rest_to_total_ratio(self, obj):
    #     work_time = timedelta()
    #     rest_time = timedelta()

    # # 동일한 daily_workation에 대한 모든 workation을 가져옵니다.
    #     workations = Time_workation.objects.filter(daily_workation=obj.daily_workation)
    
    #     for workation in workations:
    #         # datetime.combine()을 사용하여 time 객체를 datetime 객체로 변환합니다.
    #         start_time = datetime.combine(datetime.today(), workation.start_time)
    #         end_time = datetime.combine(datetime.today(), workation.end_time)
    #         duration = end_time - start_time
            
    #         # work와 rest에 따라 시간을 누적합니다.
    #         if workation.sort == Time_workation_sort.work:
    #             work_time += duration
    #         elif workation.sort == Time_workation_sort.rest:
    #             rest_time += duration

    #         # 총 시간을 계산합니다.
    #         total_time = work_time + rest_time
    #         if total_time == timedelta(0):
    #             return 0
            
    #         # rest 시간의 비율을 반환합니다.
    #         return rest_time / total_time


# class WorkLifeBalanceSerializer(serializers.ModelSerializer):
#     rest_to_total_ratio = serializers.SerializerMethodField()

#     class Meta:
#         model = Time_workation
#         read_only_fields = ('daily_workation',)
#         fields = ('sort', 'start_time', 'end_time', 'rest_to_total_ratio',)
    
#     def get_rest_to_total_ratio(self, obj):
#         total_work_time = timedelta()
#         total_rest_time = timedelta()
        
#         # Get all Time_workation entries for the same daily_workation as the current object
#         workations = Time_workation.objects.filter(daily_workation=obj.daily_workation)
        
#         for workation in workations:
#             duration = self.calculate_duration(workation.start_time, workation.end_time)
#             if workation.sort == Time_workation_sort.work:
#                 total_work_time += duration
#             elif workation.sort == Time_workation_sort.rest:
#                 total_rest_time += duration
        
#         total_time = total_work_time + total_rest_time
#         if total_time == timedelta():
#             return 0
        
#         # Calculate the ratio of rest time to total time
#         return total_rest_time / total_time
    
#     def calculate_duration(self, start_time, end_time):
#         """Calculate the duration between start_time and end_time assuming they are within the same day"""
#         today = datetime.today().date()
#         start_datetime = datetime.combine(today, start_time)
#         end_datetime = datetime.combine(today, end_time)
        
#         # if end_datetime < start_datetime:
#         #     # Handle cases where end_time is before start_time (if this can happen)
#         #     end_datetime += timedelta(days=1)
        
#         return end_datetime - start_datetime
from rest_framework import serializers
from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.fields import ReadOnlyField
from .models import *
from time_table import CreateTimeTable

# workation-space 중간 테이블.
class WorkationSpaceSerializer(serializers.ModelSerializer):
    space = PrimaryKeyRelatedField(queryset=Space.objects.all())
    workation = ReadOnlyField(source='workation_id')

    class Meta:
        model = Workation_space
        fields = '__all__'
        depth = 1

    def save(self, **kwargs):
        super().save(**kwargs)
        serializer = WorkationSpaceSerializer(data=self.data)
    
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
    user = PrimaryKeyRelatedField(queryset=User.objects.all())
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

        serializer = DailyWorkationSerializer(data={'workation': workation.workation_id})
        if serializer.is_valid():
            i = 0
            while validated_data['start_date'] + i <= validated_data['end_date']:
                serializer.save()
                i += 1

        return workation
        
    
# 1일 단위 워케이션.
class DailyWorkationSerializer(serializers.ModelSerializer):
    workation = PrimaryKeyRelatedField(queryset=Workation.objects.all())

    class Meta:
        model = Daily_workation
        fields = '__all__'


# 할 일.
class TaskSerializer(serializers.ModelSerializer):
    daily_workation = PrimaryKeyRelatedField(queryset=Daily_workation.objects.all())

    class Meta:
        model = Task
        fields = '__all__'

# 시간 단위 워케이션-할 일 중간 테이블.
class TimeTaskSerializer(serializers.ModelSerializer):
    task = TaskSerializer()

    class Meta:
        model = Time_task
        read_only_fields = ('time_workation_id', 'task_id')
        fields = ('task',)

# 시간 단위 워케이션.
class TimeWorkationSerializer(serializers.ModelSerializer):
    daily_workation = PrimaryKeyRelatedField(queryset=Daily_workation.objects.all())

    class Meta:
        model = Time_workation
        fields = '__all__'

class TimeTaskSerializer(serializers.ModelSerializer):
    task = PrimaryKeyRelatedField(queryset=Task.objects.all())
    time_workation = PrimaryKeyRelatedField(queryset=Time_workation.objects.all())

    class Meta:
        model = Time_task
        fields = '__all__'
        depth = 1

    # 같은 daily_workation에 속한 객체만 연결 가능.
    def validate(self, data):
        task = data.get('task')
        time_workation = data.get('time_workation')

        if task.daily_workation != time_workation.daily_workation:
            raise serializers.ValidationError("Task and Time_workation must be related to the same Daily_workation.")
        
        return data

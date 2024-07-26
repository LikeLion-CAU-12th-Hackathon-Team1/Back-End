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
        fields = '__all__' # ('workation_id', 'start_date', 'end_date', 'work', 'balance', 'space', 'rest', 'start_sleep', 'end_sleep')

from rest_framework import serializers
from .models import *

# class DailyWarkationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Daily_workation
#         field = '__all__'

# workation_rest, workation_space_type


class WorkationSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workation_space
        fields = '__all__'

class WorkationRestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workation_rest
        fields = '__all__'

class WorkationSerializer(serializers.ModelSerializer):
    space = WorkationSpaceSerializer(many=True)
    rest = WorkationRestSerializer(many=True)

    class Meta:
        model = Workation
        fields = ('workation_id', 'work', 'balance', 'space', 'rest')
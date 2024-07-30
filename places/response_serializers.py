from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from .models import Place

class ListPlaceSerializer(serializers.ModelSerializer):
    sigg = ReadOnlyField(source='sigg.sigg_id')

    class Meta:
        model = Place
        fields = ['place_code', 'placename', 'image', 'report', 'sigg']

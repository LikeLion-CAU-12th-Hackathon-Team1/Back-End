from rest_framework import serializers
from .models import Place

class ListPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        # include = ['place_code', 'placename', 'image', 'report']
        exclude = ['place_id', 'address', 'category', 'sigg_id']

from django.shortcuts import render
from rest_framework import views
from .request_serializers import PlaceCreateSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Place

class ListCreatePlace(views.APIView):
    serializer_class = PlaceCreateSerializer
    queryset = Place.objects.all()

    def get(self, request):
        places = Place.objects.all()
        serializer = PlaceCreateSerializer(places, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PlaceCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

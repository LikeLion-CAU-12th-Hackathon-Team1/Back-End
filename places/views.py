from django.shortcuts import render
from rest_framework import views
from .request_serializers import PlaceCreateSerializer
from rest_framework.response import Response
from rest_framework import status

class ListCreatePlace(views.APIView):
    def post(self, request):
        serializer = PlaceCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

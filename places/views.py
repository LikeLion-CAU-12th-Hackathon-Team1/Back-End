from django.shortcuts import render
from rest_framework import views
from .request_serializers import PlaceCreateSerializer
from .response_serializers import ListPlaceSerializer
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

class CategoryPlace(views.APIView):
    serializer_class = ListPlaceSerializer
    queryset = Place.objects.all()

    def get(self, request, sigg_id):
        category = request.GET.get('category')
        places = Place.objects.filter(sigg=sigg_id).filter(category=category)
        serializer = ListPlaceSerializer(places, many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        place = Place.objects.get(pk=pk)
        serializer = PlaceCreateSerializer(place, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        place = Place.objects.get(pk=pk)
        place.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

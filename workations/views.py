from django.shortcuts import render
from .models import *
from .serializers import *
from django.views import View
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class ListCreateWorkation(generics.ListCreateAPIView):
    queryset = Workation.objects.all()
    serializer_class = WorkationSerializer

class DailyWorkationGenericAPIView(generics.ListCreateAPIView):
    queryset = Daily_workation.objects.all()
    serializer_class = DailyWorkationSerializer

class TimeWorkationGenericAPIView(generics.ListCreateAPIView):
    queryset = Time_workation.objects.all()
    serializer_class = TimeWorkationSerializer

class TimeWorkationEditGenericAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Time_workation.objects.all()
    serializer_class = TimeWorkationSerializer
    # lookup_field = 'time_workation_id'

class TaskGenericAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TimeTaskGenericAPIView(generics.ListCreateAPIView):
    queryset = Time_task.objects.all()
    serializer_class = TimeTaskSerializer


# class WorkationScheduleGenericAPIView(generics.ListCreateAPIView):
#     queryset = Workation.objects.all()
#     serializer_class = WorkationScheduleSerializer
#     lookup_field = 'workation_id'

# class RestAPIView(generics.ListCreateAPIView):
#     queryset = Rest.objects.all()
#     serializer_class = RestSerializer

# class SpaceAPIView(generics.ListCreateAPIView):
#     queryset = Space.objects.all()
#     serializer_class = SpaceSerializer

# class WorkationCreateView(APIView):
#     def post(self, request):
#         serializer = WorkationSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

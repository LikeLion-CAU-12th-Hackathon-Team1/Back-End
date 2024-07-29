from django.shortcuts import render
from .models import *
from .serializers import *

# Create your views here.

# APIView
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.http import Http404

#GenericAPIView
from rest_framework import generics

# Create your views here.
class WorkationRegisterGenericAPIView(generics.ListCreateAPIView):
    queryset = Workation.objects.all()
    serializer_class = WorkationSerializer

# class TimeTaskGenericAPIView(generics.ListCreateAPIView):
#     queryset = Time_task.objects.all()
#     serializer_class = TimeTaskSerializer

class DailyWorkationGenericAPIView(generics.ListCreateAPIView):
    queryset = Daily_workation.objects.all()
    serializer_class = DailyWorkationSerializer

class WorkationScheduleGenericAPIView(generics.ListCreateAPIView):
    queryset = Workation.objects.all()
    serializer_class = WorkationScheduleSerializer
    lookup_field = 'workation_id'
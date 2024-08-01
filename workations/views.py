from django.shortcuts import render
from .models import *
from .serializers import *
# from django.views import View
from rest_framework import generics
# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from config.permissions import IsOwner
from datetime import datetime
import datetime as dt
from datetime import date
# Create your views here.
class ListCreateWorkation(generics.ListCreateAPIView):
    queryset = Workation.objects.all()
    serializer_class = WorkationSerializer

    def post(self, request):
        request.data['user'] = request.user.id
        start = request.data['start_date']
        end = request.data['end_date']
        request.data['start_date'] = dt.date(int(start[0:4]), int(start[4:6]), int(start[6:8]))
        request.data['end_date'] = dt.date(int(end[0:4]), int(end[4:6]), int(end[6:8]))
        serializer = WorkationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        workations = Workation.objects.filter(user=request.user.id)
        serializer = WorkationSerializer(workations, many=True)
        return Response(serializer.data)

# 데일리 워케이션을 사용자가 직접 생성, 삭제, 수정할 수 없기 때문에 뷰가 필요 없을 듯??
class DailyWorkationGenericAPIView(generics.ListCreateAPIView):
    queryset = Daily_workation.objects.all()
    serializer_class = DailyWorkationSerializer

# 타임 워케이션은 사용자가 직접 CRUD 가능하기 때문에 설정해야 함.

class DailyWorkationBalanceGenericAPIView(generics.RetrieveAPIView):
    queryset = Daily_workation.objects.all()
    serializer_class = DailyWorkationBalanceSerializer
    lookup_field = 'daily_workation_id'

class TimeWorkationGenericAPIView(generics.ListCreateAPIView):
    queryset = Time_workation.objects.all()
    serializer_class = TimeWorkationSerializer
    
    def get(self, request, daily_workation_id):
        time_workations = Time_workation.objects.filter(daily_workation=daily_workation_id)
        serializer = TimeWorkationSerializer(time_workations, many=True)
        return Response(serializer.data)

    # def post(self, request, *args, **kwargs):
    #     serializer = TimeWorkationSerializer(data=request.data)
    #     if not serializer.is_valid():
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = super().get_queryset()
        daily_workation_id = self.request.query_params.get('daily_workation_id', None)
        if daily_workation_id is not None:
            queryset = queryset.filter(daily_workation_id=daily_workation_id)
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class TaskGenericAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsOwner]

    def post(self, request, time_workation_id):
        request.data['time_workation'] = time_workation_id
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TimeTaskGenericAPIView(generics.ListCreateAPIView):
    queryset = Time_task.objects.all()
    serializer_class = TimeTaskSerializer

class RetrieveUpdateDestroyWorkation(generics.RetrieveUpdateDestroyAPIView):
    queryset = Workation.objects.all()
    serializer_class = WorkationSerializer
    lookup_field = 'workation_id'

class RetrieveUpdateDestroyDailyWorkation(generics.RetrieveUpdateDestroyAPIView):
    queryset = Daily_workation.objects.all()
    serializer_class = DailyWorkationSerializer
    lookup_field = 'daily_workation_id'

    def get(self, request, daily_workation_id):
        data = Daily_workation.objects.get(daily_workation_id=daily_workation_id)
        workation = Workation.objects.get(workation_id=data.workation.workation_id)
        serializer = DailyWorkationSerializer(data)
        data = serializer.data
        data['sigg'] = WorkationSerializer(workation).data['sigg']
        return Response(data)
    
    def patch(self, request, daily_workation_id):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetrieveUpdateDestroyTimeWorkation(generics.RetrieveUpdateDestroyAPIView):
    queryset = Time_workation.objects.all()
    serializer_class = TimeWorkationSerializer
    lookup_field = 'time_workation_id'

    def patch(self, request, time_workation_id):
        start_time = request.data.get('start_time', None)
        if start_time:
            request.data['start_time'] = dt.time(int(start_time[0:2]), int(start_time[2:4]), int(start_time[4:6]))
        end_time = request.data.get('end_time', None)
        if end_time:
            request.data['end_time'] = dt.time(int(end_time[0:2]), int(end_time[2:4]), int(end_time[4:6]))
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetrieveUpdateDestroyTask(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'task_id'

    def patch(self, request, task_id):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TodayDailyWorkation(generics.ListAPIView):
    queryset = Daily_workation.objects.all()
    serializer_class = DailyWorkationSerializer

    def get(self, request):
        today = date.today()
        try:
            daily_workation = Daily_workation.objects.get(date=today)
        except Daily_workation.DoesNotExist:
            return Response(data='there is no schedule today', status=status.HTTP_404_NOT_FOUND)
    
        serializer = DailyWorkationSerializer(daily_workation)
        return Response(serializer.data)

class WorkationRest(generics.ListCreateAPIView):
    queryset = Workation_rest.objects.all()
    serializer_class = RestSerializer

class WorkationSpace(generics.ListCreateAPIView):
    queryset = Workation_space.objects.all()
    serializer_class = SpaceSerializer

class DailyWorkationTaskList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get(self, request, daily_workation_id):
        tasks = Task.objects.filter(daily_workation=daily_workation_id)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


# 추가
# class RetrieveUpateDestroyTimeTaks(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Time_workation.objects.all()
#     serializer_class = TimeWorkationSerializer
#     lookup_field = 'time_workation_id'

class TasksByTimeWorkationView(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        time_workation_id = self.kwargs['time_workation_id']
        # Get all tasks related to the Time_workation with the given ID

        return Task.objects.filter(time_task__time_workation_id=time_workation_id)
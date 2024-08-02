from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from config.permissions import IsOwner
from datetime import datetime
import datetime as dt
from datetime import date
from django.views.decorators.http import require_GET
from django.http import JsonResponse

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

class DailyWorkationGenericAPIView(generics.ListCreateAPIView):
    queryset = Daily_workation.objects.all()
    serializer_class = DailyWorkationSerializer

class TimeWorkationGenericAPIView(generics.ListCreateAPIView):
    queryset = Time_workation.objects.all()
    serializer_class = TimeWorkationSerializer
    
    def get(self, request, daily_workation_id):
        time_workations = Time_workation.objects.filter(daily_workation=daily_workation_id)
        serializer = TimeWorkationSerializer(time_workations, many=True)
        return Response(serializer.data)
    
    def post(self, request, daily_workation_id):
        request.data['daily_workation'] = daily_workation_id
        time = request.data.get('start_time', None)
        if time is None:
            return Response(data='start_time is required', status=status.HTTP_400_BAD_REQUEST)
        request.data['start_time'] = dt.time(int(time[0:2]), int(time[2:4]), int(time[4:6]))
        time = request.data.get('end_time', None)
        if time is None:
            return Response(data='end_time is required', status=status.HTTP_400_BAD_REQUEST)
        if request.data['end_time'] == '240000':
            request.data['end_time'] = dt.time(23, 59, 59)
        else:   
            request.data['end_time'] = dt.time(int(time[0:2]), int(time[2:4]), int(time[4:6]))
        serializer = TimeWorkationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    def get(self, request, time_workation_id):
        time_tasks = Time_task.objects.filter(time_workation=time_workation_id)
        serializer = TimeTaskSerializer(time_tasks, many=True)
        return Response(serializer.data)

class RetrieveUpdateDestroyWorkation(generics.RetrieveUpdateDestroyAPIView):
    queryset = Workation.objects.all()
    serializer_class = WorkationSerializer
    lookup_field = 'workation_id'

    def get(self, request, workation_id):
        workation = Workation.objects.get(workation_id=workation_id)
        serializer = WorkationSerializer(workation)
        data = serializer.data
        daily_workations = Daily_workation.objects.filter(workation=workation_id)
        daily_workation_list = DailyWorkationSerializer(daily_workations, many=True).data
        data['daily_workation_list'] = daily_workation_list
        return Response(data)

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
        request.data['time_workation_id'] = time_workation_id
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
        serializer.data['sigg'] = WorkationSerializer(daily_workation.workation).data['sigg']
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

@require_GET
def work_rest_graph(request, daily_workation_id):
    schedules = Time_workation.objects.filter(daily_workation=daily_workation_id)
    work_time, rest_time = 0, 0
    for schedule in schedules:
        start = schedule.start_time.hour
        if schedule.end_time.minute != 0:
            end = schedule.end_time.hour + 1
        else:
            end = schedule.end_time.hour
        
        if schedule.sort == 1:
            work_time += end - start
        else:
            rest_time += end - start
    if work_time + rest_time == 0:
        return JsonResponse({
            'raio' : 0,
            'status' : 200
        })
    return JsonResponse({
        'ratio' : rest_time / (work_time + rest_time) * 100,
        'status' : 200 
        })

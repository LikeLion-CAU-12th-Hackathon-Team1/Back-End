from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from config.permissions import IsOwner
from datetime import datetime
import datetime as dt
from datetime import date
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenRefreshView

# Create your views here.
class ListCreateWorkation(generics.ListCreateAPIView):
    serializer_class = WorkationSerializer

    def get_queryset(self):
        return Workation.objects.filter(user=self.request.user)

    def post(self, request):
        request.data['user'] = request.user.id
        serializer = WorkationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DailyWorkationGenericAPIView(generics.ListCreateAPIView):
    serializer_class = DailyWorkationSerializer

    def get_queryset(self):
        return Daily_workation.objects.filter(workation__user=self.request.user).filter(workation_id=self.kwargs['workation_id'])

class TimeWorkationGenericAPIView(generics.ListCreateAPIView):
    serializer_class = TimeWorkationSerializer
    lookup_field = 'daily_workation_id'

    def get_object(self):
        return Daily_workation.objects.get(daily_workation_id=self.kwargs['daily_workation_id'])
    
    def get(self, request, daily_workation_id):
        time_workations = Time_workation.objects.filter(daily_workation_id=self.get_object().daily_workation_id)
        serializer = TimeWorkationSerializer(time_workations, many=True)
        return Response(serializer.data)
    
    def post(self, request, daily_workation_id):
        request.data['daily_workation'] = daily_workation_id
        serializer = TimeWorkationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskGenericAPIView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get(self, request, time_workation_id):
        time_tasks = Time_task.objects.filter(time_workation=time_workation_id)
        tasks = [time_task.task for time_task in time_tasks]
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, time_workation_id):
        request.data['time_workation'] = time_workation_id
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetrieveUpdateDestroyWorkation(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkationSerializer
    lookup_field = 'workation_id'

    def get_queryset(self):
        return Workation.objects.filter(user=self.request.user)

    def get(self, request, workation_id):
        workation = self.get_object()
        serializer = WorkationSerializer(workation)
        data = serializer.data

        daily_workations = Daily_workation.objects.filter(workation=workation_id)
        daily_workation_list = DailyWorkationSerializer(daily_workations, many=True).data
        daily_workation_ids = [{'daily_workation_id' : item['daily_workation_id']} for item in daily_workation_list]
        data['daily_workation_list'] = daily_workation_ids
        return Response(data)

class RetrieveUpdateDestroyDailyWorkation(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyWorkationSerializer
    lookup_field = 'daily_workation_id'

    def get_queryset(self):
        return Daily_workation.objects.filter(workation__user=self.request.user)

    def get(self, request, *args, **kwargs):
        daily_workation = self.get_object()
        serializer = DailyWorkationSerializer(daily_workation)
        daily_workations = Daily_workation.objects.filter(workation_id=daily_workation.workation_id)
        object_list = list(daily_workations)
        day = object_list.index(daily_workation)
        workation = Workation.objects.get(workation_id=daily_workation.workation.workation_id)

        data = serializer.data
        data['day'] = day + 1
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

    def delete(self, request, time_workation_id):
        time_tasks = Time_task.objects.filter(time_workation_id=time_workation_id)
        for time_task in time_tasks:
            time_task.task.delete()
        
        try:
            time_workation = get_object_or_404(Time_workation, time_workation_id=time_workation_id)
            time_workation.delete()
        except:
            return Response(data='time_workation_id is wrong.', status=status.HTTP_404_NOT_FOUND)
        return Response(data='Successfully deleted', status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, time_workation_id):
        instance = self.get_object()
        request.data['daily_workation'] = self.get_object().daily_workation.daily_workation_id
        
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
    serializer_class = DailyWorkationSerializer

    def get_queryset(self):
        return Daily_workation.objects.filter(workation__user=self.request.user)

    def get(self, request):
        today = date.today()
        try:
            daily_workation = self.get_queryset().get(date=today)
        except Daily_workation.DoesNotExist:
            return Response(data='there is no schedule today', status=status.HTTP_404_NOT_FOUND)
    
        serializer = DailyWorkationSerializer(daily_workation)
        data = serializer.data
        data['sigg'] = WorkationSerializer(daily_workation.workation).data['sigg']
        return Response(data)

class DailyWorkationTaskList(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(daily_workation__workation__user=self.request.user)

    def get(self, request, daily_workation_id):
        tasks = self.get_queryset().filter(daily_workation=daily_workation_id)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

class ClosestFutureWorkation(generics.RetrieveAPIView):
    serializer_class = WorkationSerializer

    def get_queryset(self):
        return Workation.objects.filter(user=self.request.user)
    
    def get(self, request):
        workations = self.get_queryset().filter(end_date__gte=datetime.today())
        closest_workation = workations.last()
        if closest_workation:
            serializer = self.get_serializer(closest_workation)
            data = serializer.data

            daily_workations = Daily_workation.objects.filter(workation_id=closest_workation.workation_id)
            daily_workation_list = DailyWorkationSerializer(daily_workations, many=True).data
            daily_workation_ids = [{'daily_workation_id' : item['daily_workation_id']} for item in daily_workation_list]
            data['daily_workation_list'] = daily_workation_ids
            return Response(data, status=status.HTTP_200_OK)
        return Response({'detail' : 'No future workations found'}, status=status.HTTP_404_NOT_FOUND)

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

class WorkationRest(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Workation_rest.objects.all()
    serializer_class = RestSerializer

class WorkationSpace(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Workation_space.objects.all()
    serializer_class = SpaceSerializer

class TokenRefresh(TokenRefreshView):
    pass

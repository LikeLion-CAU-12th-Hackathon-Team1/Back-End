from django.shortcuts import render
from .models import *
from .serializers import *
from django.views import View
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from config.permissions import IsOwnerOrReadOnly

# Create your views here.
class ListCreateWorkation(generics.ListCreateAPIView):
    queryset = Workation.objects.all()
    serializer_class = WorkationSerializer

    def post(self, request):
        request.data['user'] = request.user.id
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

class DailyWorkationBalanceGenericAPIView(generics.RetrieveAPIView):
    queryset = Daily_workation.objects.all()
    serializer_class = DailyWorkationBalanceSerializer
    lookup_field = 'daily_workation_id'

# 타임 워케이션은 사용자가 직접 CRUD 가능하기 때문에 설정해야 함.
class TimeWorkationGenericAPIView(generics.ListCreateAPIView):
    queryset = Time_workation.objects.all()
    serializer_class = TimeWorkationSerializer

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

class TaskGenericAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TimeTaskGenericAPIView(generics.ListCreateAPIView):
    queryset = Time_task.objects.all()
    serializer_class = TimeTaskSerializer

class RetrieveUpdateDestroyWorkation(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Workation.objects.all()
    serializer_class = WorkationSerializer
    lookup_field = 'workation_id'

class RetrieveUpdateDestroyDailyWorkation(generics.RetrieveUpdateDestroyAPIView):
    queryset = Daily_workation.objects.all()
    serializer_class = DailyWorkationSerializer
    lookup_field = 'daily_workation_id'

class RetrieveUpdateDestroyTimeWorkation(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Time_workation.objects.all()
    serializer_class = TimeWorkationSerializer
    lookup_field = 'time_workation_id'

class RetrieveUpdateDestroyTask(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = 'task_id'
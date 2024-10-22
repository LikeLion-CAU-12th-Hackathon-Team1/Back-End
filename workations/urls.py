from django.urls import path
from .views import *
# from django.conf.urls.static import static
# from django.conf import settings
# from django.contrib.auth.models import User

urlpatterns = [
    path('', ListCreateWorkation.as_view(), name='workation_list_create'),
    path('today/', TodayDailyWorkation.as_view(), name='today_workation'),
    path('closest/', ClosestFutureWorkation.as_view(), name='closest_future_workation'),
    path('<int:workation_id>/', RetrieveUpdateDestroyWorkation.as_view(), name='workation_retrieve_update_destroy'),
    path('<int:workation_id>/daily/', DailyWorkationGenericAPIView.as_view(), name='daily_workation_list_create'),
    path('daily/<int:daily_workation_id>/', RetrieveUpdateDestroyDailyWorkation.as_view(), name='daily_workation_retrieve_update_destroy'),
    path('daily/<int:daily_workation_id>/memo/', RetrieveUpdateDestroyDailyWorkation.as_view(), name='daily_workation_memo'),
    path('daily/<int:daily_workation_id>/time/', TimeWorkationGenericAPIView.as_view(), name='time_workation_list_create'),
    path('daily/time/<int:time_workation_id>/', RetrieveUpdateDestroyTimeWorkation.as_view(), name='time_workation_retrieve_update_destroy'),
    path('daily/time/<int:time_workation_id>/task/', TaskGenericAPIView.as_view(), name='task_list_create'),
    path('daily/time/<int:time_workation_id>/todolist/', TaskGenericAPIView.as_view(), name='time_task_list_create'),
    path('daily/time/task/<int:task_id>/', RetrieveUpdateDestroyTask.as_view(), name='task_retrieve_update_destroy'),
    path('daily/<int:daily_workation_id>/todolist/', DailyWorkationTaskList.as_view(), name='daily_workation_todo_list'),
    path('daily/<int:daily_workation_id>/graph/', work_rest_graph, name='daily_workation_graph'),
    path('token/refresh/', TokenRefresh.as_view(), name='refresh_access_token'),
    path('rest/', WorkationRest.as_view(), name='sido_list_create'),
    path('space/', WorkationSpace.as_view(), name='sigg_list_create'),
    path('timer/', TimerView.as_view(), name='timer'),
]
from django.urls import path
from .views import *
# from django.conf.urls.static import static
# from django.conf import settings
# from django.contrib.auth.models import User

urlpatterns = [
    path('', ListCreateWorkation.as_view(), name='workation_list_create'),
    path('<int:workation_id>/', RetrieveUpdateDestroyWorkation.as_view(), name='workation_retrieve_update_destroy'),
    path('daily/', DailyWorkationGenericAPIView.as_view(), name='daily_workation_list_create'),
    path('daily/<int:daily_workation_id>/', RetrieveUpdateDestroyDailyWorkation.as_view(), name='daily_workation_retrieve_update_destroy'),
    path('daily/<int:daily_workation_id>/balance/', DailyWorkationBalanceGenericAPIView.as_view()),
    path('daily/<int:daily_workation_id>/time/', TimeWorkationGenericAPIView.as_view(), name='time_workation_list_create'),
    path('daily/time/<int:time_workation_id>/', RetrieveUpdateDestroyTimeWorkation.as_view(), name='time_workation_retrieve_update_destroy'),
    path('daily/time/<int:time_workation_id>/task/', TaskGenericAPIView.as_view(), name='task_list_create'),
    path('daily/time/<int:time_workation_id>/task/<int:task_id>/', RetrieveUpdateDestroyTask.as_view(), name='task_retrieve_update_destroy'),
    path('daily/time/<int:time_workation_id>/todolist/', RetrieveUpateDestroyTimeTaks.as_view()),
    # path('tiemtask/', TimeTaskGenericAPIView.as_view()),
]
from django.urls import path
from .views import *
# from django.conf.urls.static import static
# from django.conf import settings
# from django.contrib.auth.models import User

urlpatterns = [
    path('', ListCreateWorkation.as_view(), name='workation_list_create'),
    # path('schedule/daily/timetask/', TimeTaskGenericAPIView.as_view()),
    # path('schedule/', WorkationScheduleGenericAPIView.as_view()),
    path('daily/', DailyWorkationGenericAPIView.as_view()),
    # path('rest/', RestAPIView.as_view()),
    # path('space/', SpaceAPIView.as_view()),
    path('time/', TimeWorkationGenericAPIView.as_view()),
    path('taks/', TaskGenericAPIView.as_view()),
    path('tiemtask/', TimeTaskGenericAPIView.as_view()),
]
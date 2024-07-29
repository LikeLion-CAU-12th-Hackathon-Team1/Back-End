from django.urls import path
from .views import *
# from django.conf.urls.static import static
# from django.conf import settings
# from django.contrib.auth.models import User

urlpatterns = [
    path('', WorkationRegisterGenericAPIView.as_view()),
    # path('schedule/daily/timetask/', TimeTaskGenericAPIView.as_view()),
    path('schedule/', WorkationScheduleGenericAPIView.as_view()),
    path('daily/', DailyWorkationGenericAPIView.as_view()),
]
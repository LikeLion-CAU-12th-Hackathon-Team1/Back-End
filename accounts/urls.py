from django.urls import path
from accounts.views import *

urlpatterns = [
    path('', hello_world, name = 'hello_world'),
    path('kakao/login/', Kakao_login.as_view(), name = 'login'),
    path('kakao/callback/', Kakao_callback.as_view(), name = 'callback'),
    path('nickname/', UserNickname.as_view(), name = 'nickname'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    kakao_id = models.BigIntegerField(null=False, unique=True)
    name = models.CharField(max_length=10)
    nickname = models.CharField(max_length=10)
    email = models.CharField(max_length=100, null=True, unique=True)
    profile = models.CharField(max_length=512, null=True, blank=True)

    USERNAME_FIELD = 'kakao_id'

    @staticmethod
    def get_user_or_none_by_kakao_id(kakao_id):
        try:
            return User.objects.get(kakao_id=kakao_id)
        except Exception:
            return None

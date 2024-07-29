from django.db import models
from accounts.models import User
from places.models import Sigg

# Create your models here.

# 업무 방식(단일)
class Workation_work(models.IntegerChoices):
    early = 1, 'early' # 오전부터 하루를 시작하고 싶어요
    mid = 2, 'mid' # 여유롭게 점심부터 시작하고 싶어요
    late = 3, 'late' # 느긋하게 오후부터 시작하고 싶어요

# 일과 쉼(단일)
class Workation_balance(models.IntegerChoices):
    work = 1, 'work' # 휴식보다 일을 집중적으로 하고 싶어요
    balance = 2, 'balance' # 일과 휴식의 균형이 중요해요
    rest = 3, 'rest' # 일보다 휴식을 주로 하고 싶어요

# 선호하는 업무 공간(복수):
class Workation_space_type(models.Model):
    space_id = models.AutoField(primary_key=True)
    space_choices = (
        (1, '바다가 보이는 공간'),
        (2, '시야 탁 트인 개방적인 공간'),
        (3, '엄무에 집중할 수 있는 나만의 독립적인 공간'),
        (4, '채광이 좋은 공간'),
    )
    space_type = models.IntegerField(choices=space_choices)


# 휴식(복수):
class Workation_rest_type(models.Model):
    rest_id = models.AutoField(primary_key=True)
    rest_choices = (
        (1, '공방'),
        (2, '게임'),
        (3, '독서'),
        (4, '라이딩'),
        (5, '영상'),
        (6, '미술'),
        (7, '산책'),
        (8, '서핑'),
        (9, '쇼핑'),
        (10, '스포츠'),
        (11, '액티비티'),
        (12, '운동'),
        (13, '요가'),
        (14, '자연힐링'),
        (15, '등산'),
    )
    rest_type = models.IntegerField(choices=rest_choices)


# 전체
class Workation(models.Model):
    workation_id = models.AutoField(primary_key=True)
    id = models.ForeignKey(User, on_delete=models.CASCADE)
    sigg_id = models.ForeignKey(Sigg, on_delete=models.CASCADE)
    start_date = models.BigIntegerField()
    end_date = models.BigIntegerField()
    start_sleep = models.IntegerField(default=0000)
    end_sleep = models.IntegerField(default=2359)
    work = models.IntegerField(
        choices = Workation_work.choices,
        default = Workation_work.mid,
    )
    balance = models.IntegerField(
        choices = Workation_balance.choices,
        default = Workation_balance.balance,
    )

class Workation_space(models.Model):
    workation_id = models.ForeignKey(Workation, related_name='space', on_delete=models.CASCADE)
    space_id = models.ForeignKey(Workation_space_type, related_name='spacetype', on_delete=models.CASCADE)


class Workation_rest(models.Model):
    workation_id = models.ForeignKey(Workation, related_name='rest', on_delete=models.CASCADE)
    rest_id = models.ForeignKey(Workation_rest_type, related_name='resttype', on_delete=models.CASCADE)


# 데일리
class Daily_workation(models.Model):
    daily_workation_id = models.AutoField(primary_key=True)
    workation_id = models.ForeignKey(Workation, related_name='daily', on_delete=models.CASCADE)
    date = models.BigIntegerField()
    memo = models.CharField(max_length=200)


# 시간별
class Time_workation_sort(models.IntegerChoices):
    work = 1, 'work'
    rest = 2, 'rest'
    etc = 3, 'etc'
    
class Time_workation(models.Model):
    time_workation_id = models.AutoField(primary_key=True)
    daily_workation_id = models.ForeignKey(Daily_workation, related_name='timeworkation', on_delete=models.CASCADE)
    sort = models.IntegerField(
        choices = Time_workation_sort.choices,
        default = Time_workation_sort.etc,
    )
    start_time = models.BigIntegerField()
    end_time = models.BigIntegerField()


# 할 일
class Task_complete(models.IntegerChoices):
    Y = 1, 'Y'
    N = 2, 'N'

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    daily_workation_id = models.ForeignKey(Daily_workation, related_name='task', on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    complete = models.IntegerField(
        choices = Task_complete.choices,
        default = Task_complete.N,
    )


class Time_task(models.Model):
    time_workation_id = models.ForeignKey(Time_workation, on_delete=models.CASCADE)
    task_id = models.ForeignKey(Task, related_name='timetask', on_delete=models.CASCADE)
from django.db import models
from accounts.models import User
from places.models import Sigg

# Create your models here.

# 업무방식(단일)
class Workation_work(models.IntegerChoices):
    early = 1, 'early'
    mid = 2, 'mid'
    late = 3, 'late'

# 일과 쉼의 등록(단일)
class Workation_balance(models.IntegerChoices):
    work = 1, 'work'
    balance = 2, 'balance'
    rest = 3, 'rest'

# 휴식 (복수)
class Workation_rest_type(models.IntegerChoices):
    workshop = 1, 'workshop'
    game = 2, 'game'
    read = 3, 'read'
    ride = 4, 'ride'
    video = 5, 'video'
    art = 6, 'art'
    walk = 7, 'walk'
    surf = 8, 'surf'
    shop = 9, 'shop'
    sport = 10, 'sport'
    activity = 11, 'activity'
    exercise = 12, 'exercise'
    yoga = 13, 'yoga'
    heal = 14, 'heal'
    climb = 15, 'climb'

# 업무공간(복수)
class Workation_space_type(models.IntegerChoices):
    beach = 1, 'beach'
    open = 2, 'open'
    independent = 3, 'independent'
    sum = 4, 'sun'


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
    space_id = models.AutoField(primary_key=True)
    space_type = models.IntegerField(
        choices = Workation_space_type.choices,
    )

class Workation_rest(models.Model):
    workation_id = models.ForeignKey(Workation, related_name='rest', on_delete=models.CASCADE)
    rest_id = models.AutoField(primary_key=True)
    rest_type = models.IntegerField(
        choices = Workation_rest_type.choices,
    )



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
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
class Space(models.Model):
    space_id = models.AutoField(primary_key=True)
    space_type = models.CharField(max_length=15)


# 휴식(복수):
class Rest(models.Model):
    rest_id = models.AutoField(primary_key=True)
    rest_type = models.CharField(max_length=15)

# 전체
class Workation(models.Model):
    workation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sigg = models.ForeignKey(Sigg, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    start_sleep = models.IntegerField(default=0000)
    end_sleep = models.IntegerField(default=2359)
    work_style = models.IntegerField(
        choices = Workation_work.choices,
        default = Workation_work.mid,
    )
    work_purpose = models.IntegerField(
        choices = Workation_balance.choices,
        default = Workation_balance.balance,
    )

    @property
    def owner(self):
        return self.user

class Workation_space(models.Model):
    workation = models.ForeignKey(Workation, on_delete=models.CASCADE)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)


class Workation_rest(models.Model):
    workation = models.ForeignKey(Workation, on_delete=models.CASCADE)
    rest = models.ForeignKey(Rest, on_delete=models.CASCADE)


# 데일리
class Daily_workation(models.Model):
    daily_workation_id = models.AutoField(primary_key=True)
    workation = models.ForeignKey(Workation, on_delete=models.CASCADE)
    date = models.DateField()
    memo = models.TextField(blank=True)

    @property
    def owner(self):
        return self.workation.user

# 시간별
class Time_workation_sort(models.IntegerChoices):
    work = 1, 'work'
    rest = 2, 'rest'
    
class Time_workation(models.Model):
    time_workation_id = models.AutoField(primary_key=True)
    daily_workation = models.ForeignKey(Daily_workation, on_delete=models.CASCADE)
    sort = models.IntegerField(choices = Time_workation_sort.choices, null=False)
    start_time = models.TimeField()
    end_time = models.TimeField()

    @property
    def owner(self):
        return self.daily_workation.workation.user

# 할 일
class Task_complete(models.IntegerChoices):
    Y = 1, 'Y'
    N = 2, 'N'

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    daily_workation = models.ForeignKey(Daily_workation, on_delete=models.CASCADE)
    description = models.CharField(max_length=28, null=True, blank=True)
    complete = models.IntegerField(
        choices = Task_complete.choices,
        default = Task_complete.N,
    )

    @property
    def owner(self):
        return self.daily_workation.workation.user

class Time_task(models.Model):
    time_workation = models.ForeignKey(Time_workation, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

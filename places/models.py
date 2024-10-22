from django.db import models

class Place_category(models.IntegerChoices):
    CAFE = 1, '카페'
    OFFICE = 2, '공유오피스'
    NATURE = 3, '자연'
    FOOD = 4, '먹거리'
    WELLNESS = 5, '웰니스'

class Sido(models.Model):
    sido_id = models.AutoField(primary_key=True)
    sido_name = models.CharField(max_length=10, null=False)
    sido_code = models.SmallIntegerField(null=False)

class Sigg(models.Model):
    sigg_id = models.AutoField(primary_key=True)
    sido = models.ForeignKey(Sido, on_delete=models.CASCADE)
    sigg_name = models.CharField(max_length=10, null=False)
    sigg_code = models.SmallIntegerField(null=False)

class Place(models.Model):
    place_id = models.AutoField(primary_key=True)
    place_code = models.BigIntegerField()
    sigg = models.ForeignKey(Sigg, on_delete=models.CASCADE)
    placename = models.CharField(max_length=30, null=False)
    address = models.CharField(max_length=200, null=False)
    image = models.URLField(max_length=512, null=True)
    category = models.IntegerField(choices=Place_category.choices, null=False)
    report = models.CharField(max_length=200, null=True)

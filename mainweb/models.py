from django.db import models
from django.conf import settings

# Create your models here.
class Rooms(models.Model):
    roomid = models.AutoField(primary_key=True)
    creater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start = models.CharField(max_length=100) # x/y
    start_txt = models.CharField(max_length=100, default='')
    end = models.CharField(max_length=100) # x/y
    end_txt = models.CharField(max_length=100, default='')
    predict_money = models.IntegerField()
    context = models.CharField(max_length=1000)
    max_people = models.IntegerField(default=4)
    start_time = models.IntegerField(default=1773501750) #unix time

class Cache_dir(models.Model):
    x = models.CharField(max_length=100)
    y = models.CharField(max_length=100)
    context = models.CharField(max_length=1000)
    
class Room_user(models.Model):
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('room', 'user')
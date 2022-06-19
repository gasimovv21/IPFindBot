from django.db import models

class UserIp(models.Model):
    Ip = models.CharField(max_length=50)
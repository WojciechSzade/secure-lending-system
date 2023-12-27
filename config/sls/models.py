from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    balance = models.IntegerField(default=100)
    pass


class SecureData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, null=True)
    id_number = models.CharField(max_length=11, null=True)


class Transfer(models.Model):
    userFrom = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='userFrom')
    userTo = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='userTo')
    amount = models.IntegerField()
    title = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    
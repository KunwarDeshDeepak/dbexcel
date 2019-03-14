from django.contrib.auth.models import User
from django.db import models


class JiraSetup(models.Model):

    url = models.CharField(max_length=200, primary_key=True)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True, null=True)

    def __str__(self):
        return self.url


class AccessToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True, null=True)
    url = models.CharField(max_length=100)
    token = models.CharField(max_length=100000)

    def __str__(self):
        return self.user.username



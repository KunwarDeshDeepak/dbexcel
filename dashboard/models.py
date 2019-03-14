from django.db import models
import datetime


# Create your models here.
class Connections(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    created_at = models.DateField("Date", default=datetime.date.today)
    used_in = models.IntegerField(max_length=10)

    class Meta:
        verbose_name_plural = "Connections"



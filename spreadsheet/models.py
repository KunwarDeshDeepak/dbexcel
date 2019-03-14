from django.db import models


# Create your models here.
class SheetActions(models.Model):
    action = models.CharField(max_length=100)
    details = models.CharField(max_length=100)

    def __str__(self):
        return self.action

    class Meta:
        verbose_name_plural = 'Sheet Actions'

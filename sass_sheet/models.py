from django.contrib.auth.models import User
from django.db import models


# Create your models here.
from spreadsheet.models import SheetActions


class ApiField(models.Model):

    app = models.CharField(max_length=10)
    action = models.CharField(max_length=100)
    api_column = models.CharField(max_length=20)
    sheet_column = models.CharField(max_length=20)

    def __str__(self):
        return self.api_column


class SasSActions(models.Model):

    app = models.CharField(max_length=10, default='Jira')
    action = models.CharField(max_length=100)
    detail = models.CharField(max_length=100)

    def __str__(self):
        return self.app + " (" + self.action + ")"

    class Meta:
        verbose_name_plural = "SasS Actions"


class SasSSheetMap(models.Model):
    app = models.CharField(max_length=10, default='Jira')
    sass_actions = models.ForeignKey(SasSActions, on_delete=models.CASCADE, default='')
    sheet_actions = models.ForeignKey(SheetActions, on_delete=models.CASCADE, default='')
    sheet_id = models.CharField(max_length=100, null=True, default='')
    worksheet_id = models.CharField(max_length=3, default='Sheet1')
    # last_row_update = models.CharField(max_length=3)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default='')
    api_columns = models.ManyToManyField(ApiField)

    def __str__(self):
        return self.app + " (" + self.sass_actions.action + ")"

    class Meta:
        verbose_name_plural = "SasS SheetMap"

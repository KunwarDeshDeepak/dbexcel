# Generated by Django 2.1.7 on 2019-03-09 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jira', '0002_sasssheetmap_worksheet_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sasssheetmap',
            name='worksheet_id',
            field=models.IntegerField(default=0, max_length=3),
        ),
    ]

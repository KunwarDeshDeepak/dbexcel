# Generated by Django 2.1.7 on 2019-03-11 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sass_sheet', '0005_auto_20190310_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sasssheetmap',
            name='worksheet_id',
            field=models.CharField(default='Sheet1', max_length=3),
        ),
    ]
# Generated by Django 2.1.7 on 2019-03-10 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sass_sheet', '0003_auto_20190310_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sasssheetmap',
            name='sheet_id',
            field=models.CharField(default='none', max_length=100, null=True),
        ),
    ]

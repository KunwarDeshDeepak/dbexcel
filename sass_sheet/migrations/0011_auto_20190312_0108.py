# Generated by Django 2.1.7 on 2019-03-12 01:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sass_sheet', '0010_auto_20190311_0800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sasssheetmap',
            name='sass_actions',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='sass_sheet.SasSActions'),
        ),
    ]
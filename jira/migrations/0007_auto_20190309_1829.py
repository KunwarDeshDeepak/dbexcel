# Generated by Django 2.1.7 on 2019-03-09 18:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jira', '0006_sassactions_app'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sasssheetmap',
            name='sass_actions',
        ),
        migrations.RemoveField(
            model_name='sasssheetmap',
            name='sheet_actions',
        ),
        migrations.RemoveField(
            model_name='sasssheetmap',
            name='user',
        ),
        migrations.DeleteModel(
            name='SasSActions',
        ),
        migrations.DeleteModel(
            name='SasSSheetMap',
        ),
        migrations.DeleteModel(
            name='SheetActions',
        ),
    ]

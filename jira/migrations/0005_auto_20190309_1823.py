# Generated by Django 2.1.7 on 2019-03-09 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jira', '0004_sasssheetmap_app'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sasssheetmap',
            old_name='jira_actions',
            new_name='sass_actions',
        ),
    ]

from django.urls import path

from jira.views import jira_form, jira_webhook,\
                       get_spread_sheet_and_actions

url_patterns = [
    path('map/', get_spread_sheet_and_actions),
    path('jira_webhook/', jira_webhook),
    path('', jira_form, name='jira_form')
]

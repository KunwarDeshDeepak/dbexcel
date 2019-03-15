from django.urls import path

from spreadsheet.views import get_worksheets_from_spreadsheet,\
                              google_sign, google_auth_submit, get_changes

url_patterns_sheet = [
    path('google/submit/', google_auth_submit),
    path('google/', google_sign),
    path('webhook/', get_changes),
    path('<str:sheet_key>/worksheets/', get_worksheets_from_spreadsheet)
]

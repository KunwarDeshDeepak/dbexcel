from django.urls import path

from hiway.views import sheet_to_hiway

url_patterns_hiway = [
    path('upload/', sheet_to_hiway)
]
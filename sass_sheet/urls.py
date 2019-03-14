from django.urls import path

from sass_sheet.views import add_api_fields_to_db, get_api_fields, create_action_map

url_patterns_sass = [
    path('create_action/', create_action_map),
    path('api_fields/', get_api_fields),
    path('add_data/', add_api_fields_to_db)
]
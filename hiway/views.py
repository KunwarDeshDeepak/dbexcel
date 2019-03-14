import json

import gspread
import requests
from django.core.exceptions import ObjectDoesNotExist
from oauth2client import client
from pydrive.auth import GoogleAuth
from rest_framework.decorators import api_view
from rest_framework.response import Response
from jira.models import AccessToken


@api_view(['GET'])
def sheet_to_hiway(request):

    # gauth = GoogleAuth()
    #
    # try:
    #     user_google_creds = AccessToken.objects.get(user=request.user)
    # except ObjectDoesNotExist:
    #     return Response(status=400, data={'message': 'Google authentication is pending'})
    #
    # gauth.credentials = client.Credentials.new_from_json(user_google_creds.token)
    #
    # if gauth.credentials.access_token_expired:
    #     gauth.Refresh()
    #     user_google_creds.token = gauth.credentials.to_json()
    #     user_google_creds.save()
    #
    # sheet_client = gspread.authorize(gauth.credentials)
    # spread_sheet = sheet_client.open_by_key('1MjpjJtjD8RQuyrTVZIIzY7kQOod8qN6fg3uYnAbBiMI')
    # worksheet = spread_sheet.get_worksheet(0)
    # list_of_lists = worksheet.get_all_values()
    #
    # refreshed__user_creds = gauth.credentials.to_json()
    # json_data = json.dumps(refreshed__user_creds)
    # print(refreshed__user_creds)
    # access_token = json_data['access_token']
    # print(access_token)
    #
    # header = {
    #     'Authorization': 'JWT eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFuc2h1bWFuLmthdXNoaWsiLCJ1c2VyX2lkIjo1NjEsImVtYWlsIjoiYW5zaHVtYW4ua2F1c2hpa0BoYXNoZWRpbi5jb20iLCJleHAiOjE1NTI4NTQwMjd9.XGx025g85h_qyI3US0so5ThnggH5Qe5Ba07aKBuUobFaj-ljwV1zaJddhKB9dm4nn4zNu4jmxV2g4QkW5YmT3Q-TB7C1z9Jb2g-5YPCSIvTAuNqJ2VigmTa0vtG_V4lZs8WI_dR-aQ-TZlrMPFXiJ85lWzn2q1HQrOsWzgkm8v65tbPY9weUp94eZvDmcQk2LCL9DKP1-Tzht6rfQzzFivsTE0kcyAy14-iErTWOgnus87iD9DV9vVtLPvNvifqrBc6Rc7RvfqM_wsPhJcsIeRiEk3RZ1VZjT-oh5sDLbvfilOTOIbskhWGmZFhDIoXZvWSOQzBuIEcr2FNJy7k6Qw',
    #     'Content-Type': 'application/json',
    #     'Accept': 'application/json'
    # }
    #
    # url = 'https://hiway.hashedin.com/api/v1/profiledetails/561/'
    # response = requests.get(url, headers=header)
    #
    # # i = 0
    # #
    # # for cur_list in list_of_lists:
    # #     if i == 0:
    # #         i = 1
    # #         continue
    # #     for cur_item in cur_list:
    # #         print(worksheet.cell(1, 2).value)

    return Response(status=200, data={'message': 'done'})

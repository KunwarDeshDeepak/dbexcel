import gspread
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from oauth2client import client
from pydrive.auth import GoogleAuth
from rest_framework.decorators import api_view
from rest_framework.response import Response
from configurations import server_url
from custom_exceptions import NoTokenFoundError
from jira.models import AccessToken, JiraSetup
from sass_sheet.models import ApiField, SasSSheetMap, SasSActions
import base64
import urllib3
import json
import uuid
import requests
from spreadsheet.models import SheetActions
from datetime import datetime


@csrf_exempt
@api_view(['POST'])
def create_action_map(request):
    # Add action to database first
    app_name = request.data.get('app')
    sass_action = request.data.get('sass_action')
    sheet_action = request.data.get('sheet_action')
    sheet_id = request.data.get('sheet')
    worksheet_index = request.data.get('worksheet')

    try:
        sass_action_obj = SasSActions.objects.get(app=app_name, action=sass_action)
    except ObjectDoesNotExist:
        return Response(status=400, data={'message': 'Sass action not found'})

    try:
        sheet_action_obj = SheetActions.objects.get(action=sheet_action)
    except ObjectDoesNotExist:
        return Response(status=200, data={'message': 'Sheet action not found'})

    current_user = User.objects.get(username='admin')
    sass_sheet_map = SasSSheetMap(app=app_name, sass_actions=sass_action_obj, sheet_actions=sheet_action_obj,
                                  sheet_id=sheet_id, worksheet_id=worksheet_index, user=current_user)

    # Save api columns also
    sass_sheet_map.save()
    sass_sheet_map_fetch = SasSSheetMap.objects.filter(app=app_name, sass_actions=sass_action_obj).first()

    for column in request.data.get('columns'):
        try:
            api_field = ApiField.objects.get(app=app_name, api_column=column)
        except ObjectDoesNotExist:
            return Response(status=400, data={'message': 'API column not found'})
        sass_sheet_map_fetch.api_columns.add(api_field)
        sass_sheet_map_fetch.save()

    # create SasS webhook
    if app_name == 'Jira':
        user = User.objects.get(username='admin')  # request.user
        event = []
        if sass_action == 'Create new issue':
            event.append("jira:issue_created")
            event.append("jira:issue_updated")
        elif sass_action == 'Create new comment':
            event.append("comment_created")
            event.append("comment_updated")
        elif sass_action == 'Create new project':
            event.append("project_created")

        response = create_jira_webhook(user, event)
        if response.status_code == 400:
            return response

    # create google webhook
    try:
        user_creds = AccessToken.objects.get(user=user)

        if user_creds.token == '':
            raise NoTokenFoundError
    except ObjectDoesNotExist:
        return Response(status=400, data={'message': 'User does not have SasS account setup'})
    except NoTokenFoundError:
        return Response(status=400, data={'message': 'User does not have google account setup'})

    token = user_creds.token

    # create_channel(token, sheet_id)

    header_list = []
    if sass_action == 'Create new issue':
        header_list = add_header_to_spreadsheet_new_issue(request.data)
    elif sass_action == 'Create new comment':
        header_list = add_header_to_spreadsheet_new_comment(request.data)
    elif sass_action == 'Create new project':
        header_list = add_header_to_spreadsheet_new_project(request.data)

    gauth = GoogleAuth()

    gauth.credentials = client.Credentials.new_from_json(token)

    sheet_client = gspread.authorize(gauth.credentials)

    sheet = sheet_client.open_by_key(sheet_id)

    worksheet = sheet.worksheet(worksheet_index)
    worksheet.append_row(header_list)

    return Response(status=200, data={'message': 'All done'})


@api_view(['GET'])
def get_api_fields(request):
    app_name = request.GET.get('app')
    action = request.GET.get('action')

    api_field_list = ApiField.objects.filter(app=app_name, action=action)

    api_fields = []
    for api_field in api_field_list:
        api_fields.append(api_field.api_column)

    return Response(status=500, data={'data': api_fields})


# For automating process of adding data into database
def add_api_fields_to_db(request):
    sheet_key = "1XUvOZiqDWlWJ5wWqa5knjmmAzYW0jg66OvryS_nO0HI"

    try:
        access_token = AccessToken.objects.get(user=request.user)

        if access_token.token == '':
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        return Response(status=400, data={'message': 'User has not done authentication with google'})

    gauth = GoogleAuth()
    gauth.credentials = client.Credentials.new_from_json(access_token.token)

    sheet_client = gspread.authorize(gauth.credentials)

    sheet = sheet_client.open_by_key(sheet_key)

    worksheet = sheet.worksheet('Sheet1')

    values_list = worksheet.row_values(1)

    for value in values_list:
        ApiField.objects.create(app='Jira', action='Create new comment', api_column=value, sheet_column=value)


# create a jira webhook in user's account
def create_jira_webhook(user, event):
    try:
        jira_creds = JiraSetup.objects.get(user=user)
    except ObjectDoesNotExist:
        return Response(status=400, data={'message': 'User does not have Jira account setup'})

    jira_email = jira_creds.email
    jira_password = jira_creds.password
    jira_url = jira_creds.url

    encoded_cred = base64.b64encode((jira_email + ':' + jira_password).encode('utf-8')).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + encoded_cred
    }

    url = jira_url + "/rest/webhooks/1.0/webhook/"

    http = urllib3.PoolManager()
    data = json.dumps({
        "name": "Webhook for spreadsheet",
        "url": server_url + "/jira/jira_webhook/",
        "events": event,
        "excludeBody": False
    })

    http.request("POST", url, headers=headers, body=data)
    return Response(status=200, data={'message': 'Jira webhook successfully created'})


# create Channel with spread sheet
def create_channel(token, sheet_id):
    gauth = GoogleAuth()
    gauth.credentials = client.Credentials.new_from_json(token)

    if gauth.access_token_expired:
        gauth.Refresh()

    token = gauth.credentials.to_json()
    token_json = json.loads(token)
    access_token = token_json['access_token']

    uuid_str = str(uuid.uuid4())

    expiration_time = int(datetime.now().strftime("%s")) * 1000
    expiration_time = expiration_time + 12 * 6 * 12 * 100000 - 600000
    print(expiration_time)

    body_data = {

        "id": uuid_str,
        "type": "web_hook",
        "address": server_url + '/sheets/webhook/',
        'expiration': expiration_time

    }

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'

    }

    url = 'https://www.googleapis.com/drive/v3/files/' + sheet_id + '/watch'
    r = requests.post(url, data=json.dumps(body_data), headers=headers)
    print(r.content)
    return r


def google_domain_verification(request):
    return HttpResponse("google-site-verification: googleef42bae5a39aace7.html")


def add_header_to_spreadsheet_new_issue(data):

    header_list = ['Issue Key', 'Project Key']

    columns = data.get('columns')

    for column in columns:
        header_list.append(column)

    return header_list


def add_header_to_spreadsheet_new_comment(data):

    header_list = ['Issue Key', 'Comment Id']

    columns = data.get('columns')

    for column in columns:
        header_list.append(column)

    return header_list


def add_header_to_spreadsheet_new_project(data):

    header_list = ['Project Id', 'Project Key']

    columns = data.get('columns')

    for column in columns:
        header_list.append(column)

    return header_list

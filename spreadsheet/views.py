import webbrowser
import gspread
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from oauth2client import client
from pydrive.auth import GoogleAuth
from rest_framework.decorators import api_view
from rest_framework.response import Response
from jira.models import AccessToken, JiraSetup
import requests
import pandas as pd
import io
import json
from sass_sheet.models import SasSSheetMap
import base64
import urllib3


@login_required
def google_sign(request):
    gauth = GoogleAuth()
    scope = {'oauth_scope': ['https://www.googleapis.com/auth/drive']}
    gauth.DEFAULT_SETTINGS.update(scope)

    try:
        access = AccessToken.objects.get(user=request.user)

        if access.token is '':
            print('nothing to worry here')
        else:
            gauth.credentials = client.Credentials.new_from_json(access.token)

    except ObjectDoesNotExist:
        return "<h1> You did not setup any SasS account</h1>"

    if gauth.credentials is None:
        # Authenticate if they're not there
        authorize_url = gauth.GetAuthUrl()
        webbrowser.open(authorize_url, new=1, autoraise=True)

        return render(request, 'google_form.html')

    elif gauth.access_token_expired:
        # Refresh them if expired
        print('Refresh')
        gauth.Refresh()
    else:
        # Initialize the saved creds
        print('Authorized')
        gauth.Authorize()

    return redirect('/dashboard/config/')


@api_view(['POST'])
def google_auth_submit(request):
    google_auth_code = request.POST.get('google')

    user_creds = AccessToken.objects.get(user=request.user)
    gauth = GoogleAuth()
    gauth.Auth(google_auth_code)

    user_creds.token = gauth.credentials.to_json()
    user_creds.save()

    return redirect('/dashboard/config/')


# API to get list of worksheets from a spread sheet
@api_view(['GET'])
def get_worksheets_from_spreadsheet(request, sheet_key):
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

    worksheet_list = sheet.worksheets()

    worksheets = []
    for worksheet in worksheet_list:
        worksheets.append(worksheet.title)

    return Response(status=200, data={'data': worksheets})


# It will get called when ever change occurs in google spread sheet
@csrf_exempt
@api_view(['POST'])
def get_changes(request):
    print("It Worked!!!!!")
    resource_uri = request.META['HTTP_X_GOOG_RESOURCE_URI']

    str = resource_uri[42:]
    file_id = ''
    for i in str:

        if i == '?':
            break
        file_id = file_id + i

    saas_sheet_map_obj = SasSSheetMap.objects.get(sheet_id=file_id)
    action_performed = saas_sheet_map_obj.sass_actions.action
    print(action_performed)
    if action_performed=='Create new issue':
        issues_changes(file_id)
    elif action_performed == 'Create new comment':
        comment_changes(file_id)

def issues_changes(file_id):
    # we will retrieve the user and then the google Access - token of the user from this file_id
    revision_url = 'https://www.googleapis.com/drive/v2/files/' + file_id + '/revisions?fields=items(exportLinks%2Cid)'

    # if the token is not valid then do refresh the token.

    # Fetch user using sheet id then fetch access token using user
    try:
        sass_obj = SasSSheetMap.objects.filter(sheet_id=file_id).first()
        user_credentials = AccessToken.objects.get(user=sass_obj.user)
        jira_creds = JiraSetup.objects.get(user=sass_obj.user)  # check if it works fine
    except ObjectDoesNotExist:
        return 'User credentials not found google account'

    token = user_credentials.token

    gauth = GoogleAuth()

    gauth.credentials = client.Credentials.new_from_json(token)

    if gauth.access_token_expired:
        gauth.Refresh()

    # authorizing the gspread
    sheet_client = gspread.authorize(gauth.credentials)
    sheet = sheet_client.open_by_key(file_id)
    worksheet = sheet.get_worksheet(
        0)  # check if the name of worksheet is provided then go with the name, here going with the spreadsheet index

    new_token = gauth.credentials.to_json()

    # Get access token from Json
    json_token = json.loads(new_token)
    access_token = json_token['access_token']

    headers = {
        'Authorization': 'Bearer ' + access_token
        , 'Accept': 'application/json'

    }

    r = requests.get(revision_url, headers=headers)

    data = r.json()
    l = len(data['items'])

    latest_update = data['items'][l - 1]['id']  # fetching the latest update id for this file
    num = int(latest_update) - 1
    latest_upd = convert_str(num)
    export_link_prev = 'https://docs.google.com/spreadsheets/export?id=' + file_id + '&revision=' + latest_upd + '&exportFormat=csv'
    export_link_latest = 'https://docs.google.com/spreadsheets/export?id=' + file_id + '&revision=' + latest_update + '&exportFormat=csv'

    spreadsheet_data_prev = requests.get(export_link_prev, headers=headers).content
    spreadsheet_data_latest = requests.get(export_link_latest, headers=headers).content

    df1 = pd.read_csv(io.BytesIO(spreadsheet_data_prev), encoding='utf8')
    df2 = pd.read_csv(io.BytesIO(spreadsheet_data_latest), encoding='utf8')

    # print(df1)
    # print(df2)

    diff_df = pd.concat([df2, df1]).drop_duplicates(keep=False)
    # print(diff_df)
    ###
    # print(diff_df)
    if diff_df.empty:
        return Response(status=200, data={'msg': "Action completed successfully"})

    changes = list(diff_df.iloc[0])
    header = list(diff_df.columns)
    diff_dic = {}

    for i in range(len(header) - 1):
        if type(changes[i]) == type('check'):
            diff_dic[convert_str(header[i])] = changes[i]
        else:
            diff_dic[convert_str(header[i])] = ''
    print(diff_dic)
    row_num = diff_df.index.values[0]

    if diff_dic['Issue Key'] != '':
        if diff_dic['Project Key'] != '':
            update_jira_issue(jira_creds, diff_dic)
            print("2 worked")

    elif diff_dic['Project Key'] != '':
        print("1 worked")
        res = create_jira_issue(jira_creds, diff_dic)
        # print(res)
        worksheet.update_cell(row_num + 2, 1, res)

    return Response(status=200, data={'msg': "Action completed successfully"})


def comment_changes(file_id):
    # we will retrieve the user and then the google Access - token of the user from this file_id
    revision_url = 'https://www.googleapis.com/drive/v2/files/' + file_id + '/revisions?fields=items(exportLinks%2Cid)'

    # if the token is not valid then do refresh the token.

    # Fetch user using sheet id then fetch access token using user
    try:
        sass_obj = SasSSheetMap.objects.filter(sheet_id=file_id).first()
        user_credentials = AccessToken.objects.get(user=sass_obj.user)
        jira_creds = JiraSetup.objects.get(user=sass_obj.user)  # check if it works fine
    except ObjectDoesNotExist:
        return 'User credentials not found google account'

    token = user_credentials.token

    gauth = GoogleAuth()

    gauth.credentials = client.Credentials.new_from_json(token)

    if gauth.access_token_expired:
        gauth.Refresh()

    # authorizing the gspread
    sheet_client = gspread.authorize(gauth.credentials)
    sheet = sheet_client.open_by_key(file_id)
    worksheet = sheet.get_worksheet(
        0)  # check if the name of worksheet is provided then go with the name, here going with the spreadsheet index

    new_token = gauth.credentials.to_json()

    # Get access token from Json
    json_token = json.loads(new_token)
    access_token = json_token['access_token']

    headers = {
        'Authorization': 'Bearer ' + access_token
        , 'Accept': 'application/json'

    }

    r = requests.get(revision_url, headers=headers)

    data = r.json()
    l = len(data['items'])

    latest_update = data['items'][l - 1]['id']  # fetching the latest update id for this file
    num = int(latest_update) - 1
    latest_upd = convert_str(num)
    export_link_prev = 'https://docs.google.com/spreadsheets/export?id=' + file_id + '&revision=' + latest_upd + '&exportFormat=csv'
    export_link_latest = 'https://docs.google.com/spreadsheets/export?id=' + file_id + '&revision=' + latest_update + '&exportFormat=csv'

    spreadsheet_data_prev = requests.get(export_link_prev, headers=headers).content
    spreadsheet_data_latest = requests.get(export_link_latest, headers=headers).content

    df1 = pd.read_csv(io.BytesIO(spreadsheet_data_prev), encoding='utf8')
    df2 = pd.read_csv(io.BytesIO(spreadsheet_data_latest), encoding='utf8')

    # print(df1)
    # print(df2)

    diff_df = pd.concat([df2, df1]).drop_duplicates(keep=False)
    # print(diff_df)
    ###
    # print(diff_df)
    if diff_df.empty:
        return Response(status=200, data={'msg': "Action completed successfully"})

    changes = list(diff_df.iloc[0])
    header = list(diff_df.columns)
    diff_dic = {}

    for i in range(len(header) - 1):
        if type(changes[i]) == type('check'):
            diff_dic[convert_str(header[i])] = changes[i]
        else:
            diff_dic[convert_str(header[i])] = ''
    print(diff_dic)
    row_num = diff_df.index.values[0]

    if diff_dic['Comment Id'] != '':
        if diff_dic['Issue Key'] != '':
            update_jira_comment(jira_creds, diff_dic)
            print("2 worked")

    elif diff_dic['Comment'] != '':
        if diff_dic['Issue Key'] != '':
            print("1 worked")
            res = create_jira_comment(jira_creds, diff_dic)
            # print(res)
            worksheet.update_cell(row_num + 2, 2, res)

    return Response(status=200, data={'msg': "Action completed successfully"})


# Create Jira issue rest api
def create_jira_issue(jira_creds, diff_dic):
    print('Create Issue')
    url = jira_creds.url + '/rest/api/2/issue/'
    print(url)
    jira_email = jira_creds.email
    jira_password = jira_creds.password

    # print(jira_email)
    # print(jira_password)

    encoded_cred = base64.b64encode((jira_email + ':' + jira_password).encode('utf-8')).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + encoded_cred
    }

    data = json.dumps({
        "fields": {
            "project":
                {
                    "key": diff_dic['Project Key']

                },

            "summary": diff_dic['Issue Summary'],
            "status": {
                "name": diff_dic['Status']
            },
            "issuetype": {
                "name": "Bug"
            }
        }
    })

    r = requests.post(url, headers=headers, data=data)
    print('Response')
    print(r)
    print(r.content)
    print(r.json()['key'])
    return r.json()['key']
    # return Response(status=200, data={'message': 'Jira Issue successfully created'})


# update jira issue with rest api
def update_jira_issue(jira_creds, diff_dic):
    print('Update Issue')
    url = jira_creds.url + '/rest/api/2/issue/' + diff_dic['Issue Key']

    jira_email = jira_creds.email
    jira_password = jira_creds.password

    encoded_cred = base64.b64encode((jira_email + ':' + jira_password).encode('utf-8')).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + encoded_cred
    }


    data = json.dumps({
        "fields": {

            "summary": diff_dic['Issue Summary'],
            "issuetype": {
                "name": diff_dic['Issue Type']
            },
            "status": {
                "name": diff_dic['Status']
            }

            # "priority": {
            #     "name":diff_dic['Priority']
            # },

            # "status" : {
            #     "name":diff_dic['Status']
            # }

        }
    })

    # http.request("POST", url, headers=headers, body=data)
    r = requests.put(url, headers=headers, data=data)
    print(r.json())
    return Response(status=200, data={'message': 'Jira Issue successfully created'})



def create_jira_comment(jira_creds,diff_dic):

    url = jira_creds.url + '/rest/api/2/issue/' + diff_dic['Issue Key'] +'/comment'
    print(url)
    jira_email = jira_creds.email
    jira_password = jira_creds.password

    encoded_cred = base64.b64encode((jira_email + ':' + jira_password).encode('utf-8')).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + encoded_cred
    }

    data = json.dumps({
    "body":diff_dic['Comment']
})

    r = requests.post(url, headers=headers, data=data)
    print('Response')
    print(r)
    print(r.content)
    print(r.json()['key'])
    return r.json()['key']
    # return Response(status=200, data={'message': 'Jira Issue successfully created'})


def update_jira_comment(jira_creds,diff_dic):
    url = jira_creds.url + '/rest/api/2/issue/' + diff_dic['Issue Key'] +'/editmeta'
    print(url)
    jira_email = jira_creds.email
    jira_password = jira_creds.password

    encoded_cred = base64.b64encode((jira_email + ':' + jira_password).encode('utf-8')).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + encoded_cred
    }

    data = json.dumps({ "update": { "comments": [{"edit": {"id": diff_dic['Comment Id'], "body": diff_dic['Comment']} } ] } })

    r = requests.post(url, headers=headers, data=data)
    print('Response')
    print(r)
    print(r.content)
    print(r.json()['key'])
    return r.json()['key']
    # return Response(status=200, data={'message': 'Jira Issue successfully created'})




def convert_str(num):
    return str(num)

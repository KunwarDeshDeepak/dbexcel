from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from gspread import CellNotFound
from oauth2client import client
from rest_framework.decorators import api_view
from pydrive.auth import GoogleAuth
import gspread
from jira.forms import JiraSetupForm
from jira.models import AccessToken, JiraSetup
from sass_sheet.models import SasSSheetMap, SasSActions


@require_POST
@csrf_exempt
@api_view(['POST'])
def jira_webhook(request):

    webhook_event = request.data.get('webhookEvent')

    if webhook_event == 'jira:issue_created' or webhook_event == 'jira:issue_updated':
        url = request.data.get('user').get('self')

        jira_user = get_user(url)
        sheet_client = get_sheet_client(jira_user)

        return HttpResponse(handle_jira_new_issue(sheet_client, jira_user, request.data))

    elif webhook_event == 'comment_created' or 'comment_updated':
        print('it reached here')
        url = request.data.get('comment').get('self')
        jira_user = get_user(url)
        sheet_client = get_sheet_client(jira_user)

        return HttpResponse(handle_jira_new_comment(sheet_client, jira_user, request.data))

    elif webhook_event == 'project_created':
        url = request.data.get('project').get('self')
        jira_user = get_user(url)
        sheet_client = get_sheet_client(jira_user)

        return HttpResponse(handle_jira_new_project(sheet_client, jira_user, request.data))

    return HttpResponse('<h1> Cannot handle this type of webhook</h1>')


def get_user(url):
    index = url.rindex('/rest')
    url = url[:index]
    print(url)
    try:
        jira_setup = JiraSetup.objects.get(url=url)
    except ObjectDoesNotExist:
        return 'No token found'

    return jira_setup.user


def get_sheet_client(user):

    gauth = GoogleAuth()

    try:
        access_token = AccessToken.objects.get(user=user)
    except ObjectDoesNotExist:
        return 'No Access token found'

    gauth.credentials = client.Credentials.new_from_json(access_token.token)

    return gspread.authorize(gauth.credentials)


def handle_jira_new_issue(sheet_client, user, data):
    sass_action = SasSActions.objects.get(app='Jira', action='Create new issue')
    try:
        sheet_map = SasSSheetMap.objects.get(user=user, sass_actions=sass_action)
    except ObjectDoesNotExist:
        return "You do not have any action for this trigger"

    if sheet_map.sheet_actions.action == 'Create new spreadsheet row':
        sheet_id = sheet_map.sheet_id

        working_spread_sheet = sheet_client.open_by_key(sheet_id)
        worksheet = working_spread_sheet.worksheet(sheet_map.worksheet_id)

        worksheet_selected_columns = get_selected_columns_new_issue(data, sheet_map)

        try:
            cell = worksheet.find(data.get('issue').get('key'))
            worksheet.delete_row(cell.row)
            worksheet.insert_row(worksheet_selected_columns, cell.row)
        except CellNotFound:
            worksheet.append_row(worksheet_selected_columns)

    elif sheet_map.sheet_actions.action == 'Create new spreadsheet':
        sheet_name = data.get('issue').get('key')
        create_new_spreadsheet(sheet_name, sheet_client)
    else:
        return 'No Action found for this request'

    return "Work sheet added"


def handle_jira_new_comment(sheet_client, user, data):

    try:
        sass_action = SasSActions.objects.get(app='Jira', action='Create new comment')
    except ObjectDoesNotExist:
        print('No Action found for jira comment')
        return 'No Action Found'

    try:
        sheet_map = SasSSheetMap.objects.get(user=user, sass_actions=sass_action)
    except ObjectDoesNotExist:
        return 'You do not have any action for this trigger'

    if sheet_map.sheet_actions.action == 'Create new spreadsheet row':
        # Get file and write data into it
        sheet_id = sheet_map.sheet_id

        sheet = sheet_client.open_by_key(sheet_id)
        worksheet = sheet.worksheet(sheet_map.worksheet_id)

        worksheet_selected_columns = get_selected_columns_new_comment(data, sheet_map)

        try:
            cell = worksheet.find(data.get('comment').get('id'))
            worksheet.delete_row(cell.row)
            worksheet.insert_row(worksheet_selected_columns, cell.row)
        except CellNotFound:
            worksheet.append_row(worksheet_selected_columns)

    elif sheet_map.sheet_actions.action == 'Create new spreadsheet':
        sheet_name = data.get('comment').get('id')
        create_new_spreadsheet(sheet_name, sheet_client)

    return "Comment Added"


def handle_jira_new_project(sheet_client, user, data):

    try:
        sass_action = SasSActions.objects.get(app='Jira', action='Create new project')
    except ObjectDoesNotExist:
        return 'No Action Found'

    try:
        sheet_map = SasSSheetMap.objects.get(user=user, jira_actions=sass_action)
    except ObjectDoesNotExist:
        return HttpResponse('<h1> You do not have any action for this trigger </h1>')

    if sheet_map.sheet_actions.action == "create new spreadsheet row":
        # Get file and write data into it
        sheet_id = sheet_map.sheet_id

        sheet = sheet_client.open_by_key(sheet_id)
        worksheet = sheet.worksheet(sheet_map.worksheet_id)
        header_list = get_selected_columns_new_project(data, sheet_map)
        worksheet.append_row(header_list)

    elif sheet_map.sheet_actions.action == 'Create new spreadsheet':
        sheet_name = data.get('project').get('key')
        create_new_spreadsheet(sheet_name, sheet_client)

    return "Project Added"


def create_new_spreadsheet(sheet_name, sheet_client):
    sh = sheet_client.create(sheet_name)


def jira_form(request):
    # if this is a POST request we need to process the form data

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = JiraSetupForm(request.user, request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            jira_setup = JiraSetup(url=form.cleaned_data['url'], email=form.cleaned_data['email'],
                                   password=form.cleaned_data['password'], user=request.user)
            jira_setup.save()

            url = form.cleaned_data['url']

            token = AccessToken(user=request.user, url=url, token='')
            token.save()

            return HttpResponseRedirect('/sheets/google/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = JiraSetupForm(request.user)

    try:
        JiraSetup.objects.get(user=request.user)
        return HttpResponseRedirect('/sheets/google/')
    except ObjectDoesNotExist:
        print('Jira setup not found nothintg to worry about this')

    return render(request, 'jira/jira_form.html', {'form': form})


# Get list of Jira has and list of spread sheets
def get_spread_sheet_and_actions(request):
    jira_actions = SasSActions.objects.values()
    jira_actions_list = [entry for entry in jira_actions]

    gauth = GoogleAuth()

    try:
        access_token = AccessToken.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return HttpResponse('<h1> No token found </h1>')

    gauth.credentials = client.Credentials.new_from_json(access_token.token)

    sheet_client = gspread.authorize(gauth.credentials)

    sheet_list = []

    for sheet in sheet_client.openall():
        sheet_list.append(sheet)

    context = {
        'sheet_list': sheet_list,
        'jira_actions_list': jira_actions_list
    }

    return render(request, 'jira/map_action.html', {'context': context})


# Get data according to selected columns for create new issue action
def get_selected_columns_new_issue(data, sheet_map):

    issue_id = data.get('issue').get('id')
    issue_key = data.get('issue').get('key')
    issue_type = data.get('issue').get('fields').get('issuetype').get('name')
    summary = data.get('issue').get('fields').get('summary')
    project_id = data.get('issue').get('fields').get('project').get('id')
    project_key = data.get('issue').get('fields').get('project').get('key')
    project_name = data.get('issue').get('fields').get('project').get('name')
    created = data.get('issue').get('fields').get('created')
    priority = data.get('issue').get('fields').get('priority').get('name')

    if not data.get('issue').get('fields').get('assignee') is None:
        assignee = data.get('issue').get('fields').get('assignee').get('emailAddress')
    else:
        assignee = ''

    updated = data.get('issue').get('fields').get('updated')
    status = data.get('issue').get('fields').get('status').get('name')
    creator_email = data.get('issue').get('fields').get('creator').get('emailAddress')
    creator_name = data.get('issue').get('fields').get('creator').get('displayName')

    add_into_worksheet = [issue_key, project_key]

    for sheet_map_column in sheet_map.api_columns.all():
        if sheet_map_column.api_column == 'Issue Id':
            add_into_worksheet.append(issue_id)
        elif sheet_map_column.api_column == 'Issue Summary':
            add_into_worksheet.append(summary)
        elif sheet_map_column.api_column == 'Priority':
            add_into_worksheet.append(priority)
        elif sheet_map_column.api_column == 'Issue Type':
            add_into_worksheet.append(issue_type)
        elif sheet_map_column.api_column == 'Created At':
            add_into_worksheet.append(created)
        elif sheet_map_column.api_column == 'Assignee':
            add_into_worksheet.append(assignee)
        elif sheet_map_column.api_column == 'Updated':
            add_into_worksheet.append(updated)
        elif sheet_map_column.api_column == 'Status':
            add_into_worksheet.append(status)
        elif sheet_map_column.api_column == 'Project Id':
            add_into_worksheet.append(project_id)
        elif sheet_map_column.api_column == 'Project Name':
            add_into_worksheet.append(project_name)
        elif sheet_map_column.api_column == 'Creator Name':
            add_into_worksheet.append(creator_name)
        elif sheet_map_column.api_column == 'Creator Email':
            add_into_worksheet.append(creator_email)

    return add_into_worksheet


# Get selected colums for create new issue action
def get_selected_columns_new_comment(data, sheet_map):

    issue_key = data.get('issue').get('key')
    comment_id = data.get('comment').get('id')
    comment = data.get('comment').get('body')
    author = data.get('comment').get('author').get('displayName')
    created_at = data.get('comment').get('created')

    add_into_worksheet = [issue_key, comment_id]

    for sheet_map_column in sheet_map.api_columns.all():
        if sheet_map_column.api_column == 'Comment':
            add_into_worksheet.append(comment)
        elif sheet_map_column.api_column == 'Created At (Comment)':
            add_into_worksheet.append(created_at)
        elif sheet_map_column.api_column == 'Comment By':
            add_into_worksheet.append(author)

    return add_into_worksheet


# Get selected colums for create new issue action
def get_selected_columns_new_project(data, sheet_map):
    project_id = data.get('project').get('id')
    project_key = data.get('project').get('key')
    name = data.get('project').get('name')
    project_lead_name = data.get('project').get('projectLead').get('displayName')
    project_lead_email = data.get('project').get('projectLead').get('emailAddress')

    add_into_worksheet = [project_id, project_key]

    for sheet_map_column in sheet_map.api_columns.all():
        if sheet_map_column.api_column == 'Project Name':
            add_into_worksheet.append(name)
        elif sheet_map_column.api_column == 'Project Lead Name':
            add_into_worksheet.append(project_lead_name)
        elif sheet_map_column.api_column == 'Project Lead Email':
            add_into_worksheet.append(project_lead_email)

    return add_into_worksheet


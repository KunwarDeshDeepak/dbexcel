from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from configurations import server_url
from .models import Connections
from sass_sheet.models import SasSActions, ApiField
from spreadsheet.models import SheetActions
from .forms import JiraTrigger, JiraAccount, Jirasetup, SSsetup, HalfDone
import json
import requests
from jira.models import AccessToken
from pydrive.auth import GoogleAuth
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import gspread
from oauth2client import client

# Create your views here.
actionStep = 0
HalfDoneFlag = 0
HalfDoneObject = {}


@login_required
def index(request):
    global HalfDoneFlag
    global HalfDoneObject
    global actionStep
    HalfDoneFlag = 0
    HalfDoneObject = {}
    actionStep = 0
    return render(request, 'dashboard/layout.htm')


def zaps(request):
    return render(request, 'dashboard/zaps.htm')


def connections(request):
    global HalfDoneFlag
    global HalfDoneObject
    global actionStep
    HalfDoneFlag = 0
    HalfDoneObject = {}
    actionStep = 0
    contexts = Connections.objects.values()
    connections_list = [entry for entry in contexts]
    context = {
        'conlist': connections_list,
    }
    return render(request, 'dashboard/connections.htm', {'context': context})


def taskhistory(request):
    return render(request, 'dashboard/taskhistory.htm')


def config(request):
    global HalfDoneObject
    formobject = get_Donesetup(request)
    context = {}

    if HalfDoneFlag == 1 and HalfDoneObject != {} and formobject != {}:
        context = {
            "halfdone": formobject
        }
        print(context)
    return render(request, 'dashboard/config.htm', {'context': context})


def selectsstrigger(request):
    contexts = SheetActions.objects.values()

    SsActionsList = [entry for entry in contexts]
    context = {
        'actions': SsActionsList
    }
    if (HalfDoneFlag == 1 and HalfDoneObject != {}):
        context = {
            'actions': SsActionsList,
            'halfdone': HalfDoneObject
        }
    return render(request, 'dashboard/selectsstrigger.htm', {'context': context})


def selectjiratrigger(request):
    contexts = SasSActions.objects.values()

    JiraActionsList = [entry for entry in contexts]
    context = {
        'actions': JiraActionsList
    }

    return render(request, 'dashboard/selectjiratrigger.htm', {'context': context})


def selectssaccount(request):
    formobject = get_sstrigger(request)
    context = {
        'trigger': formobject
    }
    return render(request, 'dashboard/selectssaccount.htm', {'context': context})


def setupssissue(request):
    global HalfDoneObject

    gauth = GoogleAuth()

    try:
        access_token = AccessToken.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return HttpResponse('<h1> No token found </h1>')

    gauth.credentials = client.Credentials.new_from_json(access_token.token)

    sheet_client = gspread.authorize(gauth.credentials)

    sheet_list = []

    for sheet in sheet_client.openall():
        obj = {
            "title": sheet.title,
            "id": sheet.id
        }
        sheet_list.append(obj)

    # list1 =[entry.title for entry in sheet_list]
    WsList = [{'name': 'Sheet1'}, {'name': 'Sheet2'}]
    formobject = get_ssaccount(request)

    context = {
        'spreadsheet': sheet_list,
        'worksheet': WsList,
        'account': formobject,
    }
    formobject = get_sstrigger(request)
    context['trigger'] = formobject

    if HalfDoneFlag == 1 and HalfDoneObject != {} and formobject != {}:
        HalfDoneObject = str(HalfDoneObject).replace('\"{', '{')
        HalfDoneObject = str(HalfDoneObject).replace('}\"', '}')
        print(HalfDoneObject)
        d = json.loads(HalfDoneObject)
        # d = json.loads()
        temp1 = ApiField.objects.values()
        temp = [entry for entry in temp1]
        checkboxforcomment = [entry for entry in temp if entry['action'] == "Create new comment"]
        checkboxforissue = [entry for entry in temp if entry['action'] == "Create new issue"]
        checkboxforproject = [entry for entry in temp if entry['action'] == "Create new project"]
        print(d['trigger']['name'])
        context['halfdone'] = d
        context['listofcheckboxes'] = {
            'checkboxforcomment': checkboxforcomment,
            'checkboxforissue': checkboxforissue,
            'checkboxforproject': checkboxforproject,
        }

    return render(request, 'dashboard/setupssissue.htm', {'context': context})


def overviewss(request):
    global actionStep
    formobject = get_sssetup(request)
    if HalfDoneObject == {}:
        actionStep = 0
    else:
        actionStep = 1
    context = {
        'ss': formobject,
        'actionStep': actionStep,
        'halfdone': HalfDoneObject
    }
    d = json.loads(str(HalfDoneObject))
    obj = str(formobject).replace('\\', '')
    obj = str(obj).replace('\'', '\"')
    obj = str(obj).replace('\"{', '{')
    obj = str(obj).replace('}\"', '}')

    f = json.loads(str(obj).replace('\'', '\"'))
    print(formobject.get('ssname'))
    postformat = {
        "app": "Jira",
        "sass_action": d['trigger']['name'],
        "sheet_action": f["accountpasser"]["trigger"]["name"],
        "sheet": formobject.get('ssname'),
        "worksheet": "Sheet1",
        "columns": f["fields"]
    }

    headers = {'Content-Type': 'application/json'}

    r = requests.post(server_url + '/sass/create_action/', data=json.dumps(postformat), headers=headers)
    print(r.content)

    return render(request, 'dashboard/overviewss.htm', {'context': context})


def selectjiraaccount(request):
    formobject = get_jiratrigger(request)
    context = {

    }
    global actionStep
    if HalfDoneObject == {}:
        actionStep = 0
    else:
        actionStep = 1
    context = {
        'trigger': formobject,
        'actionStep': actionStep,
        'halfdone': HalfDoneObject
    }
    return render(request, 'dashboard/overview.htm', {'context': context})


def setupjiraissue(request):
    JiraIssueList = [{'name': 'dbExcelpranav'}, {'name': 'dbExcel2pranav'}]
    formobject = get_jiraaccount(request)
    context = {
        'projects': JiraIssueList,
        'account': formobject
    }
    return render(request, 'dashboard/setupjiraissue.htm', {'context': context})


def overview(request):
    global actionStep
    if HalfDoneObject == {}:
        actionStep = 0
    else:
        actionStep = 1
    formobject = get_jirasetup(request)
    context = {
        'project': formobject,
        'actionStep': actionStep,
        'halfdone': HalfDoneObject
    }

    return render(request, 'dashboard/overview.htm', {'context': context})


def get_jiratrigger(request):
    if request.method == 'POST':
        form = JiraTrigger(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            detail = form.cleaned_data['detail']
    formobject = {
        'name': name,
        'detail': detail
    }
    return formobject


def get_jiraaccount(request):
    if request.method == 'POST':
        form = JiraAccount(request.POST)
        if form.is_valid():
            account = form.cleaned_data['account']
            triggerpasser = form.cleaned_data['triggerpasser']
    context = {
        'account': account,
        'triggerpasser': triggerpasser
    }
    return context


def get_jirasetup(request):
    project = ''
    accountpasser = ''
    if request.method == 'POST':
        form = Jirasetup(request.POST)
        if form.is_valid():
            project = form.cleaned_data['project']
            accountpasser = form.cleaned_data['accountpasser']
    context = {
        'project': project,
        'accountpasser': accountpasser
    }
    return context


def get_sstrigger(request):
    if request.method == 'POST':
        form = JiraTrigger(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            detail = form.cleaned_data['detail']
    formobject = {
        'name': name,
        'detail': detail
    }
    return formobject


def get_ssaccount(request):
    if request.method == 'POST':
        form = JiraAccount(request.POST)
        if form.is_valid():
            account = form.cleaned_data['account']
            triggerpasser = form.cleaned_data['triggerpasser']
    formobject = {
        'account': account,
        'triggerpasser': triggerpasser
    }
    return formobject


def get_sssetup(request):
    if request.method == 'POST':
        form = SSsetup(request.POST)
        if form.is_valid():
            ssname = form.cleaned_data['ssname']
            wsname = form.cleaned_data['wsname']
            accountpasser = form.cleaned_data['accountpasser']
            fields = request.POST.getlist('fields')
    context = {
        'ssname': ssname,
        'wsname': wsname,
        'fields': fields,
        'accountpasser': accountpasser
    }
    return context


def get_Donesetup(request):
    global HalfDoneFlag
    global HalfDoneObject
    context = {}
    halfdone = None

    if request.method == 'POST':
        HalfDoneFlag = 1
        form = HalfDone(request.POST)
        if form.is_valid():
            halfdone = form.cleaned_data['halfdone']
        else:
            HalfDoneFlag = 0

    if (HalfDoneFlag == 1) and (halfdone is not None):
        halfdone = halfdone.replace('\'', '\"')
        halfdone = halfdone.replace('\\', '')
        HalfDoneObject = halfdone
        context = halfdone
    return context

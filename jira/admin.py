from django.contrib import admin

# Register your models here.
from jira.models import JiraSetup, AccessToken
from sass_sheet.models import SasSActions, SasSSheetMap
from spreadsheet.models import SheetActions

admin.site.register(JiraSetup)
admin.site.register(AccessToken)
admin.site.register(SasSActions)
admin.site.register(SheetActions)
admin.site.register(SasSSheetMap)

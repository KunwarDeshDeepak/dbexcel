from django import forms
import json

class JiraTrigger(forms.Form):
    name = forms.CharField(max_length=100,required=False)
    detail = forms.CharField(max_length=100,required=False)

class JiraAccount(forms.Form):
    account = forms.CharField(max_length=10240,required=False)
    triggerpasser = forms.CharField(max_length=100,required=False)
    def clean_jsonfield(self):
         jdata = self.cleaned_data['account']
         try:
             json_data = json.loads(jdata) 
         except:
             raise forms.ValidationError("Invalid data in jsonfield")
         return jdata

class Jirasetup(forms.Form):
    project = forms.CharField(max_length=100,required=False)
    accountpasser = forms.CharField(max_length=10240,required=False)
    

class SSTrigger(forms.Form):
    name = forms.CharField(max_length=100,required=False)
    detail = forms.CharField(max_length=100,required=False)

class SSAccount(forms.Form):
    account = forms.CharField(max_length=10240,required=False)
    triggerpasser = forms.CharField(max_length=100,required=False)


class SSsetup(forms.Form):
    ssname = forms.CharField(max_length=100,required=False)
    wsname = forms.CharField(max_length=100,required=False)
    fields = forms.CharField(required=False)
    accountpasser = forms.CharField(max_length=10240,required=False)

class HalfDone(forms.Form):
    halfdone = forms.CharField(max_length=5000,required=False)

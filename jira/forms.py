from django import forms

from jira.models import JiraSetup


class JiraSetupForm(forms.ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput)
    url = forms.CharField(widget=forms.URLInput(attrs={'class': 'jiraForm'}))
    email = forms.CharField(widget=forms.URLInput(attrs={'class': 'jiraForm'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'jiraForm'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(JiraSetupForm, self).__init__(*args, **kwargs)

    class Meta:
        model = JiraSetup
        fields = ('url', 'email', 'password',)

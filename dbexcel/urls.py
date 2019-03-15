"""dbexcel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin, auth
from django.urls import path, include
from jira.urls import url_patterns
from sass_sheet.views import google_domain_verification
from spreadsheet.urls import url_patterns_sheet
from sass_sheet.urls import url_patterns_sass
from hiway.urls import url_patterns_hiway
from dashboard.urls import url_patterns_dashboard

urlpatterns = [
    path('googlea73117b61cc11fc2.html/', google_domain_verification),
    path('hiway/', include(url_patterns_hiway)),
    path('jira/', include(url_patterns)),
    path('sheets/', include(url_patterns_sheet)),
    path('sass/', include(url_patterns_sass)),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('dashboard/', include(url_patterns_dashboard)),
    path('', include(url_patterns_dashboard))
]

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("automation/", views.automation_dashboard, name="automation-dashboard"),
    path("automation/run/", views.run_automation_from_web, name="automation-run-web"),
    path("automation/data/", views.automation_data_api, name="automation-data-api"),
]

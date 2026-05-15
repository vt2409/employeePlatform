from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"employees", views.EmployeeViewSet, basename="employee")

urlpatterns = [
    path("", include(router.urls)),
    path("insights/country/", views.country_insights, name="insights-country"),
    path("insights/job-title/", views.job_title_insights, name="insights-job-title"),
    path("insights/department/", views.department_insights, name="insights-department"),
    path("insights/overview/", views.overview_insights, name="insights-overview"),
]

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from .factories import EmployeeFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestCountryInsights:

    def setup_method(self):
        EmployeeFactory.create_batch(3, country="India", country_code="IN", salary="1000000", currency="INR")
        EmployeeFactory.create_batch(2, country="United States", country_code="US", salary="100000", currency="USD")

    def test_returns_data_for_all_countries(self, api_client):
        response = api_client.get(reverse("insights-country"))
        assert response.status_code == 200
        country_codes = [d["country_code"] for d in response.data]
        assert "IN" in country_codes
        assert "US" in country_codes

    def test_filter_by_country_code(self, api_client):
        response = api_client.get(reverse("insights-country") + "?country_code=IN")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["country_code"] == "IN"
        assert response.data[0]["headcount"] == 3

    def test_salary_aggregates_are_correct(self, api_client):
        response = api_client.get(reverse("insights-country") + "?country_code=IN")
        data = response.data[0]
        assert float(data["min_salary"]) == 1000000.0
        assert float(data["max_salary"]) == 1000000.0
        assert float(data["avg_salary"]) == 1000000.0

    def test_excludes_inactive_employees(self, api_client):
        EmployeeFactory(country="India", country_code="IN", salary="5000000", is_active=False)
        response = api_client.get(reverse("insights-country") + "?country_code=IN")
        assert response.data[0]["headcount"] == 3


@pytest.mark.django_db
class TestJobTitleInsights:

    def test_returns_avg_salary_per_job_title(self, api_client):
        EmployeeFactory.create_batch(2, job_title="Software Engineer", country_code="IN", salary="1200000")
        EmployeeFactory(job_title="Data Analyst", country_code="IN", salary="900000")
        response = api_client.get(reverse("insights-job-title") + "?country_code=IN")
        assert response.status_code == 200
        titles = [d["job_title"] for d in response.data]
        assert "Software Engineer" in titles
        assert "Data Analyst" in titles

    def test_filter_by_job_title(self, api_client):
        EmployeeFactory.create_batch(3, job_title="Software Engineer", country_code="IN", salary="1500000")
        EmployeeFactory(job_title="HR Manager", country_code="IN", salary="800000")
        response = api_client.get(
            reverse("insights-job-title") + "?country_code=IN&job_title=Software Engineer"
        )
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["headcount"] == 3


@pytest.mark.django_db
class TestOverviewInsights:

    def test_overview_returns_correct_counts(self, api_client):
        EmployeeFactory.create_batch(5, is_active=True)
        EmployeeFactory(is_active=False)
        response = api_client.get(reverse("insights-overview"))
        assert response.status_code == 200
        assert response.data["active_employees"] == 5
        assert response.data["total_employees"] == 6

    def test_top_earners_count(self, api_client):
        EmployeeFactory.create_batch(10, is_active=True)
        response = api_client.get(reverse("insights-overview"))
        assert len(response.data["top_earners"]) <= 5

    def test_employment_type_breakdown_present(self, api_client):
        EmployeeFactory.create_batch(3, employment_type="Full-time")
        EmployeeFactory(employment_type="Contract")
        response = api_client.get(reverse("insights-overview"))
        breakdown = response.data["employment_type_breakdown"]
        assert "Full-time" in breakdown
        assert breakdown["Full-time"] == 3

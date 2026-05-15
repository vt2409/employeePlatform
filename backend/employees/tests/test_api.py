import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from employees.models import Employee
from .factories import EmployeeFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestEmployeeListCreate:

    def test_list_returns_active_employees_only(self, api_client):
        EmployeeFactory.create_batch(3, is_active=True)
        EmployeeFactory(is_active=False)
        url = reverse("employee-list")
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 3

    def test_create_employee_success(self, api_client):
        payload = {
            "full_name": "Jane Doe",
            "job_title": "Software Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "1200000.00",
            "currency": "INR",
            "employment_type": "Full-time",
            "date_joined": "2023-01-15",
        }
        url = reverse("employee-list")
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 201
        assert Employee.objects.filter(full_name="Jane Doe").exists()

    def test_create_employee_invalid_salary(self, api_client):
        payload = {
            "full_name": "Bad Salary",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "-500",
            "currency": "INR",
            "employment_type": "Full-time",
            "date_joined": "2023-01-15",
        }
        url = reverse("employee-list")
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 400
        assert "salary" in response.data

    def test_create_employee_missing_required_fields(self, api_client):
        url = reverse("employee-list")
        response = api_client.post(url, {}, format="json")
        assert response.status_code == 400

    def test_search_by_name(self, api_client):
        EmployeeFactory(full_name="Alice Smith")
        EmployeeFactory(full_name="Bob Jones")
        url = reverse("employee-list") + "?search=Alice"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["full_name"] == "Alice Smith"

    def test_filter_by_country_code(self, api_client):
        EmployeeFactory.create_batch(3, country_code="IN")
        EmployeeFactory.create_batch(2, country_code="US", country="United States", currency="USD")
        url = reverse("employee-list") + "?country_code=IN"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 3


@pytest.mark.django_db
class TestEmployeeRetrieveUpdateDelete:

    def test_retrieve_employee(self, api_client):
        emp = EmployeeFactory(full_name="Retrieve Me")
        url = reverse("employee-detail", args=[emp.id])
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["full_name"] == "Retrieve Me"

    def test_update_employee_salary(self, api_client):
        emp = EmployeeFactory(salary="1000000.00")
        url = reverse("employee-detail", args=[emp.id])
        response = api_client.patch(url, {"salary": "1500000.00"}, format="json")
        assert response.status_code == 200
        emp.refresh_from_db()
        assert float(emp.salary) == 1500000.0

    def test_soft_delete_via_api(self, api_client):
        emp = EmployeeFactory()
        url = reverse("employee-detail", args=[emp.id])
        response = api_client.delete(url)
        assert response.status_code == 200
        emp.refresh_from_db()
        assert emp.is_active is False

    def test_deleted_employee_excluded_from_list(self, api_client):
        emp = EmployeeFactory()
        emp.delete()
        url = reverse("employee-list")
        response = api_client.get(url)
        results = [r["id"] for r in response.data["results"]]
        assert str(emp.id) not in results

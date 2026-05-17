import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from employees.models import Employee, EmploymentType
from datetime import date
from decimal import Decimal
from .factories import EmployeeFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestEmployeeListCreate:
    """Test employee list and creation endpoints."""

    def test_list_returns_active_employees_only(self, api_client):
        """Verify list endpoint returns only active employees by default."""
        EmployeeFactory.create_batch(3, is_active=True)
        EmployeeFactory(is_active=False)
        url = reverse("employee-list")
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 3

    def test_list_with_active_all_parameter_includes_inactive(self, api_client):
        """Verify ?active=all returns both active and inactive employees."""
        EmployeeFactory.create_batch(2, is_active=True)
        EmployeeFactory.create_batch(2, is_active=False)
        url = reverse("employee-list") + "?active=all"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 4

    def test_list_pagination_default(self, api_client):
        """Verify pagination is applied to list endpoint."""
        EmployeeFactory.create_batch(25)
        url = reverse("employee-list")
        response = api_client.get(url)
        assert response.status_code == 200
        assert "next" in response.data
        assert "previous" in response.data
        assert len(response.data["results"]) <= 20  # Default pagination

    def test_list_returns_correct_serializer_fields(self, api_client):
        """Verify list endpoint returns EmployeeListSerializer (without timestamps)."""
        emp = EmployeeFactory(full_name="Test User")
        url = reverse("employee-list")
        response = api_client.get(url)
        assert response.status_code == 200
        data = response.data["results"][0]
        assert "full_name" in data
        assert "id" in data
        # EmployeeListSerializer should NOT include created_at/updated_at
        assert "created_at" not in data
        assert "updated_at" not in data

    def test_create_employee_success(self, api_client):
        """Verify employee creation with valid payload."""
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
        emp = Employee.objects.get(full_name="Jane Doe")
        assert emp.salary == Decimal("1200000.00")
        assert emp.is_active is True

    def test_create_employee_returns_full_serializer(self, api_client):
        """Verify create returns EmployeeSerializer (with timestamps)."""
        payload = {
            "full_name": "John Doe",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "1000000.00",
            "currency": "INR",
            "employment_type": "Full-time",
            "date_joined": "2023-01-15",
        }
        url = reverse("employee-list")
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 201
        assert "created_at" in response.data
        assert "updated_at" in response.data
        assert "id" in response.data

    def test_create_employee_with_zero_salary_fails(self, api_client):
        """Verify salary validation: zero salary is rejected."""
        payload = {
            "full_name": "Bad Salary",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "0",
            "currency": "INR",
            "employment_type": "Full-time",
            "date_joined": "2023-01-15",
        }
        url = reverse("employee-list")
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 400
        assert "salary" in response.data

    def test_create_employee_with_negative_salary_fails(self, api_client):
        """Verify salary validation: negative salary is rejected."""
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
        """Verify required field validation."""
        url = reverse("employee-list")
        response = api_client.post(url, {}, format="json")
        assert response.status_code == 400
        # Should have errors for required fields
        assert len(response.data) > 0

    def test_create_employee_missing_full_name(self, api_client):
        """Verify full_name is required."""
        payload = {
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "1000000.00",
            "currency": "INR",
            "employment_type": "Full-time",
            "date_joined": "2023-01-15",
        }
        url = reverse("employee-list")
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 400
        assert "full_name" in response.data

    def test_create_employee_missing_salary(self, api_client):
        """Verify salary is required."""
        payload = {
            "full_name": "John Doe",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "currency": "INR",
            "employment_type": "Full-time",
            "date_joined": "2023-01-15",
        }
        url = reverse("employee-list")
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 400
        assert "salary" in response.data

    def test_create_employee_invalid_employment_type(self, api_client):
        """Verify employment_type validation against allowed choices."""
        payload = {
            "full_name": "John Doe",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "1000000.00",
            "currency": "INR",
            "employment_type": "Invalid Type",
            "date_joined": "2023-01-15",
        }
        url = reverse("employee-list")
        response = api_client.post(url, payload, format="json")
        assert response.status_code == 400
        assert "employment_type" in response.data

    def test_create_employee_with_valid_employment_types(self, api_client):
        """Verify all valid employment types are accepted."""
        base_payload = {
            "full_name": "Test User",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "1000000.00",
            "currency": "INR",
            "date_joined": "2023-01-15",
        }
        url = reverse("employee-list")
        for emp_type in ["Full-time", "Part-time", "Contract"]:
            payload = base_payload.copy()
            payload["employment_type"] = emp_type
            response = api_client.post(url, payload, format="json")
            assert response.status_code == 201

    def test_search_by_full_name(self, api_client):
        """Verify search filters by full_name."""
        EmployeeFactory(full_name="Alice Smith")
        EmployeeFactory(full_name="Bob Jones")
        url = reverse("employee-list") + "?search=Alice"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["full_name"] == "Alice Smith"

    def test_search_is_case_insensitive(self, api_client):
        """Verify search is case-insensitive."""
        EmployeeFactory(full_name="Alice Smith")
        url = reverse("employee-list") + "?search=alice"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_search_by_job_title(self, api_client):
        """Verify search filters by job_title."""
        EmployeeFactory(job_title="Software Engineer")
        EmployeeFactory(job_title="Data Analyst")
        url = reverse("employee-list") + "?search=Software"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_search_by_department(self, api_client):
        """Verify search filters by department."""
        EmployeeFactory(department="Engineering")
        EmployeeFactory(department="Finance")
        url = reverse("employee-list") + "?search=Engineering"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_search_returns_no_results(self, api_client):
        """Verify search returns empty results when no match."""
        EmployeeFactory(full_name="Alice Smith")
        url = reverse("employee-list") + "?search=NonExistent"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 0

    def test_filter_by_country_code(self, api_client):
        """Verify filtering by country_code."""
        EmployeeFactory.create_batch(3, country_code="IN")
        EmployeeFactory.create_batch(2, country_code="US", country="United States", currency="USD")
        url = reverse("employee-list") + "?country_code=IN"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 3

    def test_filter_by_country_code_case_insensitive(self, api_client):
        """Verify country_code filter is case-insensitive."""
        EmployeeFactory(country_code="IN")
        url = reverse("employee-list") + "?country_code=in"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_filter_by_department(self, api_client):
        """Verify filtering by department."""
        EmployeeFactory.create_batch(3, department="Engineering")
        EmployeeFactory(department="Finance")
        url = reverse("employee-list") + "?department=Engineering"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 3

    def test_filter_by_department_case_insensitive(self, api_client):
        """Verify department filter is case-insensitive."""
        EmployeeFactory(department="Engineering")
        url = reverse("employee-list") + "?department=engineering"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_filter_by_employment_type(self, api_client):
        """Verify filtering by employment_type."""
        EmployeeFactory.create_batch(2, employment_type="Full-time")
        EmployeeFactory(employment_type="Contract")
        url = reverse("employee-list") + "?employment_type=Full-time"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 2

    def test_combine_multiple_filters(self, api_client):
        """Verify multiple filters work together (AND logic)."""
        EmployeeFactory(country_code="IN", department="Engineering")
        EmployeeFactory(country_code="IN", department="Finance")
        EmployeeFactory(country_code="US", department="Engineering")
        url = reverse("employee-list") + "?country_code=IN&department=Engineering"
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_ordering_by_full_name(self, api_client):
        """Verify ordering by full_name (default is ascending)."""
        EmployeeFactory(full_name="Charlie Brown")
        EmployeeFactory(full_name="Alice Smith")
        EmployeeFactory(full_name="Bob Jones")
        url = reverse("employee-list") + "?ordering=full_name"
        response = api_client.get(url)
        names = [r["full_name"] for r in response.data["results"]]
        assert names == ["Alice Smith", "Bob Jones", "Charlie Brown"]

    def test_ordering_by_salary_descending(self, api_client):
        """Verify ordering by salary descending."""
        EmployeeFactory(full_name="A", salary="1000000.00")
        EmployeeFactory(full_name="B", salary="2000000.00")
        EmployeeFactory(full_name="C", salary="500000.00")
        url = reverse("employee-list") + "?ordering=-salary"
        response = api_client.get(url)
        salaries = [float(r["salary"]) for r in response.data["results"]]
        assert salaries == [2000000.0, 1000000.0, 500000.0]


@pytest.mark.django_db
class TestEmployeeRetrieveUpdateDelete:
    """Test individual employee retrieval, update, and deletion."""

    def test_retrieve_employee_success(self, api_client):
        """Verify retrieving a single employee by ID."""
        emp = EmployeeFactory(full_name="Retrieve Me")
        url = reverse("employee-detail", args=[emp.id])
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["full_name"] == "Retrieve Me"
        assert "created_at" in response.data  # Full serializer with timestamps
        assert "updated_at" in response.data

    def test_retrieve_nonexistent_employee(self, api_client):
        """Verify retrieving non-existent employee returns 404."""
        import uuid
        url = reverse("employee-detail", args=[uuid.uuid4()])
        response = api_client.get(url)
        assert response.status_code == 404

    def test_retrieve_inactive_employee_returns_404(self, api_client):
        """Verify retrieving an inactive employee returns 404."""
        emp = EmployeeFactory(is_active=False)
        url = reverse("employee-detail", args=[emp.id])
        response = api_client.get(url)
        assert response.status_code == 404

    def test_full_update_employee_success(self, api_client):
        """Verify PUT (full update) of an employee."""
        emp = EmployeeFactory()
        payload = {
            "full_name": "Updated Name",
            "job_title": "New Title",
            "department": "Finance",
            "country": "USA",
            "country_code": "US",
            "salary": "2000000.00",
            "currency": "USD",
            "employment_type": "Contract",
            "date_joined": "2024-01-01",
        }
        url = reverse("employee-detail", args=[emp.id])
        response = api_client.put(url, payload, format="json")
        assert response.status_code == 200
        emp.refresh_from_db()
        assert emp.full_name == "Updated Name"
        assert emp.department == "Finance"

    def test_partial_update_employee_success(self, api_client):
        """Verify PATCH (partial update) of an employee."""
        emp = EmployeeFactory(salary="1000000.00", full_name="Original Name")
        url = reverse("employee-detail", args=[emp.id])
        response = api_client.patch(url, {"salary": "1500000.00"}, format="json")
        assert response.status_code == 200
        emp.refresh_from_db()
        assert float(emp.salary) == 1500000.0
        assert emp.full_name == "Original Name"  # Unchanged

    def test_update_employee_salary_validation(self, api_client):
        """Verify salary validation on update."""
        emp = EmployeeFactory()
        url = reverse("employee-detail", args=[emp.id])
        response = api_client.patch(url, {"salary": "-1000"}, format="json")
        assert response.status_code == 400
        assert "salary" in response.data

    def test_update_employment_type_validation(self, api_client):
        """Verify employment_type validation on update."""
        emp = EmployeeFactory()
        url = reverse("employee-detail", args=[emp.id])
        response = api_client.patch(url, {"employment_type": "Invalid"}, format="json")
        assert response.status_code == 400

    def test_soft_delete_via_delete_endpoint(self, api_client):
        """Verify DELETE performs soft delete (sets is_active=False)."""
        emp = EmployeeFactory()
        emp_id = emp.id
        url = reverse("employee-detail", args=[emp.id])
        response = api_client.delete(url)
        assert response.status_code == 200
        emp.refresh_from_db()
        assert emp.is_active is False
        # Record still exists in database
        assert Employee.objects.filter(id=emp_id).exists()

    def test_delete_returns_success_message(self, api_client):
        """Verify delete returns appropriate message."""
        emp = EmployeeFactory()
        url = reverse("employee-detail", args=[emp.id])
        response = api_client.delete(url)
        assert response.status_code == 200
        assert "detail" in response.data

    def test_deleted_employee_not_in_list(self, api_client):
        """Verify deleted employee doesn't appear in list."""
        emp = EmployeeFactory()
        emp.delete()
        url = reverse("employee-list")
        response = api_client.get(url)
        results_ids = [r["id"] for r in response.data["results"]]
        assert str(emp.id) not in results_ids

    def test_delete_already_deleted_employee(self, api_client):
        """Verify deleting an already deleted employee returns 404."""
        emp = EmployeeFactory()
        emp.delete()
        url = reverse("employee-detail", args=[emp.id])
        response = api_client.delete(url)
        assert response.status_code == 404

    def test_update_nonexistent_employee_returns_404(self, api_client):
        """Verify updating non-existent employee returns 404."""
        import uuid
        url = reverse("employee-detail", args=[uuid.uuid4()])
        response = api_client.patch(url, {"salary": "1000000"}, format="json")
        assert response.status_code == 404

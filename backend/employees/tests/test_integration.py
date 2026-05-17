import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from employees.models import Employee
from .factories import EmployeeFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestEmployeeWorkflows:
    """Test complete employee management workflows."""

    def test_full_employee_lifecycle(self, api_client):
        """Test complete workflow: create, retrieve, update, delete employee."""
        # 1. Create employee
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
        create_response = api_client.post(reverse("employee-list"), payload, format="json")
        assert create_response.status_code == 201
        employee_id = create_response.data["id"]
        
        # 2. Retrieve employee
        retrieve_response = api_client.get(reverse("employee-detail", args=[employee_id]))
        assert retrieve_response.status_code == 200
        assert retrieve_response.data["full_name"] == "Jane Doe"
        
        # 3. Update employee salary
        update_response = api_client.patch(
            reverse("employee-detail", args=[employee_id]),
            {"salary": "1500000.00"},
            format="json"
        )
        assert update_response.status_code == 200
        
        # 4. Verify update
        verify_response = api_client.get(reverse("employee-detail", args=[employee_id]))
        assert float(verify_response.data["salary"]) == 1500000.0
        
        # 5. Delete employee (soft delete)
        delete_response = api_client.delete(reverse("employee-detail", args=[employee_id]))
        assert delete_response.status_code == 200
        
        # 6. Verify employee is inactive but record exists
        emp = Employee.objects.get(id=employee_id)
        assert emp.is_active is False

    def test_bulk_employee_import_and_query(self, api_client):
        """Test importing multiple employees and querying them."""
        # Create employees from multiple countries
        countries = [
            ("India", "IN", "INR"),
            ("United States", "US", "USD"),
            ("United Kingdom", "GB", "GBP"),
        ]
        
        for country, code, currency in countries:
            for i in range(3):
                EmployeeFactory(
                    full_name=f"{country} Employee {i}",
                    country=country,
                    country_code=code,
                    currency=currency,
                    salary=f"{1000000 + i * 100000}.00"
                )
        
        # Query employees by country
        response = api_client.get(reverse("employee-list") + "?country_code=IN")
        assert response.status_code == 200
        assert response.data["count"] == 3
        
        # Verify all returned employees are from India
        for emp in response.data["results"]:
            assert emp["country_code"] == "IN"

    def test_salary_update_reflected_in_insights(self, api_client):
        """Test that employee salary updates are reflected in insights."""
        # Create employees with known salaries
        emp1 = EmployeeFactory(
            job_title="Engineer",
            country_code="IN",
            salary="1000000.00"
        )
        emp2 = EmployeeFactory(
            job_title="Engineer",
            country_code="IN",
            salary="2000000.00"
        )
        
        # Get initial insights
        initial_response = api_client.get(
            reverse("insights-job-title") + "?country_code=IN&job_title=Engineer"
        )
        initial_avg = float(initial_response.data[0]["avg_salary"])
        assert initial_avg == 1500000.0
        
        # Update one employee's salary
        api_client.patch(
            reverse("employee-detail", args=[emp1.id]),
            {"salary": "3000000.00"},
            format="json"
        )
        
        # Get updated insights
        updated_response = api_client.get(
            reverse("insights-job-title") + "?country_code=IN&job_title=Engineer"
        )
        updated_avg = float(updated_response.data[0]["avg_salary"])
        assert updated_avg == 2500000.0

    def test_soft_delete_excluded_from_insights(self, api_client):
        """Test that soft-deleted employees are excluded from all insights."""
        # Create employees
        emp1 = EmployeeFactory(country_code="IN", department="Engineering", salary="1000000.00")
        emp2 = EmployeeFactory(country_code="IN", department="Engineering", salary="2000000.00")
        
        # Get initial overview
        initial_overview = api_client.get(reverse("insights-overview"))
        initial_active = initial_overview.data["active_employees"]
        
        # Soft delete one employee
        api_client.delete(reverse("employee-detail", args=[emp1.id]))
        
        # Get updated overview
        updated_overview = api_client.get(reverse("insights-overview"))
        assert updated_overview.data["active_employees"] == initial_active - 1
        
        # Verify employee not in list
        list_response = api_client.get(reverse("employee-list"))
        emp_ids = [e["id"] for e in list_response.data["results"]]
        assert str(emp1.id) not in emp_ids

    def test_search_and_filter_combination(self, api_client):
        """Test combining search and filter parameters."""
        # Create test employees
        EmployeeFactory(
            full_name="Alice Johnson",
            job_title="Software Engineer",
            country_code="IN",
            department="Engineering"
        )
        EmployeeFactory(
            full_name="Alice Smith",
            job_title="Data Analyst",
            country_code="IN",
            department="Finance"
        )
        EmployeeFactory(
            full_name="Bob Johnson",
            job_title="Software Engineer",
            country_code="US",
            department="Engineering"
        )
        
        # Search for "Johnson" in country "IN" - should find only Alice Johnson
        response = api_client.get(
            reverse("employee-list") + "?search=Johnson&country_code=IN"
        )
        assert response.data["count"] == 1
        assert response.data["results"][0]["full_name"] == "Alice Johnson"

    def test_concurrent_employee_updates_consistency(self, api_client):
        """Test that concurrent-like updates maintain data consistency."""
        emp = EmployeeFactory(salary="1000000.00")
        
        # Make two updates in sequence
        api_client.patch(
            reverse("employee-detail", args=[emp.id]),
            {"salary": "1100000.00"},
            format="json"
        )
        
        api_client.patch(
            reverse("employee-detail", args=[emp.id]),
            {"job_title": "Senior Engineer"},
            format="json"
        )
        
        # Verify both updates are applied
        response = api_client.get(reverse("employee-detail", args=[emp.id]))
        assert float(response.data["salary"]) == 1100000.0
        assert response.data["job_title"] == "Senior Engineer"

    def test_employee_creation_with_all_valid_employment_types(self, api_client):
        """Test creating employees with all employment type variants."""
        employment_types = ["Full-time", "Part-time", "Contract"]
        base_payload = {
            "full_name": "Test",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "1000000.00",
            "currency": "INR",
            "date_joined": "2023-01-15",
        }
        
        for emp_type in employment_types:
            payload = base_payload.copy()
            payload["employment_type"] = emp_type
            payload["full_name"] = f"Employee {emp_type}"
            
            response = api_client.post(reverse("employee-list"), payload, format="json")
            assert response.status_code == 201
        
        # Verify all were created
        response = api_client.get(reverse("employee-list"))
        assert response.data["count"] == 3

    def test_department_headcount_accurate_after_modifications(self, api_client):
        """Test that department insights remain accurate after employee changes."""
        # Create initial employees
        emp1 = EmployeeFactory(department="Engineering")
        emp2 = EmployeeFactory(department="Engineering")
        emp3 = EmployeeFactory(department="Finance")
        
        # Check initial count
        response = api_client.get(reverse("insights-department"))
        eng = next(d for d in response.data if d["department"] == "Engineering")
        assert eng["headcount"] == 2
        
        # Update one employee's department
        api_client.patch(
            reverse("employee-detail", args=[emp1.id]),
            {"department": "Finance"},
            format="json"
        )
        
        # Verify updated counts
        response = api_client.get(reverse("insights-department"))
        eng = next((d for d in response.data if d["department"] == "Engineering"), None)
        fin = next(d for d in response.data if d["department"] == "Finance")
        
        # Engineering should now have 1
        if eng:
            assert eng["headcount"] == 1
        # Finance should now have 2
        assert fin["headcount"] == 2

    def test_ordering_consistency_across_pages(self, api_client):
        """Test that ordering remains consistent across paginated results."""
        # Create employees with specific names
        for i in range(25):
            EmployeeFactory(full_name=f"Employee {i:02d}")
        
        # Get first page with ordering
        page1 = api_client.get(reverse("employee-list") + "?ordering=full_name")
        page1_names = [e["full_name"] for e in page1.data["results"]]
        
        # Get second page
        page2 = api_client.get(page1.data["next"])
        page2_names = [e["full_name"] for e in page2.data["results"]]
        
        # Verify ordering continues across pages
        all_names = page1_names + page2_names
        assert all_names == sorted(all_names)

    def test_top_earners_consistency_after_salary_changes(self, api_client):
        """Test that top earners list updates correctly with salary changes."""
        # Create employees with varying salaries
        emp_low = EmployeeFactory(full_name="Low Earner", salary="500000.00")
        emp_high = EmployeeFactory(full_name="High Earner", salary="5000000.00")
        
        # Check initial top earners - High Earner should be first
        response = api_client.get(reverse("insights-overview"))
        assert response.data["top_earners"][0]["full_name"] == "High Earner"
        
        # Update low earner to have highest salary
        api_client.patch(
            reverse("employee-detail", args=[emp_low.id]),
            {"salary": "10000000.00"},
            format="json"
        )
        
        # Verify updated top earners - Low Earner should now be first
        response = api_client.get(reverse("insights-overview"))
        assert response.data["top_earners"][0]["full_name"] == "Low Earner"
        assert float(response.data["top_earners"][0]["salary"]) == 10000000.0

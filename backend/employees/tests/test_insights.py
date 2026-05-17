import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from decimal import Decimal
from .factories import EmployeeFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestCountryInsights:
    """Test country-level salary insights endpoint."""

    def setup_method(self):
        """Setup test data with multiple countries."""
        EmployeeFactory.create_batch(3, country="India", country_code="IN", salary="1000000", currency="INR")
        EmployeeFactory.create_batch(2, country="United States", country_code="US", salary="100000", currency="USD")

    def test_returns_data_for_all_countries(self, api_client):
        """Verify endpoint returns data for all countries."""
        response = api_client.get(reverse("insights-country"))
        assert response.status_code == 200
        country_codes = [d["country_code"] for d in response.data]
        assert "IN" in country_codes
        assert "US" in country_codes

    def test_returns_correct_fields(self, api_client):
        """Verify response includes all required insight fields."""
        response = api_client.get(reverse("insights-country"))
        assert response.status_code == 200
        data = response.data[0]
        required_fields = ["country", "country_code", "currency", "headcount", "min_salary", "max_salary", "avg_salary"]
        for field in required_fields:
            assert field in data

    def test_filter_by_country_code(self, api_client):
        """Verify filtering by country_code parameter."""
        response = api_client.get(reverse("insights-country") + "?country_code=IN")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["country_code"] == "IN"
        assert response.data[0]["headcount"] == 3

    def test_filter_by_country_code_case_insensitive(self, api_client):
        """Verify country_code filter is case-insensitive."""
        response = api_client.get(reverse("insights-country") + "?country_code=in")
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_salary_aggregates_are_correct(self, api_client):
        """Verify salary min/max/avg aggregations are correct."""
        response = api_client.get(reverse("insights-country") + "?country_code=IN")
        data = response.data[0]
        assert float(data["min_salary"]) == 1000000.0
        assert float(data["max_salary"]) == 1000000.0
        assert float(data["avg_salary"]) == 1000000.0

    def test_headcount_is_correct(self, api_client):
        """Verify headcount calculation is correct."""
        response = api_client.get(reverse("insights-country") + "?country_code=IN")
        assert response.data[0]["headcount"] == 3
        
        response = api_client.get(reverse("insights-country") + "?country_code=US")
        assert response.data[0]["headcount"] == 2

    def test_salary_aggregates_with_varied_salaries(self, api_client):
        """Verify aggregations work correctly with different salary values."""
        EmployeeFactory(country="UK", country_code="GB", salary="500000", currency="GBP")
        EmployeeFactory(country="UK", country_code="GB", salary="1000000", currency="GBP")
        EmployeeFactory(country="UK", country_code="GB", salary="1500000", currency="GBP")
        
        response = api_client.get(reverse("insights-country") + "?country_code=GB")
        data = response.data[0]
        
        assert float(data["min_salary"]) == 500000.0
        assert float(data["max_salary"]) == 1500000.0
        assert float(data["avg_salary"]) == 1000000.0

    def test_excludes_inactive_employees(self, api_client):
        """Verify inactive employees are excluded from insights."""
        EmployeeFactory(country="India", country_code="IN", salary="5000000", is_active=False)
        response = api_client.get(reverse("insights-country") + "?country_code=IN")
        # Should still be 3 (inactive not counted)
        assert response.data[0]["headcount"] == 3

    def test_currency_is_included(self, api_client):
        """Verify currency information is included in response."""
        response = api_client.get(reverse("insights-country"))
        for country_data in response.data:
            assert "currency" in country_data
            assert country_data["currency"] in ["INR", "USD"]

    def test_ordering_by_country(self, api_client):
        """Verify results are ordered by country name."""
        response = api_client.get(reverse("insights-country"))
        countries = [d["country"] for d in response.data]
        assert countries == sorted(countries)

    def test_nonexistent_country_code_returns_empty(self, api_client):
        """Verify querying non-existent country_code returns empty."""
        response = api_client.get(reverse("insights-country") + "?country_code=XX")
        assert response.status_code == 200
        assert len(response.data) == 0


@pytest.mark.django_db
class TestJobTitleInsights:
    """Test job title-level salary insights endpoint."""

    def test_returns_avg_salary_per_job_title(self, api_client):
        """Verify endpoint returns average salary per job title."""
        EmployeeFactory.create_batch(2, job_title="Software Engineer", country_code="IN", salary="1200000")
        EmployeeFactory(job_title="Data Analyst", country_code="IN", salary="900000")
        response = api_client.get(reverse("insights-job-title") + "?country_code=IN")
        assert response.status_code == 200
        titles = [d["job_title"] for d in response.data]
        assert "Software Engineer" in titles
        assert "Data Analyst" in titles

    def test_returns_correct_fields(self, api_client):
        """Verify response includes all required fields."""
        EmployeeFactory(job_title="Engineer", country_code="IN")
        response = api_client.get(reverse("insights-job-title") + "?country_code=IN")
        assert response.status_code == 200
        data = response.data[0]
        required_fields = ["job_title", "country", "country_code", "headcount", "avg_salary"]
        for field in required_fields:
            assert field in data

    def test_filter_by_country_code(self, api_client):
        """Verify filtering by country_code parameter."""
        EmployeeFactory(job_title="Engineer", country_code="IN", salary="1200000")
        EmployeeFactory(job_title="Engineer", country_code="US", salary="200000")
        response = api_client.get(reverse("insights-job-title") + "?country_code=IN")
        assert response.status_code == 200
        for item in response.data:
            assert item["country_code"] == "IN"

    def test_filter_by_job_title(self, api_client):
        """Verify filtering by job_title parameter."""
        EmployeeFactory.create_batch(3, job_title="Software Engineer", country_code="IN", salary="1500000")
        EmployeeFactory(job_title="HR Manager", country_code="IN", salary="800000")
        response = api_client.get(
            reverse("insights-job-title") + "?country_code=IN&job_title=Software Engineer"
        )
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["headcount"] == 3
        assert response.data[0]["job_title"] == "Software Engineer"

    def test_filter_by_job_title_case_insensitive(self, api_client):
        """Verify job_title filter is case-insensitive."""
        EmployeeFactory(job_title="Software Engineer", country_code="IN")
        response = api_client.get(
            reverse("insights-job-title") + "?country_code=IN&job_title=software engineer"
        )
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_avg_salary_calculation(self, api_client):
        """Verify average salary calculation is correct."""
        EmployeeFactory.create_batch(2, job_title="Engineer", country_code="IN", salary="1000000")
        EmployeeFactory(job_title="Engineer", country_code="IN", salary="2000000")
        response = api_client.get(
            reverse("insights-job-title") + "?country_code=IN&job_title=Engineer"
        )
        data = response.data[0]
        assert float(data["avg_salary"]) == 1333333.33  # (1000000 + 1000000 + 2000000) / 3

    def test_headcount_per_job_title(self, api_client):
        """Verify headcount is calculated correctly per job title."""
        EmployeeFactory.create_batch(3, job_title="Engineer", country_code="IN")
        EmployeeFactory.create_batch(2, job_title="Manager", country_code="IN")
        response = api_client.get(reverse("insights-job-title") + "?country_code=IN")
        
        engineer_data = next(d for d in response.data if d["job_title"] == "Engineer")
        manager_data = next(d for d in response.data if d["job_title"] == "Manager")
        
        assert engineer_data["headcount"] == 3
        assert manager_data["headcount"] == 2

    def test_excludes_inactive_employees(self, api_client):
        """Verify inactive employees are excluded."""
        EmployeeFactory.create_batch(2, job_title="Engineer", country_code="IN")
        EmployeeFactory(job_title="Engineer", country_code="IN", is_active=False)
        response = api_client.get(
            reverse("insights-job-title") + "?country_code=IN&job_title=Engineer"
        )
        assert response.data[0]["headcount"] == 2

    def test_ordering_by_country_and_title(self, api_client):
        """Verify results are ordered by country and then job title."""
        EmployeeFactory(job_title="Data Analyst", country_code="US", country="USA")
        EmployeeFactory(job_title="Software Engineer", country_code="US", country="USA")
        EmployeeFactory(job_title="HR Manager", country_code="IN", country="India")
        
        response = api_client.get(reverse("insights-job-title"))
        # Results should be ordered by country then job title
        prev_country = None
        prev_title = None
        for item in response.data:
            if prev_country and item["country"] == prev_country:
                assert item["job_title"] >= prev_title
            prev_country = item["country"]
            prev_title = item["job_title"]

    def test_nonexistent_job_title_returns_empty(self, api_client):
        """Verify querying non-existent job_title returns empty."""
        EmployeeFactory(job_title="Engineer", country_code="IN")
        response = api_client.get(
            reverse("insights-job-title") + "?country_code=IN&job_title=NonExistent"
        )
        assert response.status_code == 200
        assert len(response.data) == 0


@pytest.mark.django_db
class TestDepartmentInsights:
    """Test department-level insights endpoint."""

    def test_returns_department_insights(self, api_client):
        """Verify endpoint returns department insights."""
        EmployeeFactory.create_batch(5, department="Engineering", salary="1500000")
        EmployeeFactory.create_batch(3, department="Finance", salary="1000000")
        response = api_client.get(reverse("insights-department"))
        assert response.status_code == 200
        departments = [d["department"] for d in response.data]
        assert "Engineering" in departments
        assert "Finance" in departments

    def test_returns_correct_fields(self, api_client):
        """Verify response includes all required fields."""
        EmployeeFactory(department="Engineering")
        response = api_client.get(reverse("insights-department"))
        assert response.status_code == 200
        data = response.data[0]
        required_fields = ["department", "headcount", "avg_salary", "total_payroll"]
        for field in required_fields:
            assert field in data

    def test_headcount_calculation(self, api_client):
        """Verify headcount is calculated correctly."""
        EmployeeFactory.create_batch(5, department="Engineering")
        EmployeeFactory.create_batch(3, department="Finance")
        response = api_client.get(reverse("insights-department"))
        
        eng = next(d for d in response.data if d["department"] == "Engineering")
        fin = next(d for d in response.data if d["department"] == "Finance")
        
        assert eng["headcount"] == 5
        assert fin["headcount"] == 3

    def test_avg_salary_per_department(self, api_client):
        """Verify average salary is calculated per department."""
        EmployeeFactory.create_batch(2, department="Engineering", salary="1000000")
        EmployeeFactory(department="Engineering", salary="2000000")
        response = api_client.get(reverse("insights-department"))
        
        eng = next(d for d in response.data if d["department"] == "Engineering")
        assert float(eng["avg_salary"]) == 1333333.33

    def test_total_payroll_calculation(self, api_client):
        """Verify total payroll is calculated correctly."""
        EmployeeFactory.create_batch(2, department="Engineering", salary="1000000")
        EmployeeFactory(department="Engineering", salary="2000000")
        response = api_client.get(reverse("insights-department"))
        
        eng = next(d for d in response.data if d["department"] == "Engineering")
        assert float(eng["total_payroll"]) == 4000000.0

    def test_excludes_inactive_employees(self, api_client):
        """Verify inactive employees are excluded from calculations."""
        EmployeeFactory.create_batch(2, department="Engineering")
        EmployeeFactory(department="Engineering", is_active=False)
        response = api_client.get(reverse("insights-department"))
        
        eng = next(d for d in response.data if d["department"] == "Engineering")
        assert eng["headcount"] == 2

    def test_ordering_by_total_payroll_descending(self, api_client):
        """Verify results are ordered by total_payroll descending."""
        EmployeeFactory.create_batch(2, department="Finance", salary="1000000")  # 2M total
        EmployeeFactory.create_batch(5, department="Engineering", salary="1000000")  # 5M total
        EmployeeFactory(department="HR", salary="1000000")  # 1M total
        
        response = api_client.get(reverse("insights-department"))
        payrolls = [float(d["total_payroll"]) for d in response.data]
        assert payrolls == sorted(payrolls, reverse=True)


@pytest.mark.django_db
class TestOverviewInsights:
    """Test organization overview insights endpoint."""

    def test_overview_returns_correct_counts(self, api_client):
        """Verify overview returns correct employee counts."""
        EmployeeFactory.create_batch(5, is_active=True)
        EmployeeFactory(is_active=False)
        response = api_client.get(reverse("insights-overview"))
        assert response.status_code == 200
        assert response.data["active_employees"] == 5
        assert response.data["total_employees"] == 6

    def test_overview_returns_correct_fields(self, api_client):
        """Verify overview response includes all required fields."""
        EmployeeFactory()
        response = api_client.get(reverse("insights-overview"))
        assert response.status_code == 200
        required_fields = [
            "total_employees", "active_employees", "total_countries",
            "total_departments", "top_earners", "employment_type_breakdown"
        ]
        for field in required_fields:
            assert field in response.data

    def test_total_countries_count(self, api_client):
        """Verify total_countries calculation is correct."""
        EmployeeFactory.create_batch(2, country_code="IN")
        EmployeeFactory.create_batch(2, country_code="US")
        EmployeeFactory(country_code="GB")
        response = api_client.get(reverse("insights-overview"))
        assert response.data["total_countries"] == 3

    def test_total_departments_count(self, api_client):
        """Verify total_departments calculation is correct."""
        EmployeeFactory.create_batch(2, department="Engineering")
        EmployeeFactory.create_batch(2, department="Finance")
        EmployeeFactory(department="HR")
        response = api_client.get(reverse("insights-overview"))
        assert response.data["total_departments"] == 3

    def test_top_earners_limit(self, api_client):
        """Verify top_earners list is limited to 5."""
        EmployeeFactory.create_batch(10, is_active=True)
        response = api_client.get(reverse("insights-overview"))
        assert len(response.data["top_earners"]) <= 5

    def test_top_earners_are_ordered_by_salary(self, api_client):
        """Verify top_earners are sorted by salary descending."""
        EmployeeFactory(full_name="A", salary="1000000", is_active=True)
        EmployeeFactory(full_name="B", salary="5000000", is_active=True)
        EmployeeFactory(full_name="C", salary="3000000", is_active=True)
        response = api_client.get(reverse("insights-overview"))
        salaries = [float(e["salary"]) for e in response.data["top_earners"]]
        assert salaries == sorted(salaries, reverse=True)

    def test_employment_type_breakdown_present(self, api_client):
        """Verify employment_type_breakdown is present and correct."""
        EmployeeFactory.create_batch(3, employment_type="Full-time")
        EmployeeFactory(employment_type="Contract")
        response = api_client.get(reverse("insights-overview"))
        breakdown = response.data["employment_type_breakdown"]
        assert "Full-time" in breakdown
        assert breakdown["Full-time"] == 3
        assert breakdown["Contract"] == 1

    def test_employment_type_breakdown_only_active(self, api_client):
        """Verify employment_type_breakdown only counts active employees."""
        EmployeeFactory.create_batch(2, employment_type="Full-time", is_active=True)
        EmployeeFactory(employment_type="Full-time", is_active=False)
        response = api_client.get(reverse("insights-overview"))
        breakdown = response.data["employment_type_breakdown"]
        assert breakdown["Full-time"] == 2

    def test_top_earners_only_active(self, api_client):
        """Verify top_earners only includes active employees."""
        EmployeeFactory(salary="5000000", is_active=True)
        EmployeeFactory(salary="10000000", is_active=False)  # Inactive, higher salary
        response = api_client.get(reverse("insights-overview"))
        top_earner = response.data["top_earners"][0]
        # Should be the active one with 5M
        assert float(top_earner["salary"]) == 5000000.0

    def test_total_countries_and_departments_only_active(self, api_client):
        """Verify country and department counts only include active employees."""
        EmployeeFactory(country_code="IN", department="Engineering", is_active=True)
        EmployeeFactory(country_code="US", department="Finance", is_active=False)
        response = api_client.get(reverse("insights-overview"))
        # Should only count active employees
        assert response.data["total_countries"] == 1
        assert response.data["total_departments"] == 1


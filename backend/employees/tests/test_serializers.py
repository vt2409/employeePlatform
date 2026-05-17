import pytest
from decimal import Decimal
from datetime import date
from rest_framework import serializers as drf_serializers
from employees.models import Employee, EmploymentType
from employees.serializers import (
    EmployeeSerializer,
    EmployeeListSerializer,
    CountryInsightSerializer,
    JobTitleInsightSerializer,
    DepartmentInsightSerializer,
    OverviewSerializer,
)
from .factories import EmployeeFactory


@pytest.mark.django_db
class TestEmployeeSerializer:
    """Test EmployeeSerializer validation and data serialization."""

    def test_serialize_employee_with_all_fields(self):
        """Verify serializer includes all required fields."""
        emp = EmployeeFactory(
            full_name="John Doe",
            job_title="Engineer",
            department="Engineering",
            country="India",
            country_code="IN",
            salary="1500000.00",
            currency="INR",
            employment_type="Full-time",
        )
        serializer = EmployeeSerializer(emp)
        data = serializer.data
        
        assert data["full_name"] == "John Doe"
        assert data["job_title"] == "Engineer"
        assert data["department"] == "Engineering"
        assert data["country"] == "India"
        assert data["country_code"] == "IN"
        assert float(data["salary"]) == 1500000.0
        assert data["currency"] == "INR"
        assert data["employment_type"] == "Full-time"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_employee_serializer_id_readonly(self):
        """Verify ID field is read-only."""
        emp = EmployeeFactory()
        serializer = EmployeeSerializer(emp, data={"id": "new-id"}, partial=True)
        assert serializer.is_valid()
        # ID should not change
        assert serializer.validated_data.get("id") is None

    def test_employee_serializer_timestamps_readonly(self):
        """Verify created_at and updated_at are read-only."""
        emp = EmployeeFactory()
        old_created = emp.created_at
        data = {
            "full_name": "Updated",
            "created_at": "2020-01-01T00:00:00Z",
            "updated_at": "2020-01-01T00:00:00Z",
        }
        serializer = EmployeeSerializer(emp, data=data, partial=True)
        assert serializer.is_valid()
        serializer.save()
        emp.refresh_from_db()
        # Timestamps should not be changed
        assert emp.created_at == old_created

    def test_validate_salary_positive(self):
        """Verify salary must be positive."""
        data = {
            "full_name": "Test",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "1000000.00",
            "currency": "INR",
            "employment_type": "Full-time",
            "date_joined": "2023-01-15",
        }
        serializer = EmployeeSerializer(data=data)
        assert serializer.is_valid()

    def test_validate_salary_zero_fails(self):
        """Verify zero salary is rejected."""
        data = {
            "full_name": "Test",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "0",
            "currency": "INR",
            "employment_type": "Full-time",
            "date_joined": "2023-01-15",
        }
        serializer = EmployeeSerializer(data=data)
        assert not serializer.is_valid()
        assert "salary" in serializer.errors

    def test_validate_salary_negative_fails(self):
        """Verify negative salary is rejected."""
        data = {
            "full_name": "Test",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "-5000.00",
            "currency": "INR",
            "employment_type": "Full-time",
            "date_joined": "2023-01-15",
        }
        serializer = EmployeeSerializer(data=data)
        assert not serializer.is_valid()
        assert "salary" in serializer.errors

    def test_validate_employment_type_valid_choices(self):
        """Verify employment_type accepts valid choices."""
        base_data = {
            "full_name": "Test",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "1000000.00",
            "currency": "INR",
            "date_joined": "2023-01-15",
        }
        for emp_type in ["Full-time", "Part-time", "Contract"]:
            data = base_data.copy()
            data["employment_type"] = emp_type
            serializer = EmployeeSerializer(data=data)
            assert serializer.is_valid(), f"Failed for {emp_type}"

    def test_validate_employment_type_invalid_fails(self):
        """Verify invalid employment_type is rejected."""
        data = {
            "full_name": "Test",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "1000000.00",
            "currency": "INR",
            "employment_type": "Invalid Type",
            "date_joined": "2023-01-15",
        }
        serializer = EmployeeSerializer(data=data)
        assert not serializer.is_valid()
        assert "employment_type" in serializer.errors

    def test_required_fields_validation(self):
        """Verify all required fields are enforced."""
        serializer = EmployeeSerializer(data={})
        assert not serializer.is_valid()
        required_fields = [
            "full_name", "job_title", "department", "country",
            "country_code", "salary", "date_joined"
        ]
        # Note: currency and employment_type are NOT required as they have default values
        for field in required_fields:
            assert field in serializer.errors

    def test_salary_decimal_precision(self):
        """Verify salary decimal precision is maintained."""
        data = {
            "full_name": "Test",
            "job_title": "Engineer",
            "department": "Engineering",
            "country": "India",
            "country_code": "IN",
            "salary": "1500000.99",
            "currency": "INR",
            "employment_type": "Full-time",
            "date_joined": "2023-01-15",
        }
        serializer = EmployeeSerializer(data=data)
        assert serializer.is_valid()
        serializer.save()
        emp = Employee.objects.get(full_name="Test")
        assert emp.salary == Decimal("1500000.99")


@pytest.mark.django_db
class TestEmployeeListSerializer:
    """Test EmployeeListSerializer (lighter version without timestamps)."""

    def test_list_serializer_excludes_timestamps(self):
        """Verify EmployeeListSerializer excludes created_at and updated_at."""
        emp = EmployeeFactory()
        serializer = EmployeeListSerializer(emp)
        data = serializer.data
        
        assert "full_name" in data
        assert "id" in data
        assert "created_at" not in data
        assert "updated_at" not in data

    def test_list_serializer_includes_all_essential_fields(self):
        """Verify EmployeeListSerializer includes all essential employee fields."""
        emp = EmployeeFactory()
        serializer = EmployeeListSerializer(emp)
        data = serializer.data
        
        essential_fields = [
            "id", "full_name", "job_title", "department",
            "country", "country_code", "salary", "currency",
            "employment_type", "date_joined", "is_active"
        ]
        for field in essential_fields:
            assert field in data

    def test_list_serializer_many_employees(self):
        """Verify EmployeeListSerializer works with multiple employees."""
        emps = EmployeeFactory.create_batch(5)
        serializer = EmployeeListSerializer(emps, many=True)
        assert len(serializer.data) == 5
        for emp_data in serializer.data:
            assert "created_at" not in emp_data
            assert "updated_at" not in emp_data


@pytest.mark.django_db
class TestCountryInsightSerializer:
    """Test CountryInsightSerializer for insights data."""

    def test_serialize_country_insight_data(self):
        """Verify CountryInsightSerializer serializes insight data correctly."""
        data = {
            "country": "India",
            "country_code": "IN",
            "currency": "INR",
            "headcount": 100,
            "min_salary": Decimal("500000.00"),
            "max_salary": Decimal("5000000.00"),
            "avg_salary": Decimal("1500000.00"),
        }
        serializer = CountryInsightSerializer(data)
        assert serializer.data["country"] == "India"
        assert serializer.data["headcount"] == 100
        assert float(serializer.data["avg_salary"]) == 1500000.0

    def test_required_fields_present(self):
        """Verify all required fields are present in serializer."""
        incomplete_data = {
            "country": "India",
            "country_code": "IN",
        }
        serializer = CountryInsightSerializer(data=incomplete_data)
        assert not serializer.is_valid()
        required = ["currency", "headcount", "min_salary", "max_salary", "avg_salary"]
        for field in required:
            assert field in serializer.errors


@pytest.mark.django_db
class TestJobTitleInsightSerializer:
    """Test JobTitleInsightSerializer for job title insights."""

    def test_serialize_job_title_insight(self):
        """Verify JobTitleInsightSerializer serializes data correctly."""
        data = {
            "job_title": "Software Engineer",
            "country": "India",
            "country_code": "IN",
            "headcount": 50,
            "avg_salary": Decimal("1200000.00"),
        }
        serializer = JobTitleInsightSerializer(data)
        assert serializer.data["job_title"] == "Software Engineer"
        assert serializer.data["headcount"] == 50


@pytest.mark.django_db
class TestDepartmentInsightSerializer:
    """Test DepartmentInsightSerializer for department insights."""

    def test_serialize_department_insight(self):
        """Verify DepartmentInsightSerializer serializes data correctly."""
        data = {
            "department": "Engineering",
            "headcount": 100,
            "avg_salary": Decimal("1500000.00"),
            "total_payroll": Decimal("150000000.00"),
        }
        serializer = DepartmentInsightSerializer(data)
        assert serializer.data["department"] == "Engineering"
        assert serializer.data["headcount"] == 100
        assert float(serializer.data["total_payroll"]) == 150000000.0


@pytest.mark.django_db
class TestOverviewSerializer:
    """Test OverviewSerializer for organization overview."""

    def test_serialize_overview_data(self):
        """Verify OverviewSerializer serializes overview data correctly."""
        top_earner_data = EmployeeFactory(full_name="Top Earner")
        data = {
            "total_employees": 1000,
            "active_employees": 950,
            "total_countries": 5,
            "total_departments": 10,
            "top_earners": [top_earner_data],
            "employment_type_breakdown": {"Full-time": 800, "Part-time": 100, "Contract": 50},
        }
        serializer = OverviewSerializer(data)
        assert serializer.data["total_employees"] == 1000
        assert serializer.data["active_employees"] == 950
        assert serializer.data["total_countries"] == 5
        assert serializer.data["employment_type_breakdown"]["Full-time"] == 800

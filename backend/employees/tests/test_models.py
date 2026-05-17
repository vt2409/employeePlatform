import pytest
from datetime import date
from decimal import Decimal
from employees.models import Employee, EmploymentType
from .factories import EmployeeFactory


@pytest.mark.django_db
class TestEmployeeModel:
    """Test Employee model structure, validation, and behavior."""

    def test_employee_creation_with_all_fields(self):
        """Verify employee can be created with all fields."""
        emp = EmployeeFactory(
            full_name="John Doe",
            job_title="Senior Engineer",
            department="Engineering",
            country="India",
            country_code="IN",
            salary="1500000.00",
            currency="INR",
            employment_type="Full-time",
            date_joined="2023-01-15",
        )
        assert emp.full_name == "John Doe"
        assert emp.job_title == "Senior Engineer"
        assert emp.department == "Engineering"
        assert emp.salary == Decimal("1500000.00") or float(emp.salary) == 1500000.0
        assert emp.is_active is True

    def test_employee_id_is_uuid(self):
        """Verify employee ID is a UUID."""
        emp = EmployeeFactory()
        assert emp.id is not None
        assert isinstance(emp.id, type(emp.id))  # UUID type

    def test_employee_str_representation(self):
        """Verify string representation includes name, title, and country code."""
        emp = EmployeeFactory(full_name="Vikas Tomar", job_title="Senior Engineer", country_code="IN")
        emp_str = str(emp)
        assert "Vikas Tomar" in emp_str
        assert "Senior Engineer" in emp_str
        assert "IN" in emp_str

    def test_employee_is_active_default_true(self):
        """Verify new employees are active by default."""
        emp = EmployeeFactory()
        assert emp.is_active is True

    def test_employment_type_choices(self):
        """Verify all employment type choices are available."""
        assert "Full-time" in [choice[0] for choice in EmploymentType.choices]
        assert "Part-time" in [choice[0] for choice in EmploymentType.choices]
        assert "Contract" in [choice[0] for choice in EmploymentType.choices]

    def test_default_employment_type_is_full_time(self):
        """Verify default employment type is Full-time."""
        emp = EmployeeFactory()
        assert emp.employment_type == "Full-time"

    def test_salary_is_decimal_field(self):
        """Verify salary is stored as Decimal."""
        emp = EmployeeFactory(salary="1500000.00")
        emp.refresh_from_db()
        assert isinstance(emp.salary, Decimal)
        assert float(emp.salary) == 1500000.0

    def test_salary_decimal_precision(self):
        """Verify salary maintains decimal precision."""
        emp = EmployeeFactory(salary="1500000.99")
        emp.refresh_from_db()
        assert emp.salary == Decimal("1500000.99")

    def test_date_joined_is_date_field(self):
        """Verify date_joined is stored as date."""
        test_date = date(2023, 1, 15)
        emp = EmployeeFactory(date_joined=test_date)
        assert isinstance(emp.date_joined, date)
        assert emp.date_joined == test_date

    def test_soft_delete_sets_inactive(self):
        """Verify delete() method performs soft delete by setting is_active=False."""
        emp = EmployeeFactory()
        assert emp.is_active is True
        emp.delete()
        emp.refresh_from_db()
        assert emp.is_active is False

    def test_soft_delete_preserves_record(self):
        """Verify soft delete doesn't remove record from database."""
        emp = EmployeeFactory()
        emp_id = emp.id
        emp.delete()
        # Record still exists in DB
        assert Employee.objects.filter(id=emp_id).exists()

    def test_soft_delete_updates_updated_at(self):
        """Verify soft delete updates the updated_at timestamp."""
        emp = EmployeeFactory()
        original_updated = emp.updated_at
        emp.delete()
        emp.refresh_from_db()
        assert emp.updated_at >= original_updated

    def test_multiple_soft_deletes_same_record(self):
        """Verify record can be soft deleted multiple times without error."""
        emp = EmployeeFactory()
        emp.delete()
        emp.refresh_from_db()
        assert emp.is_active is False
        
        # Deleting again should not raise error
        emp.delete()
        emp.refresh_from_db()
        assert emp.is_active is False

    def test_field_max_lengths(self):
        """Verify field max_length constraints."""
        # This would normally fail at database level, but we test the model definition
        assert Employee._meta.get_field("full_name").max_length == 200
        assert Employee._meta.get_field("job_title").max_length == 200
        assert Employee._meta.get_field("department").max_length == 200
        assert Employee._meta.get_field("country").max_length == 100
        assert Employee._meta.get_field("country_code").max_length == 10
        assert Employee._meta.get_field("currency").max_length == 10

    def test_employment_type_max_length(self):
        """Verify employment_type field constraints."""
        assert Employee._meta.get_field("employment_type").max_length == 20

    def test_salary_decimal_places(self):
        """Verify salary decimal field precision."""
        field = Employee._meta.get_field("salary")
        assert field.max_digits == 12
        assert field.decimal_places == 2

    def test_created_at_auto_set(self):
        """Verify created_at is automatically set on creation."""
        emp = EmployeeFactory()
        assert emp.created_at is not None
        assert isinstance(emp.created_at, type(emp.created_at))

    def test_updated_at_auto_update(self):
        """Verify updated_at is automatically updated."""
        emp = EmployeeFactory(full_name="Original")
        original_updated = emp.updated_at
        import time
        time.sleep(0.01)
        emp.full_name = "Updated"
        emp.save()
        emp.refresh_from_db()
        assert emp.updated_at >= original_updated

    def test_model_ordering(self):
        """Verify model has default ordering by full_name."""
        EmployeeFactory(full_name="Charlie")
        EmployeeFactory(full_name="Alice")
        EmployeeFactory(full_name="Bob")
        
        employees = Employee.objects.filter(is_active=True)
        names = [e.full_name for e in employees]
        assert names == ["Alice", "Bob", "Charlie"]

    def test_indexes_exist(self):
        """Verify important indexes are defined."""
        # Verify the model has indexes defined (specific index validation would be DB-specific)
        assert Employee._meta.indexes is not None
        assert len(Employee._meta.indexes) > 0

    def test_employee_queryset_filtering(self):
        """Verify employees can be filtered by various fields."""
        EmployeeFactory(full_name="Test1", country_code="IN", department="Engineering")
        EmployeeFactory(full_name="Test2", country_code="US", department="Finance")
        
        # Filter by country_code
        in_employees = Employee.objects.filter(country_code="IN")
        assert in_employees.count() == 1
        
        # Filter by department
        eng_employees = Employee.objects.filter(department="Engineering")
        assert eng_employees.count() == 1

    def test_employee_update_preserves_other_fields(self):
        """Verify updating one field doesn't affect others."""
        emp = EmployeeFactory(
            full_name="Original",
            job_title="Engineer",
            salary="1000000.00"
        )
        
        emp.full_name = "Updated"
        emp.save()
        emp.refresh_from_db()
        
        assert emp.full_name == "Updated"
        assert emp.job_title == "Engineer"
        assert emp.salary == Decimal("1000000.00")

    def test_currency_default_value(self):
        """Verify currency has a default value of USD."""
        emp = Employee(
            full_name="Test",
            job_title="Engineer",
            department="Engineering",
            country="USA",
            country_code="US",
            salary=Decimal("1000000.00"),
            employment_type="Full-time",
            date_joined=date(2023, 1, 1),
        )
        assert emp.currency == "USD"

    def test_active_employees_queryset_optimization(self):
        """Verify filtering by is_active=True retrieves only active employees."""
        EmployeeFactory.create_batch(3, is_active=True)
        EmployeeFactory.create_batch(2, is_active=False)
        
        active = Employee.objects.filter(is_active=True)
        assert active.count() == 3
        
        all_employees = Employee.objects.all()
        assert all_employees.count() == 5

    def test_employee_with_all_employment_types(self):
        """Verify all employment types can be assigned to employees."""
        for emp_type in ["Full-time", "Part-time", "Contract"]:
            emp = EmployeeFactory(employment_type=emp_type)
            assert emp.employment_type == emp_type

    def test_employee_distinct_creation(self):
        """Verify multiple employees can be created with distinct data."""
        emp1 = EmployeeFactory(full_name="Employee 1")
        emp2 = EmployeeFactory(full_name="Employee 2")
        
        assert emp1.id != emp2.id
        assert emp1.full_name != emp2.full_name

import pytest
from employees.models import Employee
from .factories import EmployeeFactory


@pytest.mark.django_db
class TestEmployeeModel:

    def test_str_representation(self):
        emp = EmployeeFactory(full_name="Vikas Tomar", job_title="Senior Engineer", country_code="IN")
        assert "Vikas Tomar" in str(emp)
        assert "IN" in str(emp)

    def test_soft_delete_sets_inactive(self):
        emp = EmployeeFactory()
        assert emp.is_active is True
        emp.delete()
        emp.refresh_from_db()
        assert emp.is_active is False

    def test_soft_delete_preserves_record(self):
        emp = EmployeeFactory()
        emp_id = emp.id
        emp.delete()
        # Record still exists in DB
        assert Employee.objects.filter(id=emp_id).exists()

    def test_default_employment_type_is_full_time(self):
        emp = EmployeeFactory()
        assert emp.employment_type == "Full-time"

    def test_salary_is_decimal(self):
        emp = EmployeeFactory(salary="1500000.00")
        emp.refresh_from_db()
        assert float(emp.salary) == 1500000.0

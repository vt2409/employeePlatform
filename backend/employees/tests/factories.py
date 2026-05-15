import factory
import factory.fuzzy
from datetime import date
from decimal import Decimal

from employees.models import Employee, EmploymentType


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    full_name = factory.Sequence(lambda n: f"Employee {n}")
    job_title = factory.fuzzy.FuzzyChoice(["Software Engineer", "Product Manager", "Data Analyst"])
    department = factory.fuzzy.FuzzyChoice(["Engineering", "Product", "Finance", "HR"])
    country = "India"
    country_code = "IN"
    salary = factory.fuzzy.FuzzyDecimal(500000, 4000000, precision=2)
    currency = "INR"
    employment_type = EmploymentType.FULL_TIME
    date_joined = factory.fuzzy.FuzzyDate(date(2018, 1, 1))
    is_active = True

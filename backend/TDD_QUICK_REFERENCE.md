# TDD Quick Reference Guide

Quick start guide for writing tests in the Salary Management project.

## Quick Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest employees/tests/test_api.py

# Run with coverage
pytest --cov=employees

# Run tests matching a pattern
pytest -k "test_filter"

# Run with verbose output
pytest -v

# Run single test
pytest employees/tests/test_api.py::TestEmployeeListCreate::test_list_returns_active_employees_only
```

## Test Template

```python
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from employees.models import Employee
from .factories import EmployeeFactory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestFeatureName:
    """Describe what this test class covers."""
    
    def setup_method(self):
        """Run before each test - setup shared data."""
        self.emp = EmployeeFactory(full_name="Test User")
    
    def test_descriptive_name_of_behavior(self, api_client):
        """Test one specific behavior."""
        # 1. Arrange - set up test data
        payload = {"salary": "1500000.00"}
        
        # 2. Act - perform the action
        response = api_client.patch(
            reverse("employee-detail", args=[self.emp.id]),
            payload,
            format="json"
        )
        
        # 3. Assert - verify the result
        assert response.status_code == 200
        self.emp.refresh_from_db()
        assert self.emp.salary == Decimal("1500000.00")
```

## Common Test Patterns

### API Endpoint Test
```python
def test_create_employee_success(self, api_client):
    """Verify employee creation returns 201 and creates record."""
    payload = {
        "full_name": "Jane Doe",
        "job_title": "Engineer",
        "department": "Engineering",
        "country": "India",
        "country_code": "IN",
        "salary": "1200000.00",
        "currency": "INR",
        "employment_type": "Full-time",
        "date_joined": "2023-01-15",
    }
    response = api_client.post(reverse("employee-list"), payload, format="json")
    assert response.status_code == 201
    assert Employee.objects.filter(full_name="Jane Doe").exists()
```

### Validation Test
```python
def test_negative_salary_fails(self, api_client):
    """Verify negative salary is rejected."""
    payload = {
        "full_name": "Test",
        "job_title": "Engineer",
        "department": "Engineering",
        "country": "India",
        "country_code": "IN",
        "salary": "-1000",  # Invalid
        "currency": "INR",
        "employment_type": "Full-time",
        "date_joined": "2023-01-15",
    }
    response = api_client.post(reverse("employee-list"), payload, format="json")
    assert response.status_code == 400
    assert "salary" in response.data
```

### Filtering Test
```python
def test_filter_by_country_code(self, api_client):
    """Verify country_code filter works."""
    EmployeeFactory.create_batch(3, country_code="IN")
    EmployeeFactory.create_batch(2, country_code="US")
    
    response = api_client.get(reverse("employee-list") + "?country_code=IN")
    assert response.status_code == 200
    assert response.data["count"] == 3
```

### Model Test
```python
def test_soft_delete_sets_inactive(self):
    """Verify delete() sets is_active=False."""
    emp = EmployeeFactory()
    emp.delete()
    emp.refresh_from_db()
    assert emp.is_active is False
```

### Update Test
```python
def test_partial_update(self, api_client):
    """Verify PATCH updates only specified fields."""
    emp = EmployeeFactory(salary="1000000.00", full_name="Original")
    
    response = api_client.patch(
        reverse("employee-detail", args=[emp.id]),
        {"salary": "1500000.00"},
        format="json"
    )
    
    assert response.status_code == 200
    emp.refresh_from_db()
    assert float(emp.salary) == 1500000.0
    assert emp.full_name == "Original"  # Unchanged
```

## Important Decorators

```python
@pytest.mark.django_db          # Allows database access
@pytest.fixture                 # Creates reusable test data
@pytest.mark.slow              # Mark slow tests
@pytest.mark.integration       # Mark integration tests
```

## Important Fixtures

```python
# Available in conftest.py:
api_client        # REST API client
authenticated_client  # Authenticated client (future use)
reset_sequences   # Resets factory sequences
```

## Important Factories

```python
from employees.tests.factories import EmployeeFactory

# Single employee with defaults
emp = EmployeeFactory()

# With custom values
emp = EmployeeFactory(full_name="John", country_code="IN")

# Multiple employees
emps = EmployeeFactory.create_batch(5)

# Multiple with specific values
emps = EmployeeFactory.create_batch(3, country_code="IN")
```

## Assertions Cheatsheet

```python
# Status codes
assert response.status_code == 200
assert response.status_code == 201
assert response.status_code == 400
assert response.status_code == 404

# Response data
assert "field_name" in response.data
assert response.data["count"] == 3
assert len(response.data["results"]) == 5

# Database
assert Employee.objects.filter(name="Test").exists()
assert Employee.objects.count() == 10
emp.refresh_from_db()  # Reload from DB

# Values
assert emp.salary == Decimal("1500000.00")
assert float(emp.salary) == 1500000.0
assert emp.is_active is True
assert emp.full_name == "John"

# Collections
assert "text" in list_of_items
assert all(e["country"] == "IN" for e in employees)
```

## Naming Convention

**Good test names answer 3 questions:**
1. What is being tested?
2. What is the condition/scenario?
3. What is the expected outcome?

✅ **Good examples:**
- `test_create_employee_with_negative_salary_fails`
- `test_filter_by_country_code_returns_matching_employees`
- `test_soft_delete_excludes_employee_from_list`
- `test_search_is_case_insensitive`

❌ **Bad examples:**
- `test_employee` (too vague)
- `test_it_works` (meaningless)
- `test_1` (no description)

## Tips for Writing Good Tests

1. **One assertion per logical concept**
   ```python
   # OK - tests related aspects of same operation
   assert response.status_code == 201
   assert emp.full_name == "Jane"
   ```

2. **Use descriptive variable names**
   ```python
   # Good
   high_salary_employee = EmployeeFactory(salary="5000000.00")
   
   # Bad
   e = EmployeeFactory(salary="5000000.00")
   ```

3. **Test behavior, not implementation**
   ```python
   # Good - tests the behavior
   assert response.data["count"] == 3
   
   # Bad - tests the implementation
   assert len(response.data["results"]) == 3  # Brittle to pagination changes
   ```

4. **Setup once, use many times**
   ```python
   def setup_method(self):
       """Setup runs before EACH test."""
       self.emp = EmployeeFactory()
       self.client = APIClient()
   ```

5. **Use factories for flexibility**
   ```python
   # Good - clear intent
   EmployeeFactory.create_batch(3, country_code="IN")
   
   # Bad - brittle
   for i in range(3):
       Employee.objects.create(full_name=f"Emp{i}", country_code="IN", ...)
   ```

## Common Issues & Solutions

### Issue: Test passes locally but fails in CI
**Solution:** Tests must not depend on order or external state
```python
# Bad - depends on test order
def test_1_create():
    emp = EmployeeFactory()

def test_2_list():
    # Expects test_1 to have run first!
    response = api_client.get(reverse("employee-list"))
    assert response.data["count"] == 1

# Good - independent tests
def test_create(self, api_client):
    response = api_client.post(reverse("employee-list"), payload)
    assert response.status_code == 201

def test_list(self, api_client):
    EmployeeFactory()  # Create fresh data
    response = api_client.get(reverse("employee-list"))
    assert response.data["count"] >= 1
```

### Issue: Test data not persisting
**Solution:** Use `@pytest.mark.django_db` decorator
```python
@pytest.mark.django_db  # ← Don't forget this!
def test_employee_creation(self):
    emp = EmployeeFactory()  # This will work now
    assert Employee.objects.filter(id=emp.id).exists()
```

### Issue: Decimal comparison failing
**Solution:** Convert to float for comparison
```python
emp.refresh_from_db()
assert float(emp.salary) == 1500000.0  # ← Convert to float
# or
assert emp.salary == Decimal("1500000.00")
```

## Resources

- **Full Guide**: [TDD_GUIDE.md](./TDD_GUIDE.md)
- **Pytest Docs**: https://docs.pytest.org/
- **Factory Boy**: https://factoryboy.readthedocs.io/
- **DRF Testing**: https://www.django-rest-framework.org/api-guide/testing/

## When to Write Tests

✅ **Always write tests for:**
- New features
- Bug fixes
- Public APIs
- Business logic
- Data validation

✅ **Write when**:
- Before fixing a bug (show it fails first)
- Before adding a feature (write tests first!)
- When refactoring (safety net)

## Test Execution Tips

```bash
# Run with timing information
pytest --durations=10

# Run and stop on first failure
pytest -x

# Run failed tests from last run
pytest --lf

# Run specific tests by name pattern
pytest -k "salary"

# Run with detailed output
pytest -vv

# Run tests in random order (pytest-random-order)
pytest --random-order
```

---

**Last Updated**: May 2026  
**Coverage**: 95%  
**Test Count**: 130+

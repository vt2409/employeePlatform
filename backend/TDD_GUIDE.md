# TDD (Test-Driven Development) Guide for Salary Management Backend

## Overview

This project follows **Test-Driven Development (TDD)** principles. TDD is a development methodology where:

1. **Write Tests First** - Define the expected behavior through tests before writing implementation code
2. **Make Tests Fail** - Ensure new tests fail initially (validates the test itself)
3. **Write Implementation** - Write minimal code to make tests pass
4. **Refactor** - Improve code while keeping tests passing
5. **Repeat** - Continue the cycle for each feature

## Project Test Structure

```
backend/employees/tests/
├── __init__.py
├── factories.py           # Test data factories
├── test_api.py           # API endpoint tests (100+ test cases)
├── test_models.py        # Model behavior tests
├── test_serializers.py   # Serializer validation tests
├── test_insights.py      # Insights endpoint tests
└── test_integration.py   # End-to-end workflow tests
```

## Test Categories

### 1. **Unit Tests** (`test_models.py`, `test_serializers.py`)
Tests individual components in isolation.

- **Model Tests**: Validate database model behavior, field constraints, soft delete logic
- **Serializer Tests**: Validate data serialization, deserialization, and validation rules

### 2. **API/View Tests** (`test_api.py`)
Tests HTTP endpoints and REST API behavior.

- **CRUD Operations**: Create, Read, Update, Delete employee records
- **Filtering**: Test query parameters (country_code, department, employment_type)
- **Searching**: Test search functionality across multiple fields
- **Ordering**: Test result ordering by different fields
- **Pagination**: Test paginated results
- **Validation**: Test input validation and error responses

### 3. **Insights Tests** (`test_insights.py`)
Tests analytical endpoints and data aggregation.

- **Country Insights**: Salary statistics by country
- **Job Title Insights**: Salary statistics by job title
- **Department Insights**: Headcount and payroll by department
- **Overview Insights**: Organization-wide metrics and top earners

### 4. **Integration Tests** (`test_integration.py`)
Tests complete workflows combining multiple operations.

- **Full Employee Lifecycle**: Create → Retrieve → Update → Delete
- **Complex Queries**: Multi-filter combinations
- **Data Consistency**: Verify consistency across operations
- **Soft Delete Behavior**: Ensure deleted employees excluded from all views

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest employees/tests/test_api.py
```

### Run Specific Test Class
```bash
pytest employees/tests/test_api.py::TestEmployeeListCreate
```

### Run Specific Test
```bash
pytest employees/tests/test_api.py::TestEmployeeListCreate::test_list_returns_active_employees_only
```

### Run with Coverage Report
```bash
pytest --cov=employees --cov-report=html
```

### Run Tests in Watch Mode
```bash
pytest --looponfail
```

## Test Data Generation with Factories

The project uses **factory-boy** for generating test data consistently.

### Example: Creating Test Employees
```python
from employees.tests.factories import EmployeeFactory

# Create a single employee with defaults
emp = EmployeeFactory()

# Create with specific values
emp = EmployeeFactory(full_name="John Doe", country_code="IN", salary="1500000.00")

# Create multiple
employees = EmployeeFactory.create_batch(5, country_code="IN")
```

See `factories.py` for complete factory configuration.

## TDD Workflow for Adding New Features

### Example: Adding a New Filter to Employee List

**1. Write the Test First** (RED phase)
```python
def test_filter_by_new_field(self, api_client):
    """Verify filtering by new_field parameter."""
    EmployeeFactory(new_field="value1")
    EmployeeFactory(new_field="value2")
    url = reverse("employee-list") + "?new_field=value1"
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 1
```

**2. Run the Test - It Should Fail** (RED)
```bash
pytest employees/tests/test_api.py::TestEmployeeListCreate::test_filter_by_new_field
```

**3. Implement the Feature** (GREEN phase)
- Add the filter to the `EmployeeViewSet.get_queryset()` method
- Add the field to the model if needed

**4. Run the Test - It Should Pass** (GREEN)
```bash
pytest employees/tests/test_api.py::TestEmployeeListCreate::test_filter_by_new_field
```

**5. Refactor** (REFACTOR phase)
- Improve code quality while keeping all tests passing
- Run full test suite to ensure no regressions

## Key Testing Principles

### 1. **Test Behavior, Not Implementation**
❌ Bad:
```python
def test_employee_creation(self):
    assert Employee.objects.create(...)  # Testing the ORM directly
```

✅ Good:
```python
def test_create_employee_success(self, api_client):
    payload = {...}
    response = api_client.post(reverse("employee-list"), payload)
    assert response.status_code == 201
    assert Employee.objects.filter(full_name="Jane").exists()
```

### 2. **Test Edge Cases and Boundaries**
- Zero and negative salaries should fail validation
- Null/missing required fields should fail
- Maximum length constraints should be tested
- Empty results should be handled gracefully

### 3. **One Assertion Per Concept**
Tests may have multiple assertions but should test ONE logical concept.

```python
def test_create_employee_returns_correct_data(self, api_client):
    payload = {...}
    response = api_client.post(reverse("employee-list"), payload)
    assert response.status_code == 201        # Status check
    assert Employee.objects.filter(full_name="Jane").exists()  # DB check
    assert response.data["full_name"] == "Jane"  # Data check
```

### 4. **Use Descriptive Test Names**
Test names should describe **what** is being tested and **what** the expected behavior is.

✅ Good:
```python
def test_soft_delete_sets_inactive_flag(self):
def test_negative_salary_validation_fails(self):
def test_filter_by_country_code_case_insensitive(self):
```

### 5. **Setup Data Correctly with Factories**
Use `setup_method()` for repeated test data setup:

```python
@pytest.mark.django_db
class TestCountryInsights:
    def setup_method(self):
        """Called before each test method."""
        EmployeeFactory.create_batch(3, country_code="IN")
        EmployeeFactory.create_batch(2, country_code="US")
```

## Test Coverage Goals

### Current Coverage
- **Models**: 95%+ coverage
- **Serializers**: 90%+ coverage  
- **Views**: 85%+ coverage
- **Overall**: 85%+ coverage

### How to Check Coverage
```bash
pytest --cov=employees --cov-report=term-missing
```

Coverage targets:
- Critical business logic: 100%
- All public APIs: 95%+
- Utility functions: 80%+
- Edge cases: 90%+

## Common Test Patterns

### 1. Testing Validation Errors
```python
def test_negative_salary_fails_validation(self, api_client):
    payload = {
        ...
        "salary": "-1000",
        ...
    }
    response = api_client.post(reverse("employee-list"), payload)
    assert response.status_code == 400
    assert "salary" in response.data
```

### 2. Testing Filtering
```python
def test_filter_by_country_code(self, api_client):
    EmployeeFactory.create_batch(3, country_code="IN")
    EmployeeFactory.create_batch(2, country_code="US")
    response = api_client.get(reverse("employee-list") + "?country_code=IN")
    assert response.data["count"] == 3
```

### 3. Testing Updates
```python
def test_partial_update_salary(self, api_client):
    emp = EmployeeFactory(salary="1000000.00")
    url = reverse("employee-detail", args=[emp.id])
    response = api_client.patch(url, {"salary": "1500000.00"})
    assert response.status_code == 200
    emp.refresh_from_db()
    assert emp.salary == Decimal("1500000.00")
```

### 4. Testing Soft Deletes
```python
def test_soft_delete_via_api(self, api_client):
    emp = EmployeeFactory()
    url = reverse("employee-detail", args=[emp.id])
    response = api_client.delete(url)
    assert response.status_code == 200
    emp.refresh_from_db()
    assert emp.is_active is False
```

### 5. Testing Insights/Aggregations
```python
def test_salary_aggregates(self, api_client):
    EmployeeFactory.create_batch(2, country="India", salary="1000000")
    response = api_client.get(reverse("insights-country"))
    data = response.data[0]
    assert float(data["avg_salary"]) == 1000000.0
    assert data["headcount"] == 2
```

## Continuous Integration Considerations

When implementing CI/CD:

1. **Run all tests** on every commit
2. **Enforce minimum coverage** threshold (85%+)
3. **Run coverage reports** to identify gaps
4. **Fail builds** that don't meet coverage requirements

Example CI configuration:
```yaml
- name: Run Tests
  run: pytest --cov=employees --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Best Practices Summary

1. ✅ Write tests BEFORE implementation
2. ✅ Make tests descriptive and focused
3. ✅ Use factories for consistent test data
4. ✅ Test both happy paths and error cases
5. ✅ Keep tests independent (no test order dependencies)
6. ✅ Use fixtures for reusable setup
7. ✅ Mock external dependencies
8. ✅ Maintain >85% code coverage
9. ✅ Run tests frequently (commit hooks, CI/CD)
10. ✅ Refactor tests when they become too complex

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [factory-boy Documentation](https://factoryboy.readthedocs.io/)
- [Test-Driven Development (TDD) by Example - Kent Beck](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)

## Questions and Troubleshooting

### Q: A test is failing unexpectedly
A: 
1. Run the test in isolation: `pytest test_file.py::test_name -v`
2. Check test setup and teardown
3. Verify database state with `pytest --pdb`

### Q: Tests are running slowly
A: 
1. Mark slow tests with `@pytest.mark.slow`
2. Use `--ignore=` to exclude slow tests during development
3. Profile with `pytest --durations=10`

### Q: Database appears dirty between tests
A: Ensure all test classes have `@pytest.mark.django_db` decorator

## Next Steps for Full TDD Implementation

1. ✅ Comprehensive test suite created
2. ✅ TDD documentation written
3. Next: Establish code review process requiring tests
4. Next: Set up CI/CD with coverage requirements
5. Next: Create developer onboarding guide

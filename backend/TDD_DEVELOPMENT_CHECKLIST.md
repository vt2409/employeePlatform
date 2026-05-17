# TDD Development Checklist

Use this checklist when adding new features or fixing bugs in TDD style.

## Before You Start

- [ ] Create a new branch for your feature/bugfix
- [ ] Read the existing test patterns in the relevant test file
- [ ] Understand the feature requirements
- [ ] Check if similar functionality already exists

## Step 1: Write Tests (RED)

### For API Features
- [ ] Write test for successful operation
- [ ] Write test for validation failures
- [ ] Write test for edge cases
- [ ] Write test for filtering/searching if applicable
- [ ] Write test for pagination if applicable
- [ ] Write test for error responses

**Checklist:**
```python
def test_feature_success(self, api_client):
    """Test successful case."""
    # FAILS - test doesn't exist yet! ✓

def test_feature_validation_fails(self, api_client):
    """Test validation."""
    # FAILS - validation doesn't exist yet! ✓

def test_feature_edge_case(self, api_client):
    """Test edge case."""
    # FAILS - not implemented! ✓
```

### For Model Features
- [ ] Write test for model creation
- [ ] Write test for field validation
- [ ] Write test for default values
- [ ] Write test for relationships/methods

### For Business Logic
- [ ] Write test for correct calculation
- [ ] Write test for boundary conditions
- [ ] Write test for error handling

## Step 2: Run Tests (Verify RED)

```bash
pytest employees/tests/test_api.py::TestYourFeature -v
```

- [ ] Tests FAIL (This is good! Proves test works)
- [ ] Failures are clear and make sense
- [ ] All 3+ tests fail initially

**Expected Output:**
```
FAILED test_feature_success - Not Implemented
FAILED test_feature_validation_fails - Not Implemented
FAILED test_feature_edge_case - Not Implemented
```

## Step 3: Implement Code (GREEN)

### Write Minimal Code
- [ ] Write ONLY code needed to pass tests
- [ ] Don't over-engineer
- [ ] Don't add unused features
- [ ] Keep it simple

### Implementation Checklist
- [ ] Add feature to appropriate model/view/serializer
- [ ] Add necessary fields/methods
- [ ] Add validation if needed
- [ ] Add filtering/searching if needed

### Common Implementation Tasks
- [ ] Update serializer if needed
- [ ] Update view logic
- [ ] Update queryset filters
- [ ] Add model methods if needed
- [ ] Update URLs if new endpoint

## Step 4: Run Tests (Verify GREEN)

```bash
pytest employees/tests/test_api.py::TestYourFeature -v
```

- [ ] All new tests PASS ✓
- [ ] No existing tests broken
- [ ] Code coverage shows implementation tested

**Expected Output:**
```
PASSED test_feature_success
PASSED test_feature_validation_fails
PASSED test_feature_edge_case
```

## Step 5: Run Full Test Suite

```bash
pytest
```

- [ ] All 130+ tests pass
- [ ] No regressions introduced
- [ ] Coverage still above 85%

**Expected Output:**
```
130 passed in 2.73s
```

## Step 6: Refactor (REFACTOR)

### Code Quality
- [ ] Code is readable and clear
- [ ] No code duplication (DRY)
- [ ] Appropriate abstraction level
- [ ] Proper error messages

### Test Quality
- [ ] Tests have descriptive names
- [ ] No test duplication
- [ ] Proper setup/teardown
- [ ] Clear assertions

### Performance
- [ ] No unnecessary database queries
- [ ] Efficient filters and aggregations
- [ ] Reasonable test execution time

### Safety Net Verification
```bash
pytest
```

- [ ] All tests still pass after refactoring
- [ ] No functionality changed
- [ ] Coverage maintained or improved

## Step 7: Code Review Checklist

Before submitting PR, verify:

- [ ] All new code has tests
- [ ] All tests pass locally
- [ ] Code coverage >= 85%
- [ ] Tests follow project patterns
- [ ] Code follows PEP8
- [ ] Commit messages are clear
- [ ] Documentation updated if needed
- [ ] No debug code left

## Common Mistakes to Avoid

### ❌ Don't:
- [ ] Write all code first, then tests
- [ ] Skip tests for "simple" features
- [ ] Write tests that depend on test order
- [ ] Have tests with side effects on others
- [ ] Mock when you should test real behavior
- [ ] Test implementation details instead of behavior
- [ ] Forget `@pytest.mark.django_db` on model tests
- [ ] Use hardcoded test data instead of factories
- [ ] Write overly complex test setup

### ✅ Do:
- [ ] Write tests before implementation
- [ ] Write tests for all new features
- [ ] Keep tests independent
- [ ] Test behavior, not implementation
- [ ] Use factories for consistent data
- [ ] Keep tests simple and focused
- [ ] Use descriptive assertion messages
- [ ] Group related tests in classes
- [ ] Refactor tests like production code

## Feature Addition Example

### Scenario: Add "hire_date" validation

**Step 1: Write Tests**
```python
def test_hire_date_cannot_be_future(self, api_client):
    """Verify hire_date in future is rejected."""
    from datetime import datetime, timedelta
    future_date = (datetime.now() + timedelta(days=1)).date()
    payload = {..., "date_joined": str(future_date)}
    response = api_client.post(reverse("employee-list"), payload)
    assert response.status_code == 400
    assert "date_joined" in response.data

def test_hire_date_in_past_accepted(self, api_client):
    """Verify hire_date in past is accepted."""
    payload = {..., "date_joined": "2020-01-01"}
    response = api_client.post(reverse("employee-list"), payload)
    assert response.status_code == 201
```

**Step 2: Run Tests (Should FAIL)**
```bash
pytest employees/tests/test_api.py::TestEmployeeListCreate::test_hire_date_cannot_be_future -v
# FAILED - validation doesn't exist
```

**Step 3: Implement**
```python
# In serializers.py
def validate_date_joined(self, value):
    from django.utils import timezone
    if value > timezone.now().date():
        raise serializers.ValidationError("Hire date cannot be in the future.")
    return value
```

**Step 4: Run Tests (Should PASS)**
```bash
pytest employees/tests/test_api.py::TestEmployeeListCreate::test_hire_date_cannot_be_future -v
# PASSED ✓
pytest  # All 130+ tests pass ✓
```

**Step 5: Code Review & Merge**

## Test Template to Copy

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
class TestNewFeature:
    """Test new feature behavior."""
    
    def test_new_feature_success(self, api_client):
        """Verify feature works correctly."""
        # Arrange
        payload = {...}
        
        # Act
        response = api_client.post(reverse("endpoint"), payload)
        
        # Assert
        assert response.status_code == 201
        assert Employee.objects.filter(...).exists()
    
    def test_new_feature_validation_fails(self, api_client):
        """Verify validation works."""
        payload = {...invalid...}
        response = api_client.post(reverse("endpoint"), payload)
        assert response.status_code == 400
        assert "field" in response.data
    
    def test_new_feature_edge_case(self, api_client):
        """Verify edge case handling."""
        # Test edge case
        assert ...
```

## Daily TDD Workflow

**Morning:**
1. Review failing tests for feature you're implementing
2. Write new tests for next small behavior
3. Implement to make tests pass
4. Run full suite - ensure nothing broken

**During Development:**
```bash
# Watch tests (if using pytest-watch)
ptw

# Or run frequently
pytest -q
```

**Before Committing:**
```bash
# Final verification
pytest -q  # All pass
pytest --cov=employees  # Coverage OK
```

**Before PR Submission:**
```bash
# Final checklist
pytest -v  # Verbose - ensure clear
flake8 employees/  # Code style
```

## Useful Commands

```bash
# Only run tests you just modified
pytest -k "new_feature"

# Run with coverage
pytest --cov=employees --cov-report=html

# Run and show slowest tests
pytest --durations=10

# Run in parallel (if installed)
pytest -n auto

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Run with full traceback
pytest -vv --tb=long

# Run specific test
pytest employees/tests/test_api.py::TestClass::test_name -v
```

## Questions?

- **How do I test X?** → Check existing similar tests
- **What fixture do I use?** → See conftest.py
- **How do I create test data?** → Use EmployeeFactory
- **Test failing unexpectedly?** → Run with `-vv --tb=short`
- **Need authentication tests?** → Use authenticated_client fixture
- **Slow tests?** → Check for unnecessary database hits

---

**Remember:** Tests are documentation. Write them clearly for future developers.

**Coverage Goal:** 85%+  
**Test Execution:** < 5 seconds  
**Quality:** All tests passing on every commit

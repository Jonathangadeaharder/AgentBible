# Python Testing

## Framework: pytest

Install: `uv add --dev pytest pytest-cov pytest-mock`

## Test Structure

```
tests/
├── unit/
│   ├── test_models.py
│   └── test_utils.py
├── integration/
│   └── test_api.py
└── conftest.py
```

- Files: `test_*.py` or `*_test.py`
- Functions: `test_*`
- Classes: `Test*`

## Basic Test

```python
def test_deposit_increases_balance():
    account = BankAccount(100.0)
    account.deposit(50.0)
    assert account.balance == 150.0
```

## Fixtures

```python
@pytest.fixture
def sample_account():
    return BankAccount(1000.0)

def test_withdraw_success(sample_account):
    assert sample_account.withdraw(100.0) is True
    assert sample_account.balance == 900.0
```

## Parametrized Tests

```python
@pytest.mark.parametrize("amount,expected", [
    (100, 200), (50, 150), (0, 100),
])
def test_deposit_various(amount, expected):
    account = BankAccount(100.0)
    account.deposit(amount)
    assert account.balance == expected
```

## Mocking

```python
from unittest.mock import Mock, patch

@patch('mypackage.external_api.call_service')
def test_with_mock(mock_api):
    mock_api.return_value = {'status': 'ok'}
    result = my_function()
    mock_api.assert_called_once()
```

## Test Length Rules

- **Max 10 LOC** per unit test
- Up to 20 LOC with comment: `# Extended test: [reason]`

## Timeouts

| Type | Timeout |
|------|---------|
| Unit | 1s |
| Integration | 5s |
| E2E | 30s |

```python
@pytest.mark.timeout(1)
def test_fast(): ...
```

## Coverage

```bash
pytest --cov=mypackage --cov-branch --cov-fail-under=90 --cov-report=term-missing
```

## pyproject.toml Config

```toml
[tool.pytest.ini_options]
addopts = "--cov=mypackage --cov-branch --cov-fail-under=90 --cov-report=term-missing"
markers = ["slow", "integration", "e2e"]
```

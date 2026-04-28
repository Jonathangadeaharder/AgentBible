# Testing Principles and Standards

Quality testing ensures code reliability, maintainability, and confidence.

## Test Complexity = Design Problem

Complex test setup means the **code** needs refactoring, not the test.

| Red Flag | Meaning |
|----------|---------|
| >5 mocks | God Object anti-pattern |
| >15 lines setup | Tight coupling |
| Brittle tests | Coupled to implementation, not behavior |
| External dependencies in unit tests | Should be integration tests |

**Fix**: Refactor code to be more testable. Extract responsibilities, simplify interfaces.

## Test Pyramid

| Layer | Distribution | Speed | Purpose |
|-------|-------------|-------|---------|
| Unit | 70-80% | ms | Fast, isolated, precise, cheap |
| Integration | 15-25% | seconds | Test interactions |
| E2E | 5-10% | minutes | Critical paths only |

**Healthy Ratio**: 30:6:1 (Unit:Integration:E2E)

**Red Flags**: More integration than unit → tight coupling. More E2E than integration → missing coverage.

## Coverage Thresholds

- **Line Coverage**: ≥ 80%
- **Branch Coverage**: ≥ 70%

## Test Naming

Format: `MethodName_Scenario_ExpectedBehavior`

```
// Good
ProcessPayment_WhenInsufficientFunds_ReturnsInsufficientFundsError()
CreateOrder_WithEmptyCart_ThrowsInvalidOperationException()

// Bad
Test1()
TestPayment()
ProcessPayment_Success()
```

## Test Length

- **Ideal**: 10 lines
- **Max**: 20 lines (with comment explaining why)

## Test Independence

Tests must not share state or depend on execution order. Verify with randomized and parallel execution.

| Symptom | Cause | Fix |
|---------|-------|-----|
| Passes alone, fails in suite | Shared state | Use SetUp/TearDown |
| Flaky in CI | Timing issues | Add proper async/await |
| Fails after specific test | Not cleaned | Use transactions |

## AAA Structure

Every test follows Arrange-Act-Assert:

```
// Arrange
var userId = 123;

// Act
var result = _service.GetUser(userId);

// Assert
Assert.That(result.Name, Is.EqualTo("John Doe"));
```

## Mocking Guidelines

**When to mock**: External services, slow operations, non-deterministic behavior (time, random).
**When NOT to mock**: Value objects, DTOs, your own domain models.

| Mock Count | Verdict |
|-----------|---------|
| 3 | Good |
| 5 | Warning |
| 7+ | Refactor the code |

## Anti-Patterns

- **Testing function existence** — compiler already checks this
- **Testing without context** — `expect(validateSpy).toHaveBeenCalled()` → test the outcome instead
- **Testing implementation details** — `expect(service._privateMethod()).toBe(5)` → test public behavior

## What to Test vs Skip

| Test | Skip |
|------|------|
| Business logic | Framework code |
| Edge cases/boundaries | Third-party libraries |
| Error handling paths | Trivial getters/setters |
| Integration points | Constants |

## Flaky Tests: Zero Tolerance

**Common causes**: `Thread.Sleep`, shared state, external dependencies, non-deterministic data (`DateTime.Now`, `Random`).

**Solutions**: Proper async/await, isolate test data, mock externals, use fixed test data.

## Key Takeaways

- Hard to test = hard to maintain. Fix the code, not the test.
- Follow the pyramid: 70-80% unit, 15-25% integration, 5-10% E2E.
- Tests must run in any order — no shared state.
- Name tests clearly: `MethodName_Scenario_Expected`.
- 10 lines ideal, 20 max with justification.
- Zero flaky tests — fix immediately or delete.
- Few powerful tests beat many weak ones.

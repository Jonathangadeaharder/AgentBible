# C# Testing

## Framework: xUnit + Moq

```bash
dotnet add package xunit
dotnet add package xunit.runner.visualstudio
dotnet add package Moq
```

## Unit Test Example

```csharp
using Xunit;
using Moq;

public class UserServiceTests
{
    [Fact(Timeout = 60000)]
    public void GetUserById_WhenExists_ReturnsUser()
    {
        // Arrange
        var mock = new Mock<IUserRepository>();
        mock.Setup(r => r.GetById(1)).Returns(new User { Name = "John" });

        // Act
        var result = new UserService(mock.Object).GetUserById(1);

        // Assert
        Assert.Equal("John", result.Name);
    }
}
```

## Integration Test

```csharp
[Collection("DatabaseCollection")]
public class UserRepositoryTests
{
    [Fact(Timeout = 300000)]
    public async Task GetById_ReturnsUserFromDatabase()
    {
        var userId = await _fixture.CreateTestUserAsync("Jane");
        var user = await _repo.GetById(userId);
        Assert.Equal("Jane", user.Name);
    }
}
```

## Best Practices

1. AAA pattern (Arrange, Act, Assert)
2. Descriptive names: `MethodName_State_ExpectedBehavior`
3. One assertion per test when possible
4. Mock external dependencies
5. Use `[Theory]` + `[InlineData]` for parametrized tests
6. Separate unit/integration test projects

## Timeouts

| Type | Timeout |
|------|---------|
| Unit | 1 min (60,000ms) |
| Integration | 5 min (300,000ms) |
| E2E | 10 min (600,000ms) |

## Test Length

- Max 10 LOC per unit test
- Up to 20 LOC with explanatory comment

## Mocking Anti-Patterns

- **The Mockery**: Excessive mocking → indicates too many dependencies
- **Mocking internals**: Test behavior, not implementation
- **Leaky mocks**: Isolate mock configs per test

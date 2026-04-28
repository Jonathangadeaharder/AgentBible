# C# Clean Code

## Naming Conventions

```csharp
public class UserService { }          // classes: PascalCase
public interface IUserRepository { }  // interfaces: I prefix
public void CalculateTotal() { }      // methods: PascalCase
private string _userName;             // private fields: _camelCase
public const int MaxRetryAttempts = 3; // constants: PascalCase
public enum FileStatus { Active, Inactive } // enums: PascalCase
```

## Null Handling

- Enable nullable reference types: `<Nullable>enable</Nullable>`
- Use null-coalescing operators:

```csharp
var displayName = user?.Profile?.DisplayName ?? "Unknown";
```

## Async/Await

- Always `async`/`await`, never `.Result` or `.Wait()`
- Name async methods with `Async` suffix
- Avoid `async void` except event handlers

```csharp
public async Task<string> GetDataAsync(CancellationToken ct) { ... }
```

## Dependency Injection

- Constructor injection for required dependencies
- Register with appropriate lifetimes: Transient, Scoped, Singleton

## Properties and Fields

```csharp
public string UserName { get; set; }           // auto-property
public string Id { get; private set; }         // controlled mutability
```

## LINQ

- Use LINQ for readable data transformations
- Prefer `IEnumerable<T>` for parameters (deferred execution)

## String Handling

- Interpolated strings: `$"Hello {name}"`
- `StringBuilder` for loops
- `string.IsNullOrEmpty()` / `string.IsNullOrWhiteSpace()`

## Resource Management

```csharp
using var fileStream = new FileStream(path, FileMode.Open);
// Auto-disposed at end of scope
```

## Exception Handling

- Catch specific exceptions, not generic `Exception`
- Custom exception types for domain errors
- Log with context; never swallow silently

## ASP.NET Core

- Middleware for cross-cutting concerns
- Attribute routing for REST APIs
- Validate input at DTO boundaries

## Entity Framework Core

- Code First approach
- Eager loading with `Include()` to avoid N+1
- Never expose `DbContext` from services

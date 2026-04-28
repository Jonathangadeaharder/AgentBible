# C# Design Patterns

## Strategy Pattern — Switch algorithms at runtime

```csharp
public interface IPaymentStrategy
{
    bool ProcessPayment(decimal amount);
}

public class CreditCardPayment : IPaymentStrategy
{
    public bool ProcessPayment(decimal amount) => true;
}

public class PaymentProcessor
{
    private IPaymentStrategy _strategy;
    public void SetStrategy(IPaymentStrategy strategy) => _strategy = strategy;
    public bool ExecutePayment(decimal amount) => _strategy.ProcessPayment(amount);
}
```

## Observer Pattern — Notify on state changes

```csharp
public interface IObserver { void Update(string message); }

public class Subject
{
    private readonly List<IObserver> _observers = new();
    public void Attach(IObserver observer) => _observers.Add(observer);
    public void Notify(string message)
    {
        foreach (var observer in _observers) observer.Update(message);
    }
}
```

## Quick Reference

| Pattern | Problem | When to Use |
|---------|---------|-------------|
| Strategy | Switch algorithms | Multiple approaches for same task |
| Observer | Notifications | One-to-many dependencies |
| Factory | Object creation | Complex instantiation logic |
| Singleton | Single instance | Shared resource (use sparingly) |

## C#-Specific Patterns

| Feature | Use Case |
|---------|----------|
| `record` | Immutable data objects |
| `IAsyncEnumerable<T>` | Streaming async data |
| `CancellationToken` | Cooperative cancellation |
| `IDisposable` / `IAsyncDisposable` | Resource cleanup |
| Options pattern | Configuration binding |

## Guidelines

1. Understand the problem each pattern solves
2. Prefer composition over inheritance
3. Use interfaces for loose coupling
4. Don't force patterns where not needed

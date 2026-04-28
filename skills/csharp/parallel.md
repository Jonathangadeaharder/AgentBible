# C# Parallel Programming

## Task-Based Parallelism

```csharp
// CPU-bound
var task = Task.Run(() => ComputeExpensiveResult());

// I/O-bound
public async Task<string> FetchDataAsync()
{
    using var client = new HttpClient();
    return await client.GetStringAsync("https://api.example.com/data");
}
```

## Task Coordination

```csharp
// Independent tasks
var tasks = urls.Select(url => DownloadAsync(url)).ToArray();
var results = await Task.WhenAll(tasks);

// Racing
var winner = await Task.WhenAny(task1, task2, task3);
```

## PLINQ — Data Parallelism

```csharp
var results = data
    .AsParallel()
    .WithDegreeOfParallelism(Environment.ProcessorCount)
    .Where(x => IsPrime(x))
    .ToArray();
```

## Thread Safety

```csharp
// Immutable
public record User(string Name, int Age);

// Concurrent collections
private readonly ConcurrentDictionary<string, User> _users = new();

// Lock-free
private int _counter = 0;
public void Increment() => Interlocked.Increment(ref _counter);
```

## Async Best Practices

| Rule | Example |
|------|---------|
| Never `async void` | Use `async Task` |
| Avoid `.Result` / `.Wait()` | Use `await` |
| Library code | `await task.ConfigureAwait(false)` |
| Use `ValueTask` | For synchronous fast-paths |
| Use `CancellationToken` | Cooperative cancellation |

## Common Pitfalls

```csharp
// BAD: Deadlock risk
var result = asyncMethod().Result;

// GOOD: Stay async
var result = await asyncMethod();
```

## Performance

- Prefer `Task.WhenAll` over sequential awaits
- Use `IAsyncEnumerable` for streaming
- Profile before optimizing

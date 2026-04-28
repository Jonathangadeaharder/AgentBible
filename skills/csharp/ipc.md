# C# IPC

## Quick Reference

| Method | Use Case | Complexity |
|--------|----------|------------|
| HTTP/REST (ASP.NET) | Web services | Low |
| SignalR | Real-time | Medium |
| Named Pipes | Windows IPC | Low |
| Message Queues | Async processing | Medium-High |
| gRPC | High-performance | Medium |

## HTTP/REST — ASP.NET Core

```csharp
[ApiController]
[Route("api/[controller]")]
public class UserController : ControllerBase
{
    [HttpGet("{id}")]
    public ActionResult<User> GetUser(int id) => Ok(user);

    [HttpPost]
    public ActionResult<User> CreateUser(CreateUserRequest request)
        => CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
}
```

## SignalR — Real-time

```csharp
public class ChatHub : Hub
{
    public async Task SendMessage(string user, string message)
        => await Clients.All.SendAsync("ReceiveMessage", user, message);
}

// Startup
services.AddSignalR();
```

## Named Pipes — Windows IPC

```csharp
// Server
using var server = new NamedPipeServerStream("mypipe");
server.WaitForConnection();
using var writer = new StreamWriter(server);
writer.WriteLine("Hello from server");

// Client
using var client = new NamedPipeClientStream(".", "mypipe", PipeDirection.InOut);
client.Connect();
using var reader = new StreamReader(client);
string response = reader.ReadLine();
```

## Guidelines

### Web Services
- Use ASP.NET Core Web API
- Middleware for cross-cutting concerns
- Secure endpoints with authentication

### Real-time
- SignalR for .NET-to-.NET
- Handle connection lifecycle
- Reconnection logic
- Scale with Redis backplane

### Security
- Validate all requests
- Check permissions (authorization)
- HTTPS/TLS everywhere
- Sanitize all inputs

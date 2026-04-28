# Clean Code Principles

Write clean, maintainable code across all languages and frameworks.

## Meaningful Names

Names reveal intent without comments. Reduces cognitive load 40-60%.

```
// Bad
int d;
int[] list1;

// Good
int elapsedTimeInDays;
int[] activeAccountIds;
```

**Exceptions**: Loop counters (`i`, `j`), known abbreviations (`id`, `url`), math notation (`x`, `y`).

## Functions

Do one thing, do it well, do it only.

- Keep < 20 lines
- ≤ 3 parameters (use objects for more)
- Single responsibility

```
// Bad: Multiple responsibilities mixed
public void ProcessOrder(Order order) { /* validation, calc, save, log, notify */ }

// Good: Single responsibility delegates
public void ProcessOrder(Order order) {
    ValidateOrder(order);
    order.Total = CalculateTotal(order);
    SaveOrder(order);
    NotifyProcessed(order);
}
```

**Exceptions**: Framework requirements, performance-critical code.

## Comments

Code is self-documenting. Comments explain **WHY**, not WHAT.

```
// Bad: Restates code
// Check if user is not null
if (user != null) { ... }

// Good: Explains WHY
// Stripe API requires 5s for webhook retries
var timeout = 5000;
```

**When comments ARE valuable**: Legal requirements, public API docs, non-obvious algorithms, warnings about consequences, `TODO(owner, deadline): Description`.

## Formatting

- Use automated formatters (`dotnet format`, `black`, `prettier`, `clang-format`)
- ≤ 100-120 characters per line
- Group related concepts; order high-level → low-level

## Error Handling

Errors should be explicit, handled at right level, provide context.

- Use exceptions for exceptional situations
- Don't return or pass null (use Option, empty collections, exceptions)
- Catch specific exceptions, provide context

```
// Bad: Return codes, null returns
public int CreateUser(User user) { if (user == null) return -1; }
public User GetUser(int id) { return _repo.FindById(id); } // null!

// Good: Exceptions, never null
public void CreateUser(User user) {
    if (user == null) throw new ArgumentNullException(nameof(user));
    _repo.Save(user);
}
public User GetUser(int id) {
    return _repo.FindById(id) ?? throw new UserNotFoundException(id);
}
```

**Exceptions**: Performance-critical paths, parsing (TryParse pattern), C APIs, functional Result<T> types.

## Boundaries

Isolate third-party dependencies behind your interfaces. Libraries change; tight coupling prevents testing; types leak into domain.

```
// Bad: Stripe types everywhere
public async Task<StripeCharge> ProcessPayment(Order order) { ... }

// Good: Own abstraction
public interface IPaymentGateway { Task<PaymentResult> ProcessPayment(PaymentRequest r); }
public class StripeAdapter : IPaymentGateway { /* wraps SDK */ }
// Switching to PayPal = one new adapter, domain unchanged
```

## No Legacy Fallbacks

Replace old code entirely. No silent fallbacks.

- Replace old path entirely
- Update all dependents
- Document breaking changes
- Keep codebase minimal and consistent

## Key Takeaways

- Good code doesn't need comments to explain what it does
- Functions: <20 lines, ≤3 params, single responsibility
- Never return or pass null — use exceptions, Option, or empty collections
- Isolate dependencies behind your interfaces
- Replace legacy code entirely — no silent fallbacks

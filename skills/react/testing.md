# React Testing

## Framework: Vitest + React Testing Library

```bash
pnpm add -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

## Unit Test

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('./services/api', () => ({ getUser: vi.fn() }));

describe('UserProfile', () => {
  beforeEach(() => vi.clearAllMocks());

  it('displays user name when loaded', async () => {
    // Arrange
    vi.mocked(require('./services/api').getUser).mockResolvedValue({ id: 1, name: 'John' });

    // Act
    render(<UserProfile userId={1} />);

    // Assert
    expect(await screen.findByText('John')).toBeInTheDocument();
  }, 60000);
});
```

## Integration Test

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';

describe('App navigation', () => {
  it('navigate to profile and see details', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      json: () => Promise.resolve([{ id: 1, name: 'John' }]),
      ok: true
    });

    render(<BrowserRouter><App /></BrowserRouter>);

    await userEvent.click(screen.getByRole('link', { name: 'Users' }));
    expect(await screen.findByText('John')).toBeInTheDocument();
  }, 300000);
});
```

## Best Practices

1. Test user behavior, not implementation details
2. Use semantic queries (`getByRole`, `getByText`) over `data-testid`
3. Mock external dependencies (API calls)
4. AAA pattern (Arrange, Act, Assert)
5. Test happy paths and error conditions
6. Clean up mocks between tests

## Timeouts

| Type | Timeout |
|------|---------|
| Unit | 1 min (60,000ms) |
| Integration | 5 min (300,000ms) |
| E2E | 10 min (600,000ms) |

## Vitest Config

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    testTimeout: 60000,
    globals: true,
  },
});
```

## Test Length

- Max 10 LOC per unit test
- Up to 20 LOC with explanatory comment

## Mocking Anti-Patterns

- **The Mockery**: Too many mocks → too many dependencies
- **Mocking internals**: Test observable behavior
- **Leaky mocks**: Isolate per test

# React Testing

## Framework: Jest + React Testing Library

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

## Unit Test

```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

jest.mock('./services/api', () => ({ getUser: jest.fn() }));

describe('UserProfile', () => {
  beforeEach(() => jest.clearAllMocks());

  test('displays user name when loaded', async () => {
    // Arrange
    require('./services/api').getUser.mockResolvedValue({ id: 1, name: 'John' });

    // Act
    render(<UserProfile userId={1} />);

    // Assert
    expect(await screen.findByText('John')).toBeInTheDocument();
  }, 60000);
});
```

## Integration Test

```jsx
test('navigate to profile and see details', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    json: () => Promise.resolve([{ id: 1, name: 'John' }]),
    ok: true
  });

  render(<BrowserRouter><App /></BrowserRouter>);

  await userEvent.click(screen.getByRole('link', { name: 'Users' }));
  expect(await screen.findByText('John')).toBeInTheDocument();
}, 300000);
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

## Jest Config

```js
// jest.config.js
module.exports = { testTimeout: 60000 };
```

## Test Length

- Max 10 LOC per unit test
- Up to 20 LOC with explanatory comment

## Mocking Anti-Patterns

- **The Mockery**: Too many mocks → too many dependencies
- **Mocking internals**: Test observable behavior
- **Leaky mocks**: Isolate per test

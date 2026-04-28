# React Clean Code

## Naming

```jsx
function UserProfile({ name, email }) { ... }  // components: PascalCase
const MAX_RETRIES = 3;                          // constants: UPPER_SNAKE_CASE
const handleClick = useCallback(() => { ... }); // handlers: handle prefix
const isLoading = true;                         // booleans: is/has/should
```

## Component Structure

- Functional components with hooks (not classes)
- Small, single-responsibility components
- Extract custom hooks for reusable logic
- Fragments (`<>...</>`) instead of div wrappers

## Props

```jsx
// Destructure at top
function UserCard({ name, email, avatar }) {
  return <div>...</div>;
}
```

- PropTypes or TypeScript for validation
- Keep state local to where it's used
- Lift state only when sharing between siblings

## Hooks Rules

- Only call at top level (no conditions/loops)
- Only call from React functions
- `useEffect`: always specify dependency arrays
- `useCallback`/`useMemo` for performance, not by default

## ES6+ Features

- Arrow functions for callbacks
- Destructuring: `const { name, age } = user`
- Template literals: `` `Hello ${name}` ``
- Optional chaining: `user?.profile?.name`

## Imports Order

1. External libraries
2. Internal modules
3. Components
4. Assets

## Performance

- `React.memo` for frequently rendering components
- `useMemo` for expensive calculations
- `useCallback` for props passed to memoized children
- Lazy load: `const Lazy = lazy(() => import('./Lazy'))`
- Code-split by routes

## State Management

- `useState`/`useReducer` for local state
- Context API for simple global state
- Redux/Zustand for complex state
- Derive computed values; don't store them

## Styling

- CSS Modules or styled-components
- CSS variables for theming
- Mobile-first responsive design
- Avoid inline styles for complex styling

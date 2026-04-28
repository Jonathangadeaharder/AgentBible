# React Design Patterns

## Component Composition

```jsx
// Container
const UserList = ({ users, onSelect }) => (
  <div>
    {users.map(user => (
      <UserItem key={user.id} user={user} onClick={() => onSelect(user)} />
    ))}
  </div>
);

// Presentational
const UserItem = ({ user, onClick }) => (
  <div onClick={onClick}>
    <h3>{user.name}</h3>
    <p>{user.email}</p>
  </div>
);
```

## Custom Hooks — Reuse stateful logic

```jsx
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch { return initialValue; }
  });

  const setValue = (value) => {
    setStoredValue(value);
    window.localStorage.setItem(key, JSON.stringify(value));
  };

  return [storedValue, setValue];
}
```

## Context Provider — Share data without prop drilling

```jsx
const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
};
```

## Quick Reference

| Pattern | Problem | When to Use |
|---------|---------|-------------|
| Component Composition | Reusability | Building UI |
| Custom Hooks | Logic reuse | Sharing stateful logic |
| Context | Prop drilling | Global state |
| Render Props | Render flexibility | Component customization |

## Learning Path

1. Master JSX and component basics
2. Understand when to split components
3. Learn hooks before complex patterns
4. Practice with real-world examples

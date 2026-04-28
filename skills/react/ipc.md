# React IPC

## Quick Reference

| Method | Use Case | Complexity |
|--------|----------|------------|
| Fetch/Axios | API calls | Low |
| WebSockets | Real-time | Medium |
| Context | State sharing | Low |
| Redux/Zustand | Complex state | Medium |

## HTTP/REST — Custom Hook

```jsx
function useApi(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch(url, { signal: controller.signal })
      .then(r => r.json())
      .then(setData)
      .catch(e => { if (e.name !== 'AbortError') setError(e); })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [url]);

  return { data, loading, error };
}
```

## WebSockets

```jsx
function useWebSocket(url) {
  const [messages, setMessages] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = (e) => setMessages(prev => [...prev, JSON.parse(e.data)]);
    wsRef.current = ws;
    return () => ws.close();
  }, [url]);

  const sendMessage = (msg) => {
    if (wsRef.current?.readyState === WebSocket.OPEN)
      wsRef.current.send(JSON.stringify(msg));
  };

  return { messages, sendMessage };
}
```

## Context for State

```jsx
const ApiContext = createContext();

export const ApiProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  return (
    <ApiContext.Provider value={{ user, setUser }}>
      {children}
    </ApiContext.Provider>
  );
};

export const useApi = () => useContext(ApiContext);
```

## Guidelines

### Data Fetching
- Custom hooks for fetch logic
- Handle loading/error states
- Cancel on unmount
- Cache when appropriate

### Real-time
- Connection lifecycle (open/close/error)
- Reconnection logic
- Clean up on unmount

### State Management
- Local state first
- Context for moderate complexity
- Redux/Zustand for complex apps

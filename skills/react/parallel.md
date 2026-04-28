# React Parallel Processing

## Concurrent Rendering (React 18+)

### Automatic Batching

```jsx
function handleClick() {
  setCount(c => c + 1);
  setFlag(f => !f);
  // Single re-render (batched)
}
```

### Transitions

```jsx
const [isPending, startTransition] = useTransition();

function selectTab(tabId) {
  startTransition(() => { setTabId(tabId); }); // non-urgent
}
```

### Suspense

```jsx
<Suspense fallback={<Spinner />}>
  <UserProfile userId={userId} />
</Suspense>
```

## Web Workers — CPU-intensive tasks

```jsx
// worker.js
self.onmessage = (e) => {
  const result = heavyComputation(e.data);
  self.postMessage({ result });
};

// Component
useEffect(() => {
  const worker = new Worker('/worker.js');
  worker.onmessage = (e) => setResult(e.data.result);
  return () => worker.terminate();
}, []);
```

### Comlink

```jsx
import { expose } from 'comlink'; // worker.js
expose({ processData: (data) => heavyComputation(data) });

import { wrap } from 'comlink'; // component
const api = wrap(new Worker('/worker.js'));
const result = await api.processData(data);
```

## Async Patterns

### Cleanup on Unmount

```jsx
useEffect(() => {
  let cancelled = false;
  fetchUserData(userId).then(result => {
    if (!cancelled) setData(result);
  });
  return () => { cancelled = true; };
}, [userId]);
```

### AbortController

```jsx
useEffect(() => {
  const controller = new AbortController();
  fetch(`/api/search?q=${query}`, { signal: controller.signal })
    .then(r => r.json())
    .then(setData)
    .catch(e => { if (e.name !== 'AbortError') console.error(e); });
  return () => controller.abort();
}, [query]);
```

## Performance

- `useTransition` for non-urgent updates
- `useDeferredValue` for debouncing
- `React.memo` + `useMemo` + `useCallback` for expensive work
- `react-window` for virtual scrolling
- Chunked processing for large arrays

## Best Practices

- Don't block the main thread
- Always handle async errors
- Cancel requests on unmount
- Test with React 18+ concurrent features

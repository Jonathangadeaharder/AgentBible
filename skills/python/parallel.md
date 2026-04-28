# Python Parallel Processing

## Decision Matrix

| Task Type | Approach | Why |
|-----------|----------|-----|
| I/O-bound, few ops | Threading | Simple, lightweight |
| I/O-bound, many ops | asyncio | Efficient, scalable |
| CPU-bound | Multiprocessing | True parallelism (bypasses GIL) |

## Threading — I/O-bound

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(fetch_url, url): url for url in urls}
    for future in as_completed(futures):
        result = future.result()
```

### Thread Safety

```python
import threading

class SafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    def increment(self):
        with self._lock:
            self._value += 1
```

## Multiprocessing — CPU-bound

```python
from concurrent.futures import ProcessPoolExecutor

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(compute_heavy, data_items))
```

## asyncio — Many concurrent I/O

```python
import asyncio

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

asyncio.run(fetch_all(urls))
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Threading for CPU-bound | Use multiprocessing |
| Race conditions | Use locks / `threading.Lock()` |
| Deadlocks | Consistent lock ordering |
| Missing `if __name__` guard | Required for multiprocessing |

## Resource Cleanup

```python
# Always use context managers
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(task, items))
```

## Optimal Workers

```python
import os
cpu_count = os.cpu_count()
# I/O-bound: cpu_count * 2
# CPU-bound: cpu_count
```

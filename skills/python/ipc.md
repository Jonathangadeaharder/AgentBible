# Python IPC

## Quick Reference

| Method | Use Case | Complexity |
|--------|----------|------------|
| requests / aiohttp | HTTP APIs | Low |
| websockets | Real-time | Medium |
| multiprocessing.Queue | Process communication | Medium |
| Redis pub/sub | Distributed messaging | Medium |
| gRPC | High-performance RPC | Medium-High |

## HTTP/REST — requests

```python
import requests

response = requests.get(f'https://api.example.com/users/{id}')
response.raise_for_status()
data = response.json()

# Session for connection pooling
session = requests.Session()
session.headers.update({'Authorization': 'Bearer token'})
```

## Async HTTP — aiohttp

```python
import aiohttp, asyncio

async def fetch(session, url):
    async with session.get(url) as resp:
        return await resp.text()

async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'http://example.com')

asyncio.run(main())
```

## WebSockets

```python
import websockets, asyncio

async def client():
    async with websockets.connect("ws://localhost:8765") as ws:
        await ws.send("Hello!")
        response = await ws.recv()
```

## Multiprocessing Queue

```python
from multiprocessing import Process, Queue

def producer(q):
    for i in range(5):
        q.put(f"item_{i}")
    q.put(None)

def consumer(q):
    while (item := q.get()) is not None:
        process(item)
```

## Redis Pub/Sub

```python
import redis

r = redis.Redis(host='localhost', port=6379)
r.publish('channel', 'Hello!')

pubsub = r.pubsub()
pubsub.subscribe('channel')
for msg in pubsub.listen():
    if msg['type'] == 'message':
        print(msg['data'])
```

## Guidelines

- Always handle timeouts and retries
- Use context managers for connections
- Validate and sanitize API responses
- Use connection pooling for HTTP clients

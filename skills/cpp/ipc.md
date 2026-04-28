# C++ IPC

## Quick Reference

| Method | Use Case | Platform | Complexity |
|--------|----------|----------|------------|
| TCP Sockets | Network IPC | Cross-platform | Medium |
| Shared Memory | High-performance | Unix/Linux | Medium |
| Message Queues | Async communication | Unix/Linux | Medium |
| Named Pipes | Local IPC | Windows | Low |
| REST APIs | Web services | Cross-platform | Low-Medium |

## TCP Sockets

```cpp
#include <sys/socket.h>
#include <netinet/in.h>

int createServer(int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);
    bind(fd, (struct sockaddr*)&addr, sizeof(addr));
    listen(fd, 3);
    return fd;
}

int connectToServer(const char* ip, int port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, ip, &addr.sin_addr);
    connect(sock, (struct sockaddr*)&addr, sizeof(addr));
    return sock;
}
```

## Shared Memory

```cpp
#include <sys/shm.h>

int createSharedMemory(size_t size) {
    key_t key = ftok("shmfile", 65);
    return shmget(key, size, 0666 | IPC_CREAT);
}

void* attachSharedMemory(int shmid) {
    return shmat(shmid, nullptr, 0);
}
```

## Message Queues

```cpp
#include <sys/msg.h>

struct Message { long msg_type; char data[256]; };

void sendMessage(int msgid, const char* data) {
    Message msg{.msg_type = 1};
    strncpy(msg.data, data, sizeof(msg.data));
    msgsnd(msgid, &msg, sizeof(msg.data), 0);
}
```

## Guidelines

- Handle connection errors gracefully
- Use RAII for sockets and memory
- Validate all input data
- Consider Boost.Asio for cross-platform
- Handle endianness differences

# Singleton Pattern

## Problem

When you run microservices with multiple threads or async workers, you need a **single, shared instance** of expensive resources like database connections or API clients. The `ParagoNClientManager` singleton ensures all threads in a process use the same cached client instance, avoiding redundant credentials and connection overhead.

## Solution

Create a class that enforces single instantiation:

```python
from threading import Lock

class ParagonNSingleton:
    _instance = None
    _lock = Lock()

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.token = 0
    
    def _fetch_token(self) -> int:
        # Simulate fetching a token using the API key
        with self._lock:
            self.token += 1
            return self.token

    def refresh_token(self):
        self.token = self._fetch_token()
        return self.token


class ParagonNSingletonManager:
    _instance = None 
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        raise NotImplementedError("Use get_instance() method to get the singleton instance.")

    @classmethod 
    def get_instance(cls, api_key: str) -> "ParagonNSingletonManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(ParagonNSingletonManager)
                    cls._instance.client = ParagonNSingleton(api_key)
        return cls._instance
    
    @classmethod
    def get_client(cls, api_key: str) -> ParagonNSingleton:
        instance = cls.get_instance(api_key)
        return instance.client
```

## Key Features

- **Thread-safe**: Uses double-checked locking to prevent race conditions
- **Lazy initialization**: Client created only on first use
- **Global access**: `ParagoNClientManager().get_client()` from anywhere
- **Credentials managed**: API keys loaded once per process

## Usage in Your Code

```python
# Get singleton client instance
a = ParagonNSingletonManager.get_client("my_api_key")
b = ParagonNSingletonManager.get_client("my_api_key")

print(a is b)  # True - both are the same instance

# Thread-safe access
def access_client():
    client = ParagonNSingletonManager.get_client("my_api_key")
    client.refresh_token()
    print(f"Token: {client.token}")

import threading
threads = [threading.Thread(target=access_client) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Advantages & Disadvantages

| Pros | Cons |
|------|------|
| Single shared instance reduces overhead | Hard to test (global state) |
| Thread-safe token refresh | Difficult to mock in unit tests |
| Credentials loaded once | Tight coupling to singleton |
| Easy global access | Hidden dependencies |

## Testing Tip

For unit tests, consider a **test-friendly alternative**: use dependency injection or a registry pattern instead of a pure singleton.

```python
# Testable version
client_manager = ParagoNClientManager()
# Pass to handlers as dependency
def handle_user_request(user_id, client_manager=client_manager):
    client = client_manager.get_client()
    # ...
```

# Decorator Pattern – Cross-Cutting Features for API Clients

## Problem

You want to add **cross-cutting features** to API clients like `ParagoNClient` **without modifying their code**. Typical features include:

* 🔁 Retries
* 🧵 Tracing
* 📊 Metrics / Logging

### Challenges

* Features must be **chainable** and **order-sensitive**
* Wrapper overhead must be minimal for **high-frequency calls**
* Ability to **enable/disable** features via configuration

---

### ❌ Without Decorators

Embedding retries or tracing directly in the client:

```python
class ParagoNClient:
    def get_user(self, user_id):
        print("Tracing start")
        for attempt in range(3):
            try:
                print("Calling API")
                return {"user_id": user_id}
            except Exception:
                print("Retrying...")
        print("Tracing end")
```

**Problems**:

* Violates **Single Responsibility Principle**
* Hard to test or extend
* Cannot selectively enable/disable features

---

## Solution: Decorator Pattern

Wrap the client with **decorators** for each feature:

```
ParagoNClient
     ↓
RetryingClient
     ↓
TracingClient
     ↓
Application Code
```

### Advantages:

* Each feature is **isolated**
* Decorators are **composable**
* Order can change behavior (e.g., trace every retry vs retry traced calls)
* Supports **configuration-driven enable/disable**

---

## Implementation

### Base Client

```python
class ParagoNClient:
    def get_user(self, user_id: str) -> dict:
        print(f"Fetching user {user_id}")
        return {"user_id": user_id, "name": "John Doe"}

    def update_user(self, user_id: str, data: dict) -> bool:
        print(f"Updating user {user_id}")
        return True
```

---

### Base Decorator

```python
class BaseDecorator:
    def __init__(self, client: ParagoNClient):
        self.client = client

    def get_user(self, user_id: str) -> dict:
        return self.client.get_user(user_id)

    def update_user(self, user_id: str, data: dict) -> bool:
        return self.client.update_user(user_id, data)
```

---

### Retrying Decorator

```python
class RetryingClient(BaseDecorator):
    def __init__(self, client: ParagoNClient, retries: int = 3):
        super().__init__(client)
        self.retries = retries

    def retry_func(self, func, *args, **kwargs):
        for attempt in range(self.retries):
            try:
                print(f"Attempt {attempt+1} for {func.__name__}")
                if random.random() < 0.3:  # simulate failure
                    raise Exception("Simulated network error")
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error on attempt {attempt+1}: {e}")
                if attempt == self.retries - 1:
                    raise e

    def get_user(self, user_id: str) -> dict:
        return self.retry_func(super().get_user, user_id)

    def update_user(self, user_id: str, data: dict) -> bool:
        return self.retry_func(super().update_user, user_id, data)
```

---

### Tracing Decorator

```python
class TracingClient(BaseDecorator):
    def __init__(self, client: ParagoNClient):
        super().__init__(client)

    def trace_func(self, func, *args, **kwargs):
        print(f"Tracing start: {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"Tracing end: {func.__name__} with result: {result}")
        return result

    def get_user(self, user_id: str) -> dict:
        return self.trace_func(super().get_user, user_id)

    def update_user(self, user_id: str, data: dict) -> bool:
        return self.trace_func(super().update_user, user_id, data)
```

---

### Configuration-Driven Client

```python
class ParagonClientConfig:
    def __init__(self, enable_retries=True, enable_tracing=True, retries=3):
        self.enable_retries = enable_retries
        self.enable_tracing = enable_tracing
        self.retries = retries

    def get_client(self) -> ParagoNClient:
        client = ParagoNClient()
        if self.enable_retries:
            client = RetryingClient(client, retries=self.retries)
        if self.enable_tracing:
            client = TracingClient(client)
        return client
```

---

## Usage Example

```python
config = ParagonClientConfig(enable_retries=True, enable_tracing=True, retries=3)
client = config.get_client()

client.get_user("12345")
client.update_user("12345", {"name": "Jane Doe"})
```

**Order-sensitive behavior:**

```python
# Trace every retry
client = TracingClient(RetryingClient(ParagoNClient()))

# Retry traced calls
client = RetryingClient(TracingClient(ParagoNClient()))
```

---

## Unit Tests

```python
def test_decorated_client():
    config = ParagonClientConfig(True, True, retries=2)
    client = config.get_client()
    user_data = client.get_user("12345")
    assert user_data["user_id"] == "12345"
    update_status = client.update_user("12345", {"name": "Jane Doe"})
    assert update_status is True
```

```python
def test_tracing_logic(capfd):
    client = TracingClient(ParagoNClient())
    client.get_user("12345")
    out, _ = capfd.readouterr()
    assert "Tracing start" in out
    assert "Tracing end" in out
```

---

## Benefits

| Pros                                         | Cons                           |
| -------------------------------------------- | ------------------------------ |
| No changes to core client                    | Slight overhead per call       |
| Features are composable                      | Some method duplication        |
| Order-sensitive behavior                     | Requires interface consistency |
| Easy to test                                 |                                |
| Supports configuration-driven enable/disable |                                |

---

## Summary

This implementation provides a **clean, extensible, and testable** approach to adding cross-cutting features to API clients using the **Decorator Pattern**.

It allows **runtime composition**, **configurable behavior**, and ensures **SRP adherence**.

"""
Problem: You want to add cross-cutting features (retries, logging, metrics, tracing) to API clients like `ParagoNClient`
without modifying their code. Create decorators that wrap a client instance and add behavior dynamically.

Constraints & hints:
- Decorators should be chainable and order-sensitive.
- Keep wrapper overhead small for high-frequency calls.
- Provide a way to enable/disable decorators via config.

Deliverable: describe decorator wrappers (e.g., `RetryingClient`, `TracingClient`) and how to compose them.
"""
import random

class ParagoNClient:
    def get_user(self, user_id: str) -> dict:
        # Simulate an API call to get user data
        print(f"Fetching user {user_id} from ParagoN API")
        return {"user_id": user_id, "name": "John Doe"}

    def update_user(self, user_id: str, data: dict) -> bool:
        # Simulate an API call to update user data
        print(f"Updating user {user_id} with data {data} in ParagoN API")
        return True

class BaseDecorator:
    def __init__(self, client: ParagoNClient):
        self.client = client

    def get_user(self, user_id: str) -> dict:
        return self.client.get_user(user_id)
    
    def update_user(self, user_id: str, data: dict) -> bool:
        return self.client.update_user(user_id, data)


class RetryingClient(BaseDecorator):
    def __init__(self, client: ParagoNClient, retries: int = 3):
        super().__init__(client)
        self.retries = retries

    def retry_func(self, func, *args, **kwargs):
        for attempt in range(self.retries):
            try:
                # Randomly simulate failure for demonstration
                print(f"Attempt {attempt + 1} for {func.__name__}")
                if random.random() < 0.3:  # 30% chance of failure
                    raise Exception("Simulated network error")
                
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
                if attempt == self.retries - 1:
                    raise e

    def get_user(self, user_id: str) -> dict:
        return self.retry_func(super().get_user, user_id)

    def update_user(self, user_id: str, data: dict) -> bool:
        return self.retry_func(super().update_user, user_id, data)

class TracingClient(BaseDecorator):
    def __init__(self, client: ParagoNClient):
        super().__init__(client)

    def trace_func(self, func, *args, **kwargs):
        print(f"Tracing start: {func.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            print(f"Tracing end: {func.__name__} with result: {result}")
        except Exception as e:
            print(f"Tracing error in {func.__name__}: {e}")
            raise e
        return result

    def get_user(self, user_id: str) -> dict:
        return self.trace_func(super().get_user, user_id)

    def update_user(self, user_id: str, data: dict) -> bool:
        return self.trace_func(super().update_user, user_id, data)

class ParagonClientConfig:
    def __init__(self, enable_retries: bool = True, enable_tracing: bool = True, retries: int = 3):
        self.enable_retries = enable_retries
        self.enable_tracing = enable_tracing
        self.retries = retries

    def get_client(self) -> ParagoNClient:
        base_client = ParagoNClient()
        client = base_client
        if self.enable_retries:
            client = RetryingClient(client, retries=self.retries)
        if self.enable_tracing:
            client = TracingClient(client)
        return client



### Example usage:

base_client = ParagoNClient()
retrying_client = RetryingClient(base_client, retries=3)
tracing_client = TracingClient(retrying_client)

# Test Base Client
base_user_data = base_client.get_user("12345")
base_update_status = base_client.update_user("12345", {"name": "John Doe"})

# Test Retry Client
retrying_user_data = retrying_client.get_user("12345")
retrying_update_status = retrying_client.update_user("12345", {"name": "Jane Doe"})

# Test Trace Client
user_data = tracing_client.get_user("12345")
update_status = tracing_client.update_user("12345", {"name": "Jane Doe"})


# Unit Tests

def test_decorated_client():
    config = ParagonClientConfig(enable_retries=True, enable_tracing=True, retries=2)
    client = config.get_client()

    user_data = client.get_user("12345")
    assert user_data["user_id"] == "12345"

    update_status = client.update_user("12345", {"name": "Jane Doe"})
    assert update_status is True

def test_retry_logic():
    base_client = ParagoNClient()
    retrying_client = RetryingClient(base_client, retries=5)

    user_data = retrying_client.get_user("12345")
    assert user_data["user_id"] == "12345"

def test_tracing_logic(capfd):
    base_client = ParagoNClient()
    tracing_client = TracingClient(base_client)

    user_data = tracing_client.get_user("12345")
    assert user_data["user_id"] == "12345"

    out, err = capfd.readouterr()
    assert "Tracing start: get_user" in out
    assert "Tracing end: get_user" in out


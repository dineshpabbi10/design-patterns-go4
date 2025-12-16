# Abstract Factory Pattern

## Problem

Your platform integrates with **multiple third-party ecosystems** (ParagoN, another API provider). Each provider requires a set of **cooperating client objects**:

- **ParagoN ecosystem**: `AuthClient`, `DataClient`, `WebhookClient`
- **Another API**: Different implementations of the same interfaces but different protocols/auth

Without Abstract Factory, you'd end up with messy conditional logic everywhere:

```python
# ❌ Messy without pattern
if provider == "paragon":
    auth = ParagoNAuthClient()
    data = ParagoNDataClient()
    webhook = ParagoNWebhookClient()
elif provider == "another":
    auth = AnotherAuthClient()
    data = AnotherDataClient()
    webhook = AnotherWebhookClient()
```

## Solution

Define abstract interfaces and provider-specific factories:

```python
from abc import ABC, abstractmethod
from enum import Enum

class Provider(Enum):
    PARAGON = "paragon"
    ANOTHER_API = "another_api"
    MOCK = "mock"

class BaseAuthClient(ABC):
    @abstractmethod
    def authenticate(self, credentials: dict):
        raise NotImplementedError

class BaseDataClient(ABC):
    @abstractmethod
    def fetch_data(self, query: str) -> dict:
        raise NotImplementedError

class BaseWebhookClient(ABC):
    @abstractmethod
    def send_webhook(self, payload: dict) -> None:
        raise NotImplementedError

class BaseClientFactory(ABC):
    @abstractmethod
    def create_auth_client(self) -> BaseAuthClient:
        raise NotImplementedError
    
    @abstractmethod
    def create_data_client(self) -> BaseDataClient:
        raise NotImplementedError
    
    @abstractmethod
    def create_webhook_client(self) -> BaseWebhookClient:
        raise NotImplementedError

# ParagoN implementations
class ParagoNAuthClient(BaseAuthClient):
    def authenticate(self, credentials: dict):
        pass

class ParagoNDataClient(BaseDataClient):
    def fetch_data(self, query: str) -> dict:
        return {}

class ParagoNWebhookClient(BaseWebhookClient):
    def send_webhook(self, payload: dict) -> None:
        pass

class ParagoNClientFactory(BaseClientFactory):
    def create_auth_client(self) -> BaseAuthClient:
        return ParagoNAuthClient()
    
    def create_data_client(self) -> BaseDataClient:
        return ParagoNDataClient()
    
    def create_webhook_client(self) -> BaseWebhookClient:
        return ParagoNWebhookClient()

# Mock implementations for testing
class MockAuthClient(BaseAuthClient):
    def authenticate(self, credentials: dict):
        pass

class MockDataClient(BaseDataClient):
    def fetch_data(self, query: str) -> dict:
        return {}

class MockWebhookClient(BaseWebhookClient):
    def send_webhook(self, payload: dict) -> None:
        pass

class MockClientFactory(BaseClientFactory):
    def create_auth_client(self) -> BaseAuthClient:
        return MockAuthClient()
    
    def create_data_client(self) -> BaseDataClient:
        return MockDataClient()
    
    def create_webhook_client(self) -> BaseWebhookClient:
        return MockWebhookClient()

def load_factory(provider_name: Provider) -> BaseClientFactory:
    if provider_name == Provider.PARAGON:
        return ParagoNClientFactory()
    if provider_name == Provider.MOCK:
        return MockClientFactory()
    raise ValueError(f"Unknown provider: {provider_name.value}")
```

## Usage

```python
# Configuration-driven ecosystem setup
provider = Provider.PARAGON
factory = load_factory(provider)

# Create a coordinated set of clients
auth_client = factory.create_auth_client()
data_client = factory.create_data_client()
webhook_client = factory.create_webhook_client()

# All three work together seamlessly
auth_client.authenticate({"api_key": "..."})
webhook_client.send_webhook({"event": "user_created"})
data = data_client.fetch_data("SELECT * FROM users")

# Easy to switch to testing
test_factory = load_factory(Provider.MOCK)
test_auth = test_factory.create_auth_client()
test_data = test_factory.create_data_client()
```

## Benefits

- **Consistency**: All clients from one factory are compatible
- **Easy provider switching**: Change config, not code
- **Testability**: Create a mock factory for integration tests
- **Extensibility**: Adding a new provider requires only one new factory class

## Testing Example

```python
def test_ecosystem_integration():
    # Use mock factory for testing
    factory = load_factory(Provider.MOCK)
    auth_client = factory.create_auth_client()
    data_client = factory.create_data_client()
    webhook_client = factory.create_webhook_client()
    
    # All clients are now mocked
    auth_client.authenticate({})
    webhook_client.send_webhook({})
    data = data_client.fetch_data("")
```

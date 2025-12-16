# Factory Method Pattern

## Problem

Your system needs to create API clients for **different runtime contexts**:
- **Production**: Real `ParagoNClient` connecting to live API
- **Testing**: Mock client returning fixtures
- **Async workers**: Async-aware client variant

Without a factory, you'd hardcode client selection scattered throughout your code. The Factory Method centralizes this logic.

## Solution

Define a factory method that returns the appropriate client based on configuration:

```python
from enum import Enum
from typing import Union

class ClientType(Enum):
    PRODUCTION = "production"
    TESTING = "testing"
    ASYNC = "async"

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

class ParagonClientConfig:
    def __init__(self, client_type: ClientType, client_id: str = None, client_secret: str = None):
        self.client_type = client_type
        self.client_id = client_id or "default_id"
        self.client_secret = client_secret or "default_secret"

class BaseClient:
    def __init__(self, client_config: ParagonClientConfig):
        self.client_config = client_config
    def request(self, method, url, headers, data, query_params):
        raise NotImplementedError

class BaseAsyncClient:
    def __init__(self, client_config: ParagonClientConfig):
        self.client_config = client_config
    async def request(self, method: HttpMethod, url: str, headers: dict, data: dict, query_params: dict):
        raise NotImplementedError

class ParagonSyncClient(BaseClient):
    def request(self, method: HttpMethod, url: str, headers: dict, data: dict, query_params: dict):
        return f"SyncClient: {method} {url} with {data} and {query_params}"

class ParagonAsyncClient(BaseAsyncClient):
    async def request(self, method: HttpMethod, url: str, headers: dict, data: dict, query_params: dict):
        return f"AsyncClient: {method} {url} with {data} and {query_params}"

class ParagonMockClient(BaseClient):
    def request(self, method: HttpMethod, url: str, headers: dict, data: dict, query_params: dict):
        return f"MockClient: {method} {url} with {data} and {query_params}"

def create_client(config: ParagonClientConfig) -> Union[BaseClient, BaseAsyncClient]:
    if config.client_type == ClientType.PRODUCTION:
        return ParagonSyncClient(config)
    elif config.client_type == ClientType.TESTING:
        return ParagonMockClient(config)
    elif config.client_type == ClientType.ASYNC:
        return ParagonAsyncClient(config)
    else:
        raise ValueError(f"Unknown client type: {config.client_type}")
```

## Usage

```python
# Configuration-driven client creation
config_prod = ParagonClientConfig(ClientType.PRODUCTION, client_id="prod_123")
prod_client = create_client(config_prod)

config_test = ParagonClientConfig(ClientType.TESTING)
test_client = create_client(config_test)

config_async = ParagonClientConfig(ClientType.ASYNC, client_id="async_123")
async_client = create_client(config_async)

# Use the appropriate client
result_prod = prod_client.request(HttpMethod.GET, "https://api.paragon.io/users/123", {}, {}, {})
result_test = test_client.request(HttpMethod.GET, "https://api.paragon.io/users/123", {}, {}, {})
```

## Advantages & Disadvantages

| Pros | Cons |
|------|------|
| Decouples client selection from usage | Extra indirection for simple cases |
| Easy to add new client types | Factory method becomes complex with many types |
| Testability: swap with mock effortlessly | String-based selection is fragile |
| Configuration-driven behavior | |

## Advanced: Factory with Config Objects

```python
from dataclasses import dataclass

@dataclass
class ClientConfig:
    env: str
    api_key: str = None
    timeout: int = 30
    retries: int = 3

def create_client_from_config(config: ClientConfig) -> ClientBase:
    if config.env == "prod":
        return ParagoNClientProd(api_key=config.api_key, 
                                 timeout=config.timeout, 
                                 retries=config.retries)
    elif config.env == "test":
        return ParagoNClientMock()
    # ... etc
```

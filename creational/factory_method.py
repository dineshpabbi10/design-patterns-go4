"""
Problem: Your platform needs a way to create API client instances for different runtime contexts: production (real
`ParagoNClient`), testing (mock client), and async batch workers (aio client). Design a factory method that returns
an appropriate client instance based on configuration or environment.

Constraints & hints:
- The factory must be easy to extend with new client types.
- Callers should depend on a common client interface.
- Think about dependency injection into microservice handlers and test harnesses.

Deliverable: provide a `create_client(config)` factory method that chooses and returns the right client.
"""

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
    def __init__(
        self, client_type: ClientType, client_id: str = None, client_secret: str = None
    ):
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

    async def request(
        self,
        method: HttpMethod,
        url: str,
        headers: dict,
        data: dict,
        query_params: dict,
    ):
        raise NotImplementedError


class ParagonSyncClient(BaseClient):
    def request(
        self,
        method: HttpMethod,
        url: str,
        headers: dict,
        data: dict,
        query_params: dict,
    ):
        return f"SyncClient: {method} {url} with {data} and {query_params} and headers {headers}"


class ParagonAsyncClient(BaseAsyncClient):
    async def request(
        self,
        method: HttpMethod,
        url: str,
        headers: dict,
        data: dict,
        query_params: dict,
    ):
        return f"AsyncClient: {method} {url} with {data} and {query_params} and headers {headers}"


class ParagonMockClient(BaseClient):
    def request(
        self,
        method: HttpMethod,
        url: str,
        headers: dict,
        data: dict,
        query_params: dict,
    ):
        return f"MockClient: {method} {url} with {data} and {query_params} and headers {headers}"


def create_client(config: ParagonClientConfig) -> Union[BaseClient, BaseAsyncClient]:
    if config.client_type == ClientType.PRODUCTION:
        return ParagonSyncClient(config)
    elif config.client_type == ClientType.TESTING:
        return ParagonMockClient(config)
    elif config.client_type == ClientType.ASYNC:
        return ParagonAsyncClient(config)
    else:
        raise ValueError(f"Unknown client type: {config.client_type}")

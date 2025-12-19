"""
Problem: Your system integrates with multiple third-party ecosystems (e.g., ParagoN, AnotherAPI). Each ecosystem
requires a set of cooperating clients: auth client, data client, and webhook client. Design an Abstract Factory that
produces families of compatible clients for a given provider.

Constraints & hints:
- Factories should produce a consistent set (auth, data, webhook) so components using multiple clients remain
compatible.
- Allow switching providers via config at startup.
- Support creating mock factories for integration tests.

Deliverable: describe the abstract factory API and how a microservice would request a provider-specific client set.
"""

from abc import ABC, abstractmethod
from enum import Enum


class Provider(Enum):
    PARAGON = "paragon"
    ANOTHER_API = "another_api"
    Mock = "mock"


class BaseAuthClient(ABC):
    @abstractmethod
    def authenticate(self, credentials: dict[str, str]):
        raise NotImplementedError


class BaseDataClient(ABC):
    @abstractmethod
    def fetch_data(self, query: str) -> dict:
        raise NotImplementedError


class BaseWebhookClient(ABC):
    @abstractmethod
    def send_webhook(self, payload: dict[str, str]) -> None:
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


class ParagoNAuthClient(BaseAuthClient):
    def authenticate(self, credentials: dict[str, str]):
        pass


class ParagoNDataClient(BaseDataClient):
    def fetch_data(self, query: str) -> dict:
        return {}


class ParagoNWebhookClient(BaseWebhookClient):
    def send_webhook(self, payload: dict[str, str]) -> None:
        pass


class ParagoNClientFactory(BaseClientFactory):
    def create_auth_client(self) -> BaseAuthClient:
        return ParagoNAuthClient()

    def create_data_client(self) -> BaseDataClient:
        return ParagoNDataClient()

    def create_webhook_client(self) -> BaseWebhookClient:
        return ParagoNWebhookClient()


class MockAuthClient(BaseAuthClient):
    def authenticate(self, credentials: dict[str, str]):
        pass


class MockDataClient(BaseDataClient):
    def fetch_data(self, query: str) -> dict:
        return {}


class MockWebhookClient(BaseWebhookClient):
    def send_webhook(self, payload: dict[str, str]) -> None:
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

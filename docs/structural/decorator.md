# Decorator Pattern

## Problem

You want to add **cross-cutting features** to API clients (retries, logging, metrics, tracing) without modifying their code:

```python
# ❌ Without decorators: bloated client class
class ParagoNClient:
    def fetch_user(self, user_id):
        # retry logic
        for attempt in range(3):
            try:
                # logging
                logger.info(f"Fetching user {user_id}")
                # actual call
                response = requests.get(f"https://api.paragon.io/users/{user_id}")
                # tracing
                span.log_event("fetch_user_success")
                # metrics
                metrics.increment("paragon_api_calls")
                return response.json()
            except Exception as e:
                # error handling
                logger.error(f"Error: {e}")
                span.log_event("fetch_user_error")
```

This is messy, hard to maintain, and makes the client class do too much.

## Solution

Use Decorators to wrap clients and add behavior dynamically:

```python
from abc import ABC, abstractmethod
from typing import Any, Callable
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

# Abstract client interface
class ClientBase(ABC):
    @abstractmethod
    def fetch_user(self, user_id: str) -> dict:
        raise NotImplementedError


# Real client
class ParagoNClient(ClientBase):
    def fetch_user(self, user_id: str) -> dict:
        """Bare-bones client."""
        import requests
        response = requests.get(f"https://api.paragon.io/users/{user_id}")
        return response.json()


# Decorator: add retries
class RetryingClient(ClientBase):
    def __init__(self, client: ClientBase, max_retries: int = 3):
        self.client = client
        self.max_retries = max_retries
    
    def fetch_user(self, user_id: str) -> dict:
        for attempt in range(self.max_retries):
            try:
                return self.client.fetch_user(user_id)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries} for user {user_id}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise


# Decorator: add logging
class LoggingClient(ClientBase):
    def __init__(self, client: ClientBase):
        self.client = client
    
    def fetch_user(self, user_id: str) -> dict:
        logger.info(f"Fetching user {user_id}")
        try:
            result = self.client.fetch_user(user_id)
            logger.info(f"Successfully fetched user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch user {user_id}: {e}")
            raise


# Decorator: add metrics
class MetricsClient(ClientBase):
    def __init__(self, client: ClientBase, metrics_registry):
        self.client = client
        self.metrics = metrics_registry
    
    def fetch_user(self, user_id: str) -> dict:
        start = time.time()
        try:
            result = self.client.fetch_user(user_id)
            duration = time.time() - start
            self.metrics.histogram("paragon_api_duration_seconds", duration)
            self.metrics.counter("paragon_api_calls_total", 1, tags={"status": "success"})
            return result
        except Exception as e:
            self.metrics.counter("paragon_api_calls_total", 1, tags={"status": "error"})
            raise


# Decorator: add tracing
class TracingClient(ClientBase):
    def __init__(self, client: ClientBase, tracer):
        self.client = client
        self.tracer = tracer
    
    def fetch_user(self, user_id: str) -> dict:
        with self.tracer.trace("fetch_user") as span:
            span.set_tag("user_id", user_id)
            try:
                result = self.client.fetch_user(user_id)
                span.set_tag("status", "success")
                return result
            except Exception as e:
                span.set_tag("status", "error")
                span.set_tag("error", str(e))
                raise
```

## Chainable Composition

```python
# Base client
client = ParagoNClient()

# Add decorators in order
client = LoggingClient(client)
client = RetryingClient(client, max_retries=3)
client = MetricsClient(client, metrics_registry)
client = TracingClient(client, tracer)

# Use the decorated client
user = client.fetch_user("user_123")
# → Tracing + Metrics + Retry + Logging automatically applied!
```

## Configuration-Based Decorator Selection

```python
def create_decorated_client(config: Dict[str, Any]) -> ClientBase:
    """Create client with decorators based on configuration."""
    client = ParagoNClient()
    
    if config.get("enable_logging"):
        client = LoggingClient(client)
    
    if config.get("enable_retries"):
        client = RetryingClient(client, max_retries=config.get("max_retries", 3))
    
    if config.get("enable_metrics"):
        client = MetricsClient(client, metrics_registry)
    
    if config.get("enable_tracing"):
        client = TracingClient(client, tracer)
    
    return client

# Production
prod_config = {
    "enable_logging": True,
    "enable_retries": True,
    "max_retries": 5,
    "enable_metrics": True,
    "enable_tracing": True,
}
prod_client = create_decorated_client(prod_config)

# Testing
test_config = {
    "enable_logging": True,
    "enable_retries": False,
    "enable_metrics": False,
    "enable_tracing": False,
}
test_client = create_decorated_client(test_config)
```

## Advantages

| Pros | Cons |
|------|------|
| Add behavior without modifying client | Order of decorators matters |
| Highly composable | Performance overhead for each layer |
| Testable independently | Can become hard to debug |
| Configuration-driven | |
| Single Responsibility Principle | |

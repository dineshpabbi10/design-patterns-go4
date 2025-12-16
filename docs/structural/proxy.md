# Proxy Pattern

## Problem

Your edge services aggregate calls to **ParagoNClient** on behalf of React frontends. You want to add:
- **Caching**: Avoid repeated API calls for the same user
- **Rate-limiting**: Respect ParagoN's rate limits
- **Circuit breaker**: Gracefully handle ParagoN API outages

**Without Proxy**, you'd scatter this logic throughout your code:

```python
# ❌ Messy: caching, rate-limiting, and circuit-breaking mixed with business logic
cache = {}

def fetch_user_handler(user_id):
    # Check cache
    if user_id in cache:
        return cache[user_id]
    
    # Rate limit check
    if should_rate_limit():
        return {"error": "Rate limited"}
    
    # Circuit breaker check
    if circuit_breaker.is_open():
        return {"error": "Service unavailable"}
    
    try:
        user = paragon_client.fetch_user(user_id)
        cache[user_id] = user  # Cache result
        return user
    except Exception as e:
        circuit_breaker.record_failure()
        return {"error": str(e)}
```

This is mixed with business logic and hard to test.

## Solution

Create a Proxy that wraps the real client and adds cross-cutting concerns transparently:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
from collections import defaultdict
from datetime import datetime, timedelta

class ClientInterface(ABC):
    @abstractmethod
    def fetch_user(self, user_id: str) -> Dict[str, Any]:
        raise NotImplementedError


class ParagoNClient(ClientInterface):
    """Real client - only handles API calls."""
    
    def fetch_user(self, user_id: str) -> Dict[str, Any]:
        # Actual HTTP call to ParagoN
        import requests
        response = requests.get(f"https://api.paragon.io/users/{user_id}")
        return response.json()


class CachingProxy(ClientInterface):
    """Proxy: add caching layer."""
    
    def __init__(self, client: ClientInterface, ttl_seconds: int = 300):
        self.client = client
        self.cache: Dict[str, tuple] = {}  # (value, expires_at)
        self.ttl = ttl_seconds
    
    def fetch_user(self, user_id: str) -> Dict[str, Any]:
        # Check cache
        if user_id in self.cache:
            value, expires_at = self.cache[user_id]
            if datetime.now() < expires_at:
                return value  # Return cached value
            else:
                del self.cache[user_id]  # Expired
        
        # Fetch from real client
        user = self.client.fetch_user(user_id)
        
        # Cache result
        self.cache[user_id] = (user, datetime.now() + timedelta(seconds=self.ttl))
        
        return user


class RateLimitingProxy(ClientInterface):
    """Proxy: add rate limiting."""
    
    def __init__(self, client: ClientInterface, max_requests: int = 100, window_seconds: int = 60):
        self.client = client
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = []  # Timestamps of requests
    
    def fetch_user(self, user_id: str) -> Dict[str, Any]:
        now = time.time()
        
        # Remove old requests outside window
        self.requests = [ts for ts in self.requests if now - ts < self.window]
        
        if len(self.requests) >= self.max_requests:
            raise Exception(f"Rate limit exceeded: {self.max_requests} requests per {self.window}s")
        
        # Record this request
        self.requests.append(now)
        
        # Call real client
        return self.client.fetch_user(user_id)


class CircuitBreaker:
    """Simple circuit breaker."""
    
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout_seconds
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def record_success(self):
        self.failures = 0
        self.state = "closed"
    
    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "open"
    
    def is_open(self) -> bool:
        if self.state == "closed":
            return False
        
        # Check if timeout expired
        if time.time() - self.last_failure_time > self.timeout:
            self.state = "half-open"
            self.failures = 0
            return False
        
        return self.state == "open"


class CircuitBreakerProxy(ClientInterface):
    """Proxy: add circuit breaker."""
    
    def __init__(self, client: ClientInterface, breaker: CircuitBreaker):
        self.client = client
        self.breaker = breaker
    
    def fetch_user(self, user_id: str) -> Dict[str, Any]:
        if self.breaker.is_open():
            raise Exception("Circuit breaker open: ParagoN service unavailable")
        
        try:
            user = self.client.fetch_user(user_id)
            self.breaker.record_success()
            return user
        except Exception as e:
            self.breaker.record_failure()
            raise
```

## Composing Proxies

```python
# Build layered proxy stack
real_client = ParagoNClient()

# Add rate limiting first
rate_limited = RateLimitingProxy(real_client, max_requests=100)

# Add circuit breaker
breaker = CircuitBreaker(failure_threshold=5)
protected = CircuitBreakerProxy(rate_limited, breaker)

# Add caching last (cache failures too? Or only successes?)
cached = CachingProxy(protected, ttl_seconds=300)

# Use the fully proxied client
user = cached.fetch_user("user_123")
# → Caching + Circuit Breaker + Rate Limiting applied!
```

## Configuration-Based Proxy Selection

```python
def create_proxied_client(config: Dict[str, Any]) -> ClientInterface:
    """Factory for creating proxied clients."""
    client = ParagoNClient()
    
    if config.get("enable_rate_limiting"):
        client = RateLimitingProxy(
            client,
            max_requests=config.get("max_requests", 100),
            window_seconds=config.get("rate_limit_window", 60)
        )
    
    if config.get("enable_circuit_breaker"):
        breaker = CircuitBreaker(
            failure_threshold=config.get("failure_threshold", 5),
            timeout_seconds=config.get("breaker_timeout", 60)
        )
        client = CircuitBreakerProxy(client, breaker)
    
    if config.get("enable_caching"):
        client = CachingProxy(
            client,
            ttl_seconds=config.get("cache_ttl", 300)
        )
    
    return client

# Production: full stack
prod_client = create_proxied_client({
    "enable_rate_limiting": True,
    "max_requests": 1000,
    "enable_circuit_breaker": True,
    "enable_caching": True,
    "cache_ttl": 600,
})

# Testing: only caching
test_client = create_proxied_client({
    "enable_caching": True,
    "cache_ttl": 10,
})
```

## Advantages

| Pros | Cons |
|------|------|
| Transparent to callers | Order of proxies matters |
| Clean separation of concerns | Performance overhead per layer |
| Easy to enable/disable features | Can become hard to debug |
| Highly composable | Complex stack can be confusing |
| Policies configured externally | |

## Testing

```python
def test_caching_proxy():
    mock_client = MockParagoNClient()
    proxy = CachingProxy(mock_client, ttl_seconds=10)
    
    # First call
    user1 = proxy.fetch_user("user_123")
    assert mock_client.call_count == 1
    
    # Second call (cached)
    user2 = proxy.fetch_user("user_123")
    assert mock_client.call_count == 1  # Still 1!
    assert user1 == user2
```

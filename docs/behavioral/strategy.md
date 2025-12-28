# Strategy Pattern

## Problem

Your clients must support different retry and backoff strategies depending on the endpoint (idempotent vs non-idempotent) and environment (dev vs prod). Implement a `Strategy` abstraction for pluggable retry/backoff and serialization strategies used across clients and pipeline connectors.

## Solution

Define an abstract `RetryStrategy` class with a `get_delay` method, then implement concrete strategies like `FixedIntervalStrategy` and `ExponentialBackoffWithJitterStrategy`. Integrate into a client class like `HttpClient` for automatic retries.

```python
import time
import random
from abc import ABC, abstractmethod

class RetryStrategy(ABC):
    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """Calculate the delay before the next retry based on the attempt number."""
        pass

class FixedIntervalStrategy(RetryStrategy):
    def __init__(self, interval: float):
        self.interval = interval

    def get_delay(self, attempt: int) -> float:
        return self.interval
    
class ExponentialBackoffWithJitterStrategy(RetryStrategy):
    def __init__(self, base_delay: float, max_delay: float):
        self.base_delay = base_delay
        self.max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        exp_delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        jitter = random.uniform(0, exp_delay * 0.1)  # 10% jitter
        return exp_delay + jitter
    

class HttpClient:
    def __init__(self, strategy: RetryStrategy, max_attempts: int):
        self.strategy = strategy
        self.max_attempts = max_attempts

    def get(self, url: str):
        attempt = 0
        while attempt < self.max_attempts:
            try:
                # Simulate an HTTP GET request (replace with actual request logic)
                print(f"Attempt {attempt + 1} to GET {url}")
                if random.random() < 0.7:  # Simulate a failure 70% of the time
                    raise Exception("Simulated request failure")
                print("Request succeeded")
                return "Response data"
            except Exception as e:
                print(f"Request failed: {e}")
                attempt += 1
                if attempt < self.max_attempts:
                    delay = self.strategy.get_delay(attempt)
                    print(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    print("Max attempts reached. Giving up.")
                    raise
```

## Key Features

- **Pluggable**: Strategies can be swapped via configuration or runtime.
- **Composable**: Strategies can be extended or combined (e.g., add jitter to exponential backoff).
- **Decoupled**: Core client logic unchanged; reliability tuned via strategies.

## Usage in Your Code

```python
# Example usage
if __name__ == "__main__":
    strategy = ExponentialBackoffWithJitterStrategy(base_delay=1.0, max_delay=10.0)
    client = HttpClient(strategy=strategy, max_attempts=5)
    try:
        response = client.get('https://api.example.com/data')
        print(f"Received response: {response}")
    except Exception as e:
        print(f"Final failure: {e}")
```

## Advantages & Disadvantages

| Pros | Cons |
|------|------|
| Easy to swap strategies | Requires careful design to avoid tight coupling |
| Composable implementations | Potential for strategy explosion if not managed |
| Improves reliability without changing core logic | Adds abstraction overhead |

## Testing Tip

Mock the strategy in unit tests to isolate client behavior.

```python
from unittest.mock import Mock

# Mock strategy for testing
mock_strategy = Mock()
mock_strategy.get_delay.return_value = 0.1
client = HttpClient(strategy=mock_strategy, max_attempts=3)
# Test client logic without real delays
```
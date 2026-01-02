# Chain of Responsibility Pattern

## Problem

Build a pipeline of handlers to process incoming events/messages in your data platform. Handlers include validation, enrichment (calling external APIs), authorization, and routing. Each handler may handle the message, modify it, or pass it to the next handler.

Constraints & hints:
- Handlers should be easily composed and reordered.
- Support short-circuiting, retries, and prioritized handling.
- Useful for modularizing pre-processing logic before persisting or forwarding.

Deliverable: describe handler interfaces and an example chain for event ingestion.

## Solution

Define an abstract `Handler` base class with a `handle` method that accepts an event and optionally passes it to the next handler. Create concrete handlers for specific processing steps (validation, enrichment, authorization, routing) and chain them together in priority order.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Event:
    """Represents an event flowing through the handler chain."""
    event_id: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    authorized: bool = False
    route: Optional[str] = None


class Handler(ABC):
    """Abstract base class for handlers in the chain of responsibility pattern."""

    def __init__(
        self, next_handler: Optional["Handler"] = None, priority: int = 0
    ) -> None:
        """Initialize a handler."""
        self.next_handler = next_handler
        self.priority = priority

    @abstractmethod
    def handle(self, event: Event) -> Event:
        """Process the event and pass to next handler if present."""
        pass


class ValidationHandler(Handler):
    """Handler that validates event structure and content."""

    def handle(self, event: Event) -> Event:
        """Validate the event."""
        print("Validating event")
        if not event.event_id:
            raise ValueError("Invalid event: missing event_id")
        if self.next_handler:
            return self.next_handler.handle(event)
        return event


class EnrichmentHandler(Handler):
    """Handler that enriches event data with additional information."""

    def handle(self, event: Event) -> Event:
        """Enrich the event with additional data."""
        print("Enriching event")
        event.payload["enriched"] = True
        if self.next_handler:
            return self.next_handler.handle(event)
        return event


class AuthorizationHandler(Handler):
    """Handler that authorizes the event."""

    def handle(self, event: Event) -> Event:
        """Authorize the event."""
        print("Authorizing event")
        event.authorized = True
        if self.next_handler:
            return self.next_handler.handle(event)
        return event


class RoutingHandler(Handler):
    """Handler that determines the routing destination for the event."""

    def handle(self, event: Event) -> Event:
        """Route the event to its destination."""
        print("Routing event")
        event.route = "default_route"
        if self.next_handler:
            return self.next_handler.handle(event)
        return event


def build_handler_chain() -> Handler:
    """Build and return the handler chain in priority order."""
    routing_handler = RoutingHandler(priority=4)
    authorization_handler = AuthorizationHandler(
        next_handler=routing_handler, priority=3
    )
    enrichment_handler = EnrichmentHandler(
        next_handler=authorization_handler, priority=2
    )
    validation_handler = ValidationHandler(next_handler=enrichment_handler, priority=1)

    handlers = [
        validation_handler,
        enrichment_handler,
        authorization_handler,
        routing_handler,
    ]
    handlers.sort(key=lambda h: h.priority)
    for i in range(len(handlers) - 1):
        handlers[i].next_handler = handlers[i + 1]

    return handlers[0]
```

## Key Features

- **Modular Processing**: Each handler focuses on a single responsibility.
- **Composable**: Handlers can be easily reordered or added/removed without modifying others.
- **Prioritized Execution**: Handlers can be ordered by priority for flexible sequencing.
- **Short-Circuiting**: A handler can stop the chain if validation fails (via exceptions).
- **Transparent Modification**: Handlers can modify events before passing to the next handler.
- **Decoupled Chain**: Each handler only knows about the next handler, not the entire chain.

## Usage in Your Code

```python
# Example usage
def main() -> None:
    """Demonstrate chain of responsibility pattern with event processing."""
    event = Event(event_id="evt_123", payload={"data": "sample"})
    handler_chain = build_handler_chain()
    processed_event = handler_chain.handle(event)
    
    print("Event processed successfully:")
    print(f"  Enriched: {processed_event.payload.get('enriched')}")
    print(f"  Authorized: {processed_event.authorized}")
    print(f"  Route: {processed_event.route}")

    # Check invalid event
    try:
        invalid_event = Event(event_id=None, payload={"data": "sample"})
        handler_chain.handle(invalid_event)
    except ValueError as e:
        print(f"Error processing event: {e}")


if __name__ == "__main__":
    main()
```

## Advantages & Disadvantages

| Pros | Cons |
|------|------|
| Decouples sender from processors | Request may not be handled |
| Easy to add/remove handlers dynamically | Hard to debug long chains |
| Single Responsibility Principle | Order dependency can be fragile |
| Flexible handler ordering | Potential performance overhead |
| Clear separation of concerns | Chain can become complex |
| Supports short-circuiting | Hard to trace execution flow |

## Testing Tip

Mock handlers or use a test chain to verify event transformations:

```python
def test_event_processing() -> None:
    """Test successful event processing through the chain."""
    event = Event(event_id="evt_123", payload={"data": "sample"})
    handler_chain = build_handler_chain()
    processed_event = handler_chain.handle(event)

    assert processed_event.payload.get("enriched") is True
    assert processed_event.authorized is True
    assert processed_event.route == "default_route"


def test_event_validation_failure() -> None:
    """Test that validation fails for invalid events."""
    event = Event(event_id=None, payload={"data": "sample"})
    handler_chain = build_handler_chain()
    try:
        handler_chain.handle(event)
        assert False, "Expected ValueError for invalid event"
    except ValueError as e:
        assert str(e) == "Invalid event: missing event_id"
```

## Real-World Applications

- **HTTP Request Processing**: Middleware chains in web frameworks (authentication, logging, compression).
- **Event Pipeline**: Data ingestion with validation, enrichment, and routing stages.
- **Log Processing**: Handlers for filtering, formatting, and routing log messages.
- **Payment Processing**: Multi-stage approval chain with different authorization levels.
- **Document Workflow**: Sequential processing stages (validation, signing, archiving).
- **API Gateway**: Request/response processing with authentication, rate limiting, transformation.

"""
Problem: Build a pipeline of handlers to process incoming events/messages in your data platform.
Handlers include validation, enrichment (calling external APIs), authorization, and routing.
Each handler may handle the message, modify it, or pass it to the next handler.

Constraints & hints:
- Handlers should be easily composed and reordered.
- Support short-circuiting, retries, and prioritized handling.
- Useful for modularizing pre-processing logic before persisting or forwarding.

Deliverable: describe handler interfaces and an example chain for event ingestion.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Event:
    """Represents an event flowing through the handler chain.

    Attributes:
        event_id: Unique identifier for the event.
        payload: Dictionary containing event data.
        metadata: Optional metadata associated with the event.
        authorized: Flag indicating if event has been authorized.
        route: Routing destination determined by handlers.
    """

    event_id: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    authorized: bool = False
    route: Optional[str] = None


class Handler(ABC):
    """Abstract base class for handlers in the chain of responsibility pattern.

    Each handler can process an event and optionally pass it to the next handler.
    Handlers can modify the event before passing it forward.

    Attributes:
        next_handler: The next handler in the chain.
        priority: Priority level for handler ordering (lower = earlier in chain).
    """

    def __init__(
        self, next_handler: Optional["Handler"] = None, priority: int = 0
    ) -> None:
        """Initialize a handler.

        Args:
            next_handler: The next handler in the chain.
            priority: Priority level for handler ordering.
        """
        self.next_handler = next_handler
        self.priority = priority

    @abstractmethod
    def handle(self, event: Event) -> Event:
        """Process the event.

        Args:
            event: The event to process.

        Returns:
            The processed event.

        Raises:
            Exception: If event processing fails and short-circuiting is triggered.
        """
        pass


class ValidationHandler(Handler):
    """Handler that validates event structure and content.

    Ensures required fields are present before passing to the next handler.
    """

    def handle(self, event: Event) -> Event:
        """Validate the event.

        Args:
            event: The event to validate.

        Returns:
            The validated event.

        Raises:
            ValueError: If the event is invalid.
        """
        print("Validating event")
        if not event.event_id:
            raise ValueError("Invalid event: missing event_id")
        if self.next_handler:
            return self.next_handler.handle(event)
        return event


class EnrichmentHandler(Handler):
    """Handler that enriches event data.

    Calls external APIs or performs transformations to add contextual information.
    """

    def handle(self, event: Event) -> Event:
        """Enrich the event with additional data.

        Args:
            event: The event to enrich.

        Returns:
            The enriched event.
        """
        print("Enriching event")
        event.payload["enriched"] = True
        if self.next_handler:
            return self.next_handler.handle(event)
        return event


class AuthorizationHandler(Handler):
    """Handler that authorizes the event.

    Checks permissions and access control before allowing further processing.
    """

    def handle(self, event: Event) -> Event:
        """Authorize the event.

        Args:
            event: The event to authorize.

        Returns:
            The authorized event.
        """
        print("Authorizing event")
        event.authorized = True
        if self.next_handler:
            return self.next_handler.handle(event)
        return event


class RoutingHandler(Handler):
    """Handler that determines the routing destination for the event.

    Assigns the event to an appropriate route based on its content and metadata.
    """

    def handle(self, event: Event) -> Event:
        """Route the event to its destination.

        Args:
            event: The event to route.

        Returns:
            The routed event.
        """
        print("Routing event")
        event.route = "default_route"
        if self.next_handler:
            return self.next_handler.handle(event)
        return event


def build_handler_chain() -> Handler:
    """Build and return the handler chain in priority order.

    Constructs the chain with handlers ordered by priority, with lowest priority
    handlers executing first.

    Returns:
        The first handler in the chain.
    """
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


def main() -> None:
    """Demonstrate chain of responsibility pattern with event processing."""
    event = Event(event_id="evt_123", payload={"data": "sample"})
    handler_chain = build_handler_chain()
    processed_event = handler_chain.handle(event)
    print(
        "Event processed successfully:",
        processed_event.payload,
        processed_event.authorized,
        processed_event.route,
    )

    # Check invalid event
    try:
        invalid_event = Event(event_id=None, payload={"data": "sample"})
        handler_chain.handle(invalid_event)
    except ValueError as e:
        print("Error processing event:", e)


if __name__ == "__main__":
    main()


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

# Observer Pattern

## Problem

Build an `Observer`-style event system so backend services can notify interested frontends (React) and other services about state changes (e.g., customer status updates, pipeline job progress). Observers should be able to subscribe/unsubscribe dynamically and receive typed notifications.

Constraints & hints:
- Support multiple transports (websocket for React, message bus for services).
- Ensure subscribers receive delivered events at-least-once or exactly-once based on configuration.
- Consider backpressure and slow consumer handling.

Deliverable: design the observer registration API and an example notification flow for UI updates.

## Solution

Define an abstract `Observer` class with an `update` method, and an abstract `Subject` class with methods for registering, unregistering, and notifying observers. Implement concrete subjects and observers for different transports like WebSocket and Message Bus.

```python
from abc import abstractmethod, ABC

WebSocketType = str  # Placeholder for actual WebSocket type
MessageBusType = str  # Placeholder for actual Message Bus type


class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: dict):
        """Receive update from subject."""
        pass


class Subject(ABC):
    @abstractmethod
    def register_observer(self, observer: Observer):
        """Register an observer to receive updates."""
        pass

    @abstractmethod
    def unregister_observer(self, observer: Observer):
        """Unregister an observer from receiving updates."""
        pass

    @abstractmethod
    def notify_observers(self, event: str, data: dict):
        """Notify all registered observers about an event."""
        pass


class EventSubject(Subject):
    def __init__(self):
        self._observers = set()

    def register_observer(self, observer: Observer):
        self._observers.add(observer)

    def unregister_observer(self, observer: Observer):
        self._observers.discard(observer)

    def notify_observers(self, event: str, data: dict):
        for observer in self._observers:
            observer.update(event, data)


class ReactObserver(Observer):
    def __init__(self, websocket: WebSocketType):
        self.websocket = websocket

    def update(self, event: str, data: dict):
        print(
            f"ReactObserver received event '{event}' with data: {data} with websocket {self.websocket}"
        )


class MessageBusObserver(Observer):
    def __init__(self, message_bus: MessageBusType):
        self.message_bus = message_bus

    def update(self, event: str, data: dict):
        print(
            f"MessageBusObserver received event '{event}' with data: {data} with message bus {self.message_bus}"
        )


# Example usage
if __name__ == "__main__":
    subject = EventSubject()

    react_observer = ReactObserver(websocket="WebSocketConnection1")
    message_bus_observer = MessageBusObserver(message_bus="MessageBusConnection1")

    subject.register_observer(react_observer)
    subject.register_observer(message_bus_observer)

    # Notify observers about a customer status update
    subject.notify_observers(
        event="customer_status_update", data={"customer_id": 123, "status": "active"}
    )

    # Unregister the React observer and notify again
    subject.unregister_observer(react_observer)
    subject.notify_observers(
        event="pipeline_job_progress", data={"job_id": 456, "progress": "50%"}
    )
```

## When to Use

Use the Observer pattern when you need to notify multiple objects about changes in the state of another object, especially when the number of observers is dynamic and can change at runtime. It's particularly useful in event-driven systems, GUI frameworks, and distributed systems where components need to react to state changes without tight coupling.</content>
<parameter name="filePath">/workspaces/design-patterns-gog/docs/behavioral/observer.md
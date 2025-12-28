"""
Problem: Build an `Observer`-style event system so backend services can notify interested frontends (React) and other
services about state changes (e.g., customer status updates, pipeline job progress). Observers should be able to
subscribe/unsubscribe dynamically and receive typed notifications.

Constraints & hints:
- Support multiple transports (websocket for React, message bus for services).
- Ensure subscribers receive delivered events at-least-once or exactly-once based on configuration.
- Consider backpressure and slow consumer handling.

Deliverable: design the observer registration API and an example notification flow for UI updates.
"""

from abc import abstractmethod,ABC

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
    def __init__(self, websocket : WebSocketType):
        self.websocket = websocket

    def update(self, event: str, data: dict):
        print(f"ReactObserver received event '{event}' with data: {data} with websocket {self.websocket}")

class MessageBusObserver(Observer):
    def __init__(self, message_bus : MessageBusType):
        self.message_bus = message_bus

    def update(self, event: str, data: dict):
        print(f"MessageBusObserver received event '{event}' with data: {data} with message bus {self.message_bus}")

# Example usage
if __name__ == "__main__":
    subject = EventSubject()

    react_observer = ReactObserver(websocket="WebSocketConnection1")
    message_bus_observer = MessageBusObserver(message_bus="MessageBusConnection1")

    subject.register_observer(react_observer)
    subject.register_observer(message_bus_observer)

    # Notify observers about a customer status update
    subject.notify_observers(event="customer_status_update", data={"customer_id": 123, "status": "active"})

    # Unregister the React observer and notify again
    subject.unregister_observer(react_observer)
    subject.notify_observers(event="pipeline_job_progress", data={"job_id": 456, "progress": "50%"})


# Unit Tests with pytest
def test_observer_registration_and_notification():
    subject = EventSubject()

    class TestObserver(Observer):
        def __init__(self):
            self.events = []

        def update(self, event: str, data: dict):
            self.events.append((event, data))

    observer1 = TestObserver()
    observer2 = TestObserver()

    subject.register_observer(observer1)
    subject.register_observer(observer2)

    subject.notify_observers(event="test_event", data={"key": "value"})

    assert len(observer1.events) == 1
    assert observer1.events[0] == ("test_event", {"key": "value"})
    assert len(observer2.events) == 1
    assert observer2.events[0] == ("test_event", {"key": "value"})

    subject.unregister_observer(observer1)
    subject.notify_observers(event="another_event", data={"another_key": "another_value"})

    assert len(observer1.events) == 1  # No new events for observer1
    assert len(observer2.events) == 2
    assert observer2.events[1] == ("another_event", {"another_key": "another_value"})

def test_react_observer_update(capsys):
    react_observer = ReactObserver(websocket="WebSocketConnectionTest")
    react_observer.update(event="test_event", data={"key": "value"})
    captured = capsys.readouterr()
    assert "ReactObserver received event 'test_event' with data: {'key': 'value'} with websocket WebSocketConnectionTest" in captured.out

def test_message_bus_observer_update(capsys):
    message_bus_observer = MessageBusObserver(message_bus="MessageBusConnectionTest")
    message_bus_observer.update(event="test_event", data={"key": "value"})
    captured = capsys.readouterr()
    assert "MessageBusObserver received event 'test_event' with data: {'key': 'value'} with message bus MessageBusConnectionTest" in captured.out

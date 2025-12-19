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

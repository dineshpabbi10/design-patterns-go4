"""
Problem: You need to encapsulate complex operations (e.g., "create customer across services", "provision resources") as
commands that can be queued, retried, logged, and undone when possible. Design a `Command` object model that supports
asynchronous execution and persistent queuing.

Constraints & hints:
- Commands should be serializable to store in a durable queue.
- Support undo/compensating commands for failure recovery.
- Useful for implementing background workers and sagas across microservices.

Deliverable: specify the command interface and how commands are scheduled and retried in your system.
"""

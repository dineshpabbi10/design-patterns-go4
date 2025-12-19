"""
Problem: Implement a `State` machine for an order lifecycle spanning multiple microservices (created, validated,
provisioned, billed, completed, failed). The state representation should drive behavior in services and be extensible for
future states and transitions.

Constraints & hints:
- Transitions should be explicit and testable.
- Persist state changes in an event-sourced or transactional manner to avoid race conditions.
- Useful to implement service-side guards and frontend UI state mapping.

Deliverable: specify the state enum, allowed transitions, and how services enforce them.
"""

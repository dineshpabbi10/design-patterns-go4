"""
Problem: You want to add cross-cutting features (retries, logging, metrics, tracing) to API clients like `ParagoNClient`
without modifying their code. Create decorators that wrap a client instance and add behavior dynamically.

Constraints & hints:
- Decorators should be chainable and order-sensitive.
- Keep wrapper overhead small for high-frequency calls.
- Provide a way to enable/disable decorators via config.

Deliverable: describe decorator wrappers (e.g., `RetryingClient`, `TracingClient`) and how to compose them.
"""

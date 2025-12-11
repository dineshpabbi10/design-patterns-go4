"""
Problem: Your platform needs a way to create API client instances for different runtime contexts: production (real
`ParagoNClient`), testing (mock client), and async batch workers (aio client). Design a factory method that returns
an appropriate client instance based on configuration or environment.

Constraints & hints:
- The factory must be easy to extend with new client types.
- Callers should depend on a common client interface.
- Think about dependency injection into microservice handlers and test harnesses.

Deliverable: provide a `create_client(config)` factory method that chooses and returns the right client.
"""
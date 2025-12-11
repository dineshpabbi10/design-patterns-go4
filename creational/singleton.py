"""
Problem: Design a process-local, thread-safe singleton `ParagoNClientManager` that provides a single cached instance
of a `ParagoNClient` (or similar third-party client) for a microservice process. The manager must lazily initialize
credentials, handle token refresh safely under concurrency, and expose a simple API for obtaining the client.

Constraints & hints:
- Your microservices run multiple threads and may spawn worker threads for async tasks.
- The client should be usable by both request-handling code and background jobs.
- Consider lazy init, double-checked locking, and safe cleanup on shutdown.

Deliverable: implement the singleton pattern in `ParagoNClientManager` so other modules import a single instance.
"""
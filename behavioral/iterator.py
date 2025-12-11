"""
Problem: Third-party APIs return paginated results. Build an `Iterator` abstraction that yields domain objects across
pages transparently and integrates with your async and sync callers (both backend and ingestion workers).

Constraints & hints:
- Support backpressure for streaming consumers.
- Provide adapters for both sync and async iteration.
- Handle rate limits and transient errors while paginating.

Deliverable: define an iterator interface and examples for iterating over a paginated ParagoN endpoint.
"""
"""
Problem: Your clients must support different retry and backoff strategies depending on the endpoint (idempotent vs
non-idempotent) and environment (dev vs prod). Implement a `Strategy` abstraction for pluggable retry/backoff and
serialization strategies used across clients and pipeline connectors.

Constraints & hints:
- Strategies should be simple to swap via configuration or at runtime.
- Keep implementations composable (e.g., jitter + exponential backoff).
- Useful for tuning reliability without changing core logic.

Deliverable: define the strategy interface and examples for two distinct retry strategies.
"""
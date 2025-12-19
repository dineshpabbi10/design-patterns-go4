"""
Problem: Implement a `Proxy` for your HTTP API client that adds caching, rate-limiting, and circuit-breaker behavior in
front of `ParagoNClient`. The proxy should present the same API as the real client so callers can swap them easily.

Constraints & hints:
- Proxy must be transparent to callers (same method signatures).
- Support pluggable policies for caching TTL, rate limits, and breaker thresholds.
- Useful in edge services that aggregate third-party calls for frontends.

Deliverable: define the proxy interface and discuss policy configuration and metrics.
"""

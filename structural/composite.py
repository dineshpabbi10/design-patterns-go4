"""
Problem: You need to model hierarchical operations performed across services (e.g., a bulk-update composed of multiple
sub-requests to different microservices). Design a `Composite` structure where leaf operations execute RPCs and
composite nodes aggregate and run children.

Constraints & hints:
- Support recursive composition and aggregated success/failure handling.
- Allow partial execution and reporting for long-running batches.
- Integrates with your orchestration layer that may schedule sub-operations on workers.

Deliverable: outline a `Operation` composite API and how orchestration code would execute and monitor composed operations.
"""
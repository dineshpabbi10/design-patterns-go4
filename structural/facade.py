"""
Problem: Your application uses a complex onboarding subsystem that interacts with identity, billing, and a third-party
provider (ParagoN). Create a `Facade` that offers a single high-level API for onboarding a user, hiding the orchestration
and error-recovery details from callers (frontend and other services).

Constraints & hints:
- Facade should orchestrate multiple internal calls and present a simple success/failure result.
- Useful to keep controllers and frontends simple.
- Consider idempotency for retries.

Deliverable: define the facade interface and an example flow for `onboard_user()`.
"""
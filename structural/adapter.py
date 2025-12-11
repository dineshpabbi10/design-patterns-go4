"""
Problem: A third-party API returns deeply nested JSON that doesn't match your internal DTOs used by the React frontend
and backend services. Create an `Adapter` that converts external responses into your internal models (and vice versa)
so the rest of the codebase depends on stable interfaces.

Constraints & hints:
- The adapter should hide third-party quirks (field names, missing fields, type differences).
- Make adapters composable for layered transformations.
- Consider performance for high-throughput API calls.

Deliverable: define an adapter interface and an example adapter for mapping a ParagoN API response to your `User` model.
"""
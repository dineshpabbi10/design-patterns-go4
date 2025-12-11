"""
Problem: Build a pipeline of handlers to process incoming events/messages in your data platform. Handlers include
validation, enrichment (calling external APIs), authorization, and routing. Each handler may handle the message,
modify it, or pass it to the next handler.

Constraints & hints:
- Handlers should be easily composed and reordered.
- Support short-circuiting, retries, and prioritized handling.
- Useful for modularizing pre-processing logic before persisting or forwarding.

Deliverable: describe handler interfaces and an example chain for event ingestion.
"""
"""
Problem: Your system integrates with multiple third-party ecosystems (e.g., ParagoN, AnotherAPI). Each ecosystem
requires a set of cooperating clients: auth client, data client, and webhook client. Design an Abstract Factory that
produces families of compatible clients for a given provider.

Constraints & hints:
- Factories should produce a consistent set (auth, data, webhook) so components using multiple clients remain
compatible.
- Allow switching providers via config at startup.
- Support creating mock factories for integration tests.

Deliverable: describe the abstract factory API and how a microservice would request a provider-specific client set.
"""
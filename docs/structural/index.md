# Structural Patterns

Structural patterns deal with **object composition**, creating larger structures from classes and objects through inheritance and composition.

## Overview

In microservices, React integrations, and data pipelines, structural patterns help:
- **Adapt incompatible interfaces**: Hide third-party API quirks (Adapter)
- **Decouple abstraction from implementation**: Support multiple backends (Bridge)
- **Compose hierarchies**: Build tree structures of operations (Composite)
- **Add behavior dynamically**: Wrap objects with cross-cutting concerns (Decorator)
- **Simplify complex subsystems**: Provide unified high-level interfaces (Facade)
- **Share expensive objects**: Reduce memory footprint of large datasets (Flyweight)
- **Control access**: Add layers like caching and rate-limiting (Proxy)

## Patterns in This Category

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Adapter** | Make incompatible interfaces work together | Map ParagoN API to internal User DTO |
| **Bridge** | Decouple abstraction from implementation | Ingestion logic + multiple storage backends |
| **Composite** | Treat individual and composite objects uniformly | Tree of bulk operations across services |
| **Decorator** | Add responsibilities dynamically | Wrap clients with retry/tracing/metrics |
| **Facade** | Provide simplified interface to complex subsystem | Onboarding orchestration |
| **Flyweight** | Share fine-grained objects efficiently | Shared metadata across Spark tasks |
| **Proxy** | Control access to another object | Client wrapper with caching + rate-limiting |

## When to Use

Choose structural patterns when you need to:
- Work with external systems that have incompatible interfaces
- Support multiple implementations transparently
- Build flexible hierarchies of objects
- Reduce memory usage for large numbers of similar objects
- Add or modify behavior without changing class definitions

# Creational Patterns

Creational patterns deal with **object creation mechanisms**, trying to create objects in a way that is suitable to the situation. They abstract the instantiation process.

## Overview

In microservices and data pipelines, creational patterns help:
- **Manage dependencies**: Ensure single instances of clients (Singleton)
- **Abstract creation logic**: Different client types for different environments (Factory Method)
- **Build complex configurations**: Step-by-step assembly of job specs (Builder)
- **Clone and customize**: Rapidly create variations of pipeline configs (Prototype)

## Patterns in This Category

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Singleton** | One global instance per process | ParagoNClient manager |
| **Factory Method** | Choose implementation based on config | Create prod/test/async clients |
| **Abstract Factory** | Create families of related objects | Ecosystem-specific client sets |
| **Builder** | Assemble complex objects step-by-step | SparkJobBuilder |
| **Prototype** | Clone and customize objects rapidly | Pipeline spec cloning |

## When to Use

Choose creational patterns when you need to:
- Decouple object creation from your business logic
- Support multiple ways to construct similar objects
- Enforce constraints on how objects are instantiated
- Improve testability through dependency injection

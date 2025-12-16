# Behavioral Patterns

Behavioral patterns deal with **object collaboration and responsibility distribution**. They focus on how objects interact, communicate, and distribute work.

## Overview

In microservices, event-driven systems, and orchestration, behavioral patterns help:
- **Handle requests through chains**: Pass requests along a chain of handlers (Chain of Responsibility)
- **Encapsulate operations**: Queue, retry, and undo operations as objects (Command)
- **Define domain-specific languages**: Parse and execute DSL scripts (Interpreter)
- **Iterate over collections**: Traverse elements without exposing structure (Iterator)
- **Coordinate interactions**: Centralize communication between components (Mediator)
- **Capture state**: Save and restore state for undo/replay (Memento)
- **Notify dependents**: React to state changes (Observer)
- **Alter behavior by state**: Change behavior based on internal state (State)
- **Select algorithms**: Switch algorithms at runtime (Strategy)
- **Define algorithm skeletons**: Let subclasses override steps (Template Method)
- **Apply operations to elements**: Perform operations without modifying objects (Visitor)

## Patterns in This Category

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Chain of Responsibility** | Pipeline of handlers | Event validation → enrichment → routing |
| **Command** | Encapsulate operations | Queue complex actions for async execution |
| **Interpreter** | Parse domain languages | DSL for pipeline definitions |
| **Iterator** | Traverse collections | Page through API results seamlessly |
| **Mediator** | Centralize coordination | Orchestrate multi-service workflows |
| **Memento** | Capture/restore state | Pipeline checkpoints and rollback |
| **Observer** | Notify dependents | UI updates on backend state changes |
| **State** | Alter behavior by state | Order lifecycle state machine |
| **Strategy** | Select algorithms | Pluggable retry/backoff strategies |
| **Template Method** | Define algorithm skeleton | ETL job template with customizable steps |
| **Visitor** | Apply operations | Transform/validate config trees |

## When to Use

Choose behavioral patterns when you need to:
- Decouple senders from receivers
- Encapsulate requests as objects
- Define families of algorithms
- Change object behavior at runtime
- Coordinate complex interactions between components
- Provide extensibility without modifying existing code

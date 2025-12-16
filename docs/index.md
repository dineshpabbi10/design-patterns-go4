# Gang of Four Design Patterns

Welcome to an **interactive guide to design patterns** tailored for your domain: microservices, React frontends, Spark data pipelines, and custom Python clients.

## About This Guide

This repository implements the **23 Gang of Four design patterns** with real-world examples from your development experience:

- **Microservices**: Building resilient distributed systems
- **Frontend Integration**: React components communicating with backend services
- **Data Pipelines**: Spark ETL jobs and orchestration
- **API Clients**: Custom Python clients for third-party systems (like `ParagoNClient`)

Each pattern includes:
- 📖 Detailed explanation and motivation
- 💻 Complete, runnable code examples
- 🎯 Real scenarios from your domain
- ⚡ Practical considerations and trade-offs
- 🧪 Testing strategies

## Pattern Categories

### [Creational Patterns](creational/index.md)
Deal with object creation mechanisms. Useful for managing dependencies, abstracting instantiation, and building complex configurations.

- **Singleton**: Single shared instance per process (e.g., `ParagoNClient` manager)
- **Factory Method**: Choose implementation based on configuration
- **Abstract Factory**: Create families of related objects
- **Builder**: Assemble complex objects step-by-step (e.g., `SparkJobBuilder`)
- **Prototype**: Clone and customize objects rapidly

### [Structural Patterns](structural/index.md)
Deal with object composition and how classes/objects relate. Useful for adapting interfaces, adding behavior, and managing hierarchies.

- **Adapter**: Map incompatible interfaces (e.g., ParagoN API → internal DTOs)
- **Bridge**: Decouple abstraction from implementation (e.g., ingestion + storage backends)
- **Composite**: Build tree structures of operations
- **Decorator**: Add behavior dynamically (e.g., retries, tracing, metrics)
- **Facade**: Simplify complex subsystems (e.g., user onboarding)
- **Flyweight**: Share immutable objects efficiently (e.g., Spark metadata)
- **Proxy**: Control access with policies (e.g., caching, rate-limiting)

### [Behavioral Patterns](behavioral/index.md)
Deal with object collaboration and responsibility distribution.

## Quick Start

1. **Explore a pattern**: Pick one that matches your current challenge
2. **Read the problem**: Understand the real-world scenario
3. **Study the solution**: See the complete implementation
4. **Try it**: Copy, adapt, and use in your code
5. **Extend it**: Customize for your specific needs

## Example: Builder Pattern

Looking to simplify Spark job configuration?

```python
job_spec = (SparkJobBuilder()
    .from_s3("prod-bucket", "data/customers/")
    .with_filter("status = 'active'")
    .with_windowing("tumbling", duration=3600)
    .with_resources(executors=10, memory_gb=4)
    .build())
```

[Learn more about the Builder pattern →](creational/builder.md)

---

**Last Updated**: December 2025 | **Version**: 1.0
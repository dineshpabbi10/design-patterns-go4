# Flyweight Pattern: Metadata Sharing in Spark

## Problem

Your **Spark cluster** processes **millions of records** that reference a **small set of schema descriptors and lookup metadata**:

* Each record may carry references to the same descriptors repeatedly
* Large-scale duplication of metadata increases **memory usage**
* Serialization of redundant metadata adds **overhead during task shipping** across executors
* Immutable metadata can be shared safely, but naive instantiation wastes resources

### Without Flyweight

```python
# ❌ Every record creates a new metadata object
for row in rows:
    descriptor = MetadataDescriptor(id=row.descriptor_id, fields=row.fields)
    process(row, descriptor)
```

**Problems:**

* High memory consumption
* Frequent serialization/deserialization in distributed tasks
* Redundant object creation for identical descriptors
* Difficult to maintain consistent references

---

## Solution

Use the **Flyweight Pattern** to **share immutable metadata objects** across tasks:

* **MetadataFlyweight** → Represents a single, immutable descriptor object
* **Central registry** → Ensures one instance per descriptor id
* **Thread-safe creation** → Prevents race conditions when registering flyweights
* **Distributed-safe serialization** → Reuse the same metadata instance during pickling where possible

This allows:

* Minimal memory footprint
* Fast serialization
* Safe sharing across threads and tasks
* Centralized management of metadata objects

---

## Core Design

```python
from threading import Lock
```

---

### Flyweight Class

```python
class MetadataFlyweight:
    _registry = {}
    _lock = Lock()
```

* `_registry` → stores unique flyweight instances keyed by `descriptor_id`
* `_lock` → ensures thread-safe creation

---

### Object Creation (**new**)

```python
def __new__(cls, descriptor_id: str, **attributes):
    with cls._lock:
        if descriptor_id not in cls._registry:
            instance = super(MetadataFlyweight, cls).__new__(cls)
            instance.descriptor_id = descriptor_id
            instance.attributes = attributes
            cls._registry[descriptor_id] = instance
        return cls._registry[descriptor_id]
```

**Highlights:**

* Ensures **singleton per descriptor id**
* Safe to use in **multi-threaded environments**
* Additional attributes are stored **only once**
* Returns existing object if descriptor already exists

---

### Representation

```python
def __repr__(self):
    return f"MetadataFlyweight(id={self.descriptor_id}, attributes={self.attributes})"
```

* Useful for debugging and logging
* Shows **descriptor id and attributes** of shared object

---

## Usage Example: Spark Pipeline

```python
# Imagine multiple tasks processing rows with the same descriptor
tasks = [
    {"descriptor_id": "user", "fields": ["id", "name"]},
    {"descriptor_id": "order", "fields": ["id", "amount"]},
    {"descriptor_id": "user", "fields": ["id", "name"]},
]

flyweights = [MetadataFlyweight(**t) for t in tasks]

for fw in flyweights:
    print(fw)
```

**Output:**

```
MetadataFlyweight(id=user, attributes={'fields': ['id', 'name']})
MetadataFlyweight(id=order, attributes={'fields': ['id', 'amount']})
MetadataFlyweight(id=user, attributes={'fields': ['id', 'name']})
```

Notice that the **`user` descriptor is shared** across tasks.

---

## Benefits

| Pros                                    | Cons                                     |
| --------------------------------------- | ---------------------------------------- |
| Reduces memory usage by sharing objects | Requires careful immutability management |
| Faster serialization/deserialization    | Central registry can become a bottleneck |
| Thread-safe creation                    | Slight overhead on first creation        |
| Simplifies metadata consistency         | Not suitable for mutable objects         |

---

## Advanced Considerations

* **Pickling in Spark**: Ensure descriptors are pickle-friendly; avoid complex references that cannot be serialized
* **Distributed caching**: Could extend the registry to use a **distributed cache** (Redis, Broadcast variables) for cross-node sharing
* **Lazy attribute computation**: Flyweight can defer heavy initialization until first access
* **Immutable objects**: Flyweights must remain immutable to safely share across threads and tasks

---

## When to Use Flyweight

✅ Use when:

* Many objects share identical **read-only metadata**
* Memory usage or serialization overhead is significant
* You want centralized management for consistent references

❌ Avoid when:

* Objects are mutable or change per task
* Metadata is unique per record or rarely reused
* Overhead of registry outweighs memory savings

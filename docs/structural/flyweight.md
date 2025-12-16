# Flyweight Pattern

## Problem

Your Spark cluster processes **millions of records** that reference a small set of **schema descriptors and lookup metadata**. Storing each record's full metadata copy wastes memory and increases serialization overhead across worker processes.

Example: Processing 1 million events, each with a schema descriptor (1KB each):
- **Without Flyweight**: 1 million × 1KB = 1GB memory waste
- **With Flyweight**: 1 shared descriptor × 1KB + 1 million references = ~8MB + references

## Solution

Create a shared registry of immutable metadata objects that tasks reference by ID:

```python
from typing import Dict, Any, Optional
from dataclasses import dataclass
import threading

@dataclass(frozen=True)  # Immutable
class SchemaDescriptor:
    """Shared schema metadata."""
    schema_id: str
    name: str
    version: str
    fields: tuple  # Immutable tuple of field definitions
    created_at: str
    
    def __hash__(self):
        return hash(self.schema_id)


@dataclass(frozen=True)
class LookupMetadata:
    """Shared lookup table metadata."""
    lookup_id: str
    name: str
    data: tuple  # Immutable, e.g., valid enum values
    last_updated: str


class FlyweightRegistry:
    """Central registry for shared immutable objects."""
    
    def __init__(self):
        self._schemas: Dict[str, SchemaDescriptor] = {}
        self._lookups: Dict[str, LookupMetadata] = {}
        self._lock = threading.RLock()
    
    def register_schema(self, descriptor: SchemaDescriptor) -> None:
        """Register a schema descriptor."""
        with self._lock:
            self._schemas[descriptor.schema_id] = descriptor
    
    def get_schema(self, schema_id: str) -> Optional[SchemaDescriptor]:
        """Get schema by ID (thread-safe)."""
        with self._lock:
            return self._schemas.get(schema_id)
    
    def register_lookup(self, metadata: LookupMetadata) -> None:
        """Register lookup metadata."""
        with self._lock:
            self._lookups[metadata.lookup_id] = metadata
    
    def get_lookup(self, lookup_id: str) -> Optional[LookupMetadata]:
        """Get lookup metadata by ID."""
        with self._lock:
            return self._lookups.get(lookup_id)
    
    def preload_common_schemas(self):
        """Preload commonly-used schemas."""
        # Schemas shared across many tasks
        self.register_schema(SchemaDescriptor(
            schema_id="event_v1",
            name="Event",
            version="1.0",
            fields=("timestamp", "user_id", "event_type", "properties"),
            created_at="2025-01-01",
        ))
        
        self.register_schema(SchemaDescriptor(
            schema_id="user_v1",
            name="User",
            version="1.0",
            fields=("user_id", "email", "status", "created_at"),
            created_at="2025-01-01",
        ))


# Global registry
_registry = FlyweightRegistry()
_registry.preload_common_schemas()


class EventRecord:
    """Record that references shared schema via ID."""
    
    def __init__(self, schema_id: str, data: Dict[str, Any]):
        self.schema_id = schema_id  # Just store ID
        self.data = data
    
    def get_schema(self) -> SchemaDescriptor:
        """Retrieve shared schema from registry."""
        return _registry.get_schema(self.schema_id)
    
    def validate(self) -> bool:
        """Validate data against shared schema."""
        schema = self.get_schema()
        if not schema:
            raise ValueError(f"Schema {self.schema_id} not found")
        
        # Check if all required fields present
        for field in schema.fields:
            if field not in self.data:
                return False
        return True


# Usage in Spark pipeline
def process_events(event_iterator):
    """Spark task that processes events without storing schema copies."""
    
    for event_dict in event_iterator:
        # Create event with reference to shared schema
        record = EventRecord(
            schema_id="event_v1",
            data=event_dict
        )
        
        # Validate using shared schema
        if record.validate():
            # Process validated event
            process_valid_event(record)
        else:
            handle_invalid_event(record)


# Broadcasting registry to workers
def spark_job(spark):
    """Spark job setup."""
    
    # Broadcast registry to all workers (one-time cost)
    registry_broadcast = spark.sparkContext.broadcast(_registry)
    
    # RDD/DataFrame processing
    events_df = spark.read.parquet("s3://data/events/")
    
    # Each partition processes events using shared registry
    events_df.foreach(lambda row: process_events_with_registry(row, registry_broadcast.value))
```

## Benefits

| Pros | Cons |
|------|------|
| Massive memory savings for large datasets | All flyweights must be immutable |
| Reduced serialization overhead | Adds indirection (registry lookups) |
| Easier to update metadata globally | Complexity of registry management |
| Scales to millions of objects | Thread safety needed |

## Advanced: Lazy Loading with LRU Cache

```python
from functools import lru_cache

class CachedFlyweightRegistry(FlyweightRegistry):
    """Registry with LRU cache for frequently-accessed schemas."""
    
    @lru_cache(maxsize=1000)
    def get_schema_cached(self, schema_id: str) -> Optional[SchemaDescriptor]:
        """Cached lookup for hot schemas."""
        return self.get_schema(schema_id)
```

## When to Use

- Processing millions of records with shared metadata
- Memory constraints in distributed systems
- Metadata is immutable and rarely changes
- High serialization costs between worker processes

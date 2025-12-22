"""
Problem: Your Spark cluster processes millions of records that reference a small set of schema descriptors and lookup
metadata. Implement a `Flyweight` to share immutable metadata objects across tasks to reduce memory usage and
serialization overhead.

Constraints & hints:
- Flyweights must be safe to share across threads and worker processes where possible.
- Consider registering flyweights in a central registry keyed by descriptor id.
- Pay attention to pickling/serialization for distributed execution.

Deliverable: describe a `MetadataFlyweight` registry and how pipeline tasks obtain shared descriptors.
"""
from threading import Lock
class MetadataFlyweight:
    _registry = {}
    _lock = Lock()

    def __new__(cls, descriptor_id: str, **attributes):
        with cls._lock:
            if descriptor_id not in cls._registry:
                instance = super(MetadataFlyweight, cls).__new__(cls)
                instance.descriptor_id = descriptor_id
                instance.attributes = attributes
                cls._registry[descriptor_id] = instance
            return cls._registry[descriptor_id]

    def __repr__(self):
        return f"MetadataFlyweight(id={self.descriptor_id}, attributes={self.attributes})"
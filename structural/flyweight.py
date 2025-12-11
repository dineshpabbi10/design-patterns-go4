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
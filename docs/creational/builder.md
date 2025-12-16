# Builder Pattern

## Problem

Constructing a **complex Spark job configuration** requires many optional parameters:
- Input sources (S3, Kafka, database)
- Transforms (filters, maps, joins)
- Windowing and triggers
- Resource settings (executors, memory)
- Monitoring hooks

Without a builder, you'd either:
1. Use a giant constructor with 20 parameters
2. Pass a loose dictionary around
3. Use `**kwargs` and lose type safety

```python
# ❌ Messy constructor
job = SparkJob(
    source, format, schema_path,
    filter_fn, map_fn, join_key,
    window_type, window_duration, trigger_interval,
    executor_count, executor_memory, num_cores,
    shuffle_partitions, log_level, metrics_enabled,
    # ... and 10 more parameters
)
```

## Solution

Use a builder with **fluent chaining** to assemble the spec step-by-step:

```python
from copy import deepcopy

class SparkJobSpec:
    __slots__ = (
        "input_source",
        "transforms",
        "windowing",
        "triggers",
        "resources",
        "monitoring_hooks",
        "spec_version",
    )

    def __init__(self, *, input_source, transforms, windowing, triggers, resources, monitoring_hooks, spec_version="1.0"):
        object.__setattr__(self, "input_source", input_source)
        object.__setattr__(self, "transforms", tuple(transforms))
        object.__setattr__(self, "windowing", windowing)
        object.__setattr__(self, "triggers", triggers)
        object.__setattr__(self, "resources", deepcopy(resources))
        object.__setattr__(self, "monitoring_hooks", tuple(monitoring_hooks))
        object.__setattr__(self, "spec_version", spec_version)

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise AttributeError("Cannot modify immutable SparkJobSpec")
        super().__setattr__(key, value)

    def __delattr__(self, key):
        raise AttributeError("SparkJobSpec is immutable")

    def serialize(self):
        return {
            "input_source": self.input_source,
            "transforms": self.transforms,
            "windowing": self.windowing,
            "triggers": self.triggers,
            "resources": self.resources,
            "monitoring_hooks": self.monitoring_hooks,
            "spec_version": self.spec_version,
        }

class SparkJobBuilder:
    def __init__(self):
        self._input_source = None
        self._transforms = []
        self._windowing = None
        self._triggers = None
        self._resources = {}
        self._monitoring_hooks = []
        self._spec_version = "1.0"

    def input_source(self, source):
        self._input_source = source
        return self
    
    def set_transforms(self, transforms):
        self._transforms = transforms
        return self
    
    def windowing(self, windowing):
        self._windowing = windowing
        return self
    
    def triggers(self, triggers):
        self._triggers = triggers
        return self

    def resources(self, resources):
        self._resources = resources
        return self
    
    def monitoring_hooks(self, hooks):
        self._monitoring_hooks = hooks
        return self
    
    def spec_version(self, version):
        self._spec_version = version
        return self
    
    def build(self):
        return SparkJobSpec(
            input_source=self._input_source,
            transforms=self._transforms,
            windowing=self._windowing,
            triggers=self._triggers,
            resources=self._resources,
            monitoring_hooks=self._monitoring_hooks,
            spec_version=self._spec_version
        )
```

## Usage Examples

```python
# Build a job spec fluently
builder = SparkJobBuilder()
job_spec = (builder
    .input_source({"type": "s3", "bucket": "prod-bucket", "path": "data/"})
    .set_transforms([
        {"type": "filter", "condition": "status = 'active'"},
        {"type": "enrich", "api": "ParagoNClient"}
    ])
    .windowing({"type": "tumbling", "duration": 3600})
    .triggers({"type": "micro-batch", "interval": 60})
    .resources({"executor_count": 10, "executor_memory_gb": 4})
    .monitoring_hooks([{"type": "prometheus"}])
    .build())

# Serialize for storage
config = job_spec.serialize()

# Immutability guaranteed
try:
    job_spec.input_source = "new_value"  # Raises AttributeError
except AttributeError as e:
    print(f"Cannot modify: {e}")
```

## Advantages

| Pros | Cons |
|------|------|
| Readable fluent interface | Extra classes/code |
| Type-safe method signatures | Slightly more overhead |
| Immutable final spec | Not suitable for tiny objects |
| Easy to extend with new methods | Requires careful implementation |
| Versioning built-in | |

## Advanced: Builder Cloning

```python
# Clone an existing job and modify
modified_job = (SparkJobBuilder()
    # Copy settings from existing spec
    # then override specific fields
    .from_s3("test-bucket", "data/customers/")
    .with_resources(executors=2)  # Fewer resources for testing
    .build())
```

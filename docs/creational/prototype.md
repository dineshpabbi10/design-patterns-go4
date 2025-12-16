# Prototype Pattern

## Problem

In your ETL orchestration, you often reuse **pipeline configurations** with minor variations:

```python
# Base template: daily customer data pipeline
base_config = {
    "name": "customer_daily",
    "source": {"s3": "s3://prod-data/customers/"},
    "transforms": [
        {"type": "filter", "condition": "is_active=true"},
        {"type": "enrich", "api": "ParagoNClient"},
        {"type": "aggregate", "window": "1d"},
    ],
    "resources": {"executors": 10, "memory_gb": 4},
}
```

Now you need **variations** for:
- **Testing**: Same config but with test data and fewer resources
- **Weekly rollup**: Different transforms and schedule
- **A/B test variant**: Modified enrichment logic

**Without Prototype**, you rebuild each from scratch, leading to duplication and inconsistency.

## Solution

Implement a cloning mechanism with provenance tracking:

```python
from copy import deepcopy, copy

class PipelineSpec:
    """Pipeline specification with cloning and provenance."""
    
    def __init__(self, *, name: str, input_source: str, 
                 transforms: list, resources: dict, 
                 metadata: dict = None):
        self.name = name
        self.input_source = input_source
        self.transforms = transforms
        self.resources = resources
        self.metadata = metadata or {}

    def clone(self, deep: bool = True, **overrides):
        """Clone the spec, optionally overriding fields.
        
        Args:
            deep: If True, recursively copy nested structures
            **overrides: Fields to override in the cloned spec
        
        Returns:
            PipelineSpec: New independent instance
        """
        if deep:
            # Deep copy: all nested structures are independent
            cloned_transforms = deepcopy(self.transforms)
            cloned_resources = deepcopy(self.resources)
            cloned_metadata = deepcopy(self.metadata)
        else:
            # Shallow copy: nested objects are shared
            cloned_transforms = copy(self.transforms)
            cloned_resources = copy(self.resources)
            cloned_metadata = copy(self.metadata)
        
        # Apply overrides
        for key, value in overrides.items():
            if key == "transforms":
                cloned_transforms = value
            elif key == "resources":
                cloned_resources = value
            elif key == "metadata":
                cloned_metadata = value
        
        # Create new spec
        new_spec = PipelineSpec(
            name=overrides.get("name", self.name),
            input_source=overrides.get("input_source", self.input_source),
            transforms=cloned_transforms,
            resources=cloned_resources,
            metadata=cloned_metadata,
        )
        
        # Update provenance
        new_spec.metadata['cloned_from'] = self.name
        
        return new_spec
```

## Usage Examples

### Basic Cloning with Deep Copy

```python
# Create a base pipeline spec
base_spec = PipelineSpec(
    name="base_etl",
    input_source="s3://input/data",
    transforms=["parse", "clean", "enrich"],
    resources={"executor_memory": "4G", "partitions": 100},
)

# Clone it for a new use case (deep copy by default)
# All nested structures are independent
test_spec = base_spec.clone(
    name="test_etl",
    input_source="s3://test/data",
)

# Modify test_spec's transforms - does NOT affect base_spec
test_spec.transforms.append("validate")
print(f"base_spec transforms: {base_spec.transforms}")  # Still ["parse", "clean", "enrich"]
print(f"test_spec transforms: {test_spec.transforms}")  # ["parse", "clean", "enrich", "validate"]
print(f"test_spec provenance: {test_spec.metadata.get('cloned_from')}")  # "base_etl"
```

### Shallow Copy for Shared Resources

```python
# When you want nested structures to share references
# (e.g., shared resource pool configuration)
shared_spec = base_spec.clone(deep=False)
shared_spec.resources["executor_memory"] = "8G"

# With shallow copy, the list reference is shared
print(f"base_spec transforms: {base_spec.transforms}")  # Changes are reflected
```

### Templating with Overrides

```python
# Template for different environments
prod_spec = base_spec.clone(
    name="prod_etl",
    input_source="s3://prod/data",
    resources={"executor_memory": "16G", "partitions": 500},
)

# Create a debug variant
debug_spec = prod_spec.clone(
    name="prod_etl_debug",
    transforms=["parse", "clean"],  # Skip expensive enrich
    resources={"executor_memory": "2G", "partitions": 10},
)
```

## Shallow vs Deep Clone

| Shallow Copy | Deep Copy |
|--------------|-----------|
| `cloned_transforms = copy(self.transforms)` | `cloned_transforms = deepcopy(self.transforms)` |
| New list, but items still shared | Completely independent copy |
| Faster, less memory | Safer, prevents accidental mutations |
| Use when: only changing top-level fields | Use when: modifying nested structures |

```python
# Shallow clone example
base_transforms = [{"type": "filter"}]
clone1 = copy(base_transforms)
clone1[0]["condition"] = "active=true"
# base_transforms ALSO changed! ⚠️

# Deep clone example
clone2 = deepcopy(base_transforms)
clone2[0]["condition"] = "active=true"
# base_transforms unchanged ✓
```

## Advantages & Disadvantages

| Pros | Cons |
|------|------|
| Avoid duplication of complex configs | Deep copying can be slow/memory-intensive |
| Track config evolution via provenance | Extra book-keeping required |
| Support templates and variants | Shallow copy gotchas if not careful |
| Faster than manual rebuilding | Complex graphs may need custom cloning |

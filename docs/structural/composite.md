# Composite Pattern

## Problem

You need to model **hierarchical operations** performed across services. For example, a bulk-update composed of multiple sub-requests to different microservices:

```
Bulk Customer Update
├── Update Identity Service
│   ├── Update name
│   └── Update email
├── Update Billing Service
│   └── Update subscription status
└── Update Notification Service
    └── Re-subscribe to mailing list
```

Without Composite, you'd have deeply nested conditionals and ad-hoc aggregation logic.

## Solution

Implement a tree structure where both leaf and composite nodes share a common interface:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Operation(ABC):
    """Abstract operation that can be leaf or composite."""
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute and return result."""
        raise NotImplementedError
    
    @abstractmethod
    def get_status(self) -> str:
        """Get operation status."""
        raise NotImplementedError


class LeafOperation(Operation):
    """Leaf: actual RPC to a microservice."""
    
    def __init__(self, service_name: str, operation: str, payload: Dict):
        self.service_name = service_name
        self.operation = operation
        self.payload = payload
        self.result = None
        self.status = "pending"
    
    def execute(self) -> Dict[str, Any]:
        """Execute RPC to microservice."""
        print(f"Executing {self.operation} on {self.service_name}...")
        # Call actual microservice
        self.result = {"service": self.service_name, "success": True}
        self.status = "completed"
        return self.result
    
    def get_status(self) -> str:
        return self.status


class CompositeOperation(Operation):
    """Composite: aggregates multiple operations."""
    
    def __init__(self, name: str):
        self.name = name
        self.children: List[Operation] = []
        self.status = "pending"
        self.results = {}
    
    def add_operation(self, operation: Operation) -> None:
        """Add child operation."""
        self.children.append(operation)
    
    def execute(self) -> Dict[str, Any]:
        """Execute all children."""
        print(f"Executing composite operation: {self.name}")
        self.status = "running"
        
        for child in self.children:
            result = child.execute()
            self.results[child.service_name if hasattr(child, 'service_name') else self.name] = result
        
        self.status = "completed"
        return self.results
    
    def get_status(self) -> str:
        statuses = [child.get_status() for child in self.children]
        if all(s == "completed" for s in statuses):
            return "completed"
        elif any(s == "failed" for s in statuses):
            return "failed"
        return "running"


# Example: bulk customer update
def create_bulk_update_operation():
    root = CompositeOperation("BulkCustomerUpdate")
    
    # Identity service updates
    identity_ops = CompositeOperation("IdentityServiceBatch")
    identity_ops.add_operation(LeafOperation("identity", "update_name", {"user_id": "123", "name": "John Doe"}))
    identity_ops.add_operation(LeafOperation("identity", "update_email", {"user_id": "123", "email": "john@example.com"}))
    root.add_operation(identity_ops)
    
    # Billing service update
    root.add_operation(LeafOperation("billing", "update_subscription", {"user_id": "123", "status": "premium"}))
    
    # Notification service update
    root.add_operation(LeafOperation("notifications", "subscribe", {"user_id": "123", "type": "marketing"}))
    
    return root

# Execute
bulk_op = create_bulk_update_operation()
results = bulk_op.execute()
print(f"Final status: {bulk_op.get_status()}")
```

## Advantages

- Treat leaf and composite nodes uniformly
- Easy to add new operation types
- Natural hierarchical structure
- Partial execution and error handling

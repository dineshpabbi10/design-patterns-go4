# Adapter Pattern

## Problem

Your **microservices and React frontend** rely on consistent internal data models (DTOs). However, the **ParagoN API** (which you interact with via `ParagoNClient`) returns deeply nested JSON with inconsistent field names, optional fields, and different data types:

### ParagoN API Response
```json
{
  "user_id": "12345",
  "personal_info": {
    "firstName": "John",
    "lastName": "Doe",
    "contact": {
      "email_addr": "john.doe@example.com",
      "phone_num": "+1234567890"
    }
  },
  "account_status": "ACTIVE",
  "created_at": "2023-10-01T12:00:00Z",
  "metadata": {
    "tags": ["premium", "verified"],
    "preferences": {"notifications": true}
  }
}
```

### Your Internal User Model
```json
{
  "id": "12345",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "status": "active",
  "createdAt": "2023-10-01T12:00:00Z",
  "tags": ["premium", "verified"],
  "preferences": {"notifications": true}
}
```

**Discrepancies:**
- Field name variations (`user_id` → `id`, `email_addr` → `email`, `account_status` → `status`)
- Nested structure flattening
- Type conversions (string status to lowercase)
- Optional fields may be missing

## Solution

Implement bidirectional adapters that hide the complexity:

```python
from abc import ABC, abstractmethod

class BaseAdapterModel(ABC):
    """Abstract adapter interface."""
    
    def __init__(self, external_data: dict):
        self.external_data = external_data

    @abstractmethod
    def to_internal(self) -> dict:
        """Convert external API response to internal model."""
        raise NotImplementedError("to_internal method not implemented")
    
    @abstractmethod
    def to_external(self) -> dict:
        """Convert internal model back to external API format."""
        raise NotImplementedError("to_external method not implemented")


class ParagoNUserAdapter(BaseAdapterModel):
    """Maps ParagoN API user responses to internal User DTOs."""
    
    def to_internal(self) -> dict:
        """Flatten ParagoN's nested response to internal User model."""
        data = self.external_data
        internal_data = {
            "id": data.get("user_id"),
            "firstName": data.get("personal_info", {}).get("firstName"),
            "lastName": data.get("personal_info", {}).get("lastName"),
            "email": data.get("personal_info", {}).get("contact", {}).get("email_addr"),
            "phone": data.get("personal_info", {}).get("contact", {}).get("phone_num"),
            "status": data.get("account_status", "").lower(),
            "createdAt": data.get("created_at"),
            "tags": data.get("metadata", {}).get("tags", []),
            "preferences": data.get("metadata", {}).get("preferences", {}),
        }
        return internal_data

    def to_external(self) -> dict:
        """Map internal User model back to ParagoN format."""
        internal_data = self.external_data
        external_data = {
            "user_id": internal_data.get("id"),
            "personal_info": {
                "firstName": internal_data.get("firstName"),
                "lastName": internal_data.get("lastName"),
                "contact": {
                    "email_addr": internal_data.get("email"),
                    "phone_num": internal_data.get("phone"),
                },
            },
            "account_status": internal_data.get("status", "").upper(),
            "created_at": internal_data.get("createdAt"),
            "metadata": {
                "tags": internal_data.get("tags", []),
                "preferences": internal_data.get("preferences", {}),
            },
        }
        return external_data
```

## Usage Examples

### Basic Adaptation: ParagoN Response to Internal Model

```python
# Receive data from ParagoN API
paragon_response = {
    "user_id": "12345",
    "personal_info": {
        "firstName": "John",
        "lastName": "Doe",
        "contact": {
            "email_addr": "john@example.com",
            "phone_num": "+1234567890"
        }
    },
    "account_status": "ACTIVE",
    "created_at": "2023-10-01T12:00:00Z",
    "metadata": {
        "tags": ["premium", "verified"],
        "preferences": {"notifications": True}
    }
}

# Adapt to internal model
adapter = ParagoNUserAdapter(paragon_response)
internal_user = adapter.to_internal()

print(internal_user)
# {
#     "id": "12345",
#     "firstName": "John",
#     "lastName": "Doe",
#     "email": "john@example.com",
#     "phone": "+1234567890",
#     "status": "active",  # lowercased
#     "createdAt": "2023-10-01T12:00:00Z",
#     "tags": ["premium", "verified"],
#     "preferences": {"notifications": True}
# }
```

### Reverse Adaptation: Internal Model to ParagoN Format

```python
# Your internal user model (from React or database)
internal_user = {
    "id": "12345",
    "firstName": "Jane",
    "lastName": "Smith",
    "email": "jane@example.com",
    "phone": "+9876543210",
    "status": "active",
    "createdAt": "2023-10-01T12:00:00Z",
    "tags": ["vip"],
    "preferences": {"notifications": False}
}

# Adapt back to ParagoN format for API request
adapter = ParagoNUserAdapter(internal_user)
paragon_format = adapter.to_external()

print(paragon_format)
# {
#     "user_id": "12345",
#     "personal_info": {
#         "firstName": "Jane",
#         "lastName": "Smith",
#         "contact": {
#             "email_addr": "jane@example.com",
#             "phone_num": "+9876543210"
#         }
#     },
#     "account_status": "ACTIVE",  # uppercased
#     "created_at": "2023-10-01T12:00:00Z",
#     "metadata": {
#         "tags": ["vip"],
#         "preferences": {"notifications": False}
#     }
# }
```

### Handling Missing Fields

```python
# Incomplete ParagoN response (missing optional fields)
incomplete_response = {
    "user_id": "99999",
    "personal_info": {
        "firstName": "Bob"
        # No lastName, contact info, etc.
    },
    "account_status": "PENDING"
    # No created_at, metadata
}

# Adapter safely handles missing nested fields
adapter = ParagoNUserAdapter(incomplete_response)
internal = adapter.to_internal()

print(internal)
# {
#     "id": "99999",
#     "firstName": "Bob",
#     "lastName": None,  # Missing field
#     "email": None,
#     "phone": None,
#     "status": "pending",
#     "createdAt": None,
#     "tags": [],  # Default empty list
#     "preferences": {}  # Default empty dict
# }
```

## Advantages & Disadvantages

| Pros | Cons |
|------|------|
| Isolates your code from API changes | Extra layer of indirection |
| Type-safe internal models | Maintenance overhead for each new API |
| Easy to test and mock | May add performance overhead |
| Composable for complex transformations | Debugging can be harder |
| Consistent data contracts | |

## Performance Considerations

For high-throughput scenarios:
- Cache adapter instances if stateless
- Minimize deep copying
- Consider using `__slots__` for adapter classes
- Profile serialization/deserialization overhead

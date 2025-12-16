# Facade Pattern

## Problem

Your **onboarding subsystem** involves multiple complex interactions:
- Identity service: create user account
- Billing service: provision subscription
- ParagoN service: register with external provider
- Notification service: send welcome email

**Without Facade**, controllers are cluttered with orchestration logic:

```python
# ❌ Complex, fragmented logic
@app.post("/onboard")
def onboard_user(user_data):
    # Call identity service
    identity_response = identity_client.create_user(user_data["email"])
    if not identity_response.success:
        return {"error": "Failed to create identity"}
    
    # Call billing service
    billing_response = billing_client.provision_subscription(identity_response.user_id)
    if not billing_response.success:
        # Rollback identity?
        return {"error": "Failed to provision billing"}
    
    # Call ParagoN
    paragon_response = paragon_client.register_user(user_data)
    if not paragon_response.success:
        # Rollback billing and identity?
        return {"error": "Failed to register with ParagoN"}
    
    # Call notifications
    notif_response = notification_client.send_welcome_email(user_data["email"])
    
    # Handle partial failures, rollbacks, etc...
```

This is messy, error-prone, and hard to reuse.

## Solution

Create a Facade that hides the complexity behind a simple high-level API:

```python
from typing import Dict, Any, Tuple
from enum import Enum

class OnboardingStatus(Enum):
    SUCCESS = "success"
    PARTIAL_FAILURE = "partial_failure"
    FAILURE = "failure"

class OnboardingResult:
    def __init__(self, status: OnboardingStatus, user_id: str = None, error: str = None):
        self.status = status
        self.user_id = user_id
        self.error = error
        self.details = {}

class OnboardingFacade:
    """High-level onboarding orchestration."""
    
    def __init__(self, identity_client, billing_client, paragon_client, notification_client):
        self.identity = identity_client
        self.billing = billing_client
        self.paragon = paragon_client
        self.notifications = notification_client
    
    def onboard_user(self, user_data: Dict[str, Any]) -> OnboardingResult:
        """Orchestrate complete onboarding process."""
        result = OnboardingResult(OnboardingStatus.SUCCESS)
        
        try:
            # Step 1: Create identity
            identity_response = self.identity.create_user(user_data["email"])
            if not identity_response.success:
                return OnboardingResult(
                    OnboardingStatus.FAILURE,
                    error=f"Identity creation failed: {identity_response.error}"
                )
            user_id = identity_response.user_id
            result.user_id = user_id
            result.details["identity"] = {"status": "success", "user_id": user_id}
            
            # Step 2: Provision billing
            billing_response = self.billing.provision_subscription(
                user_id,
                plan_id=user_data.get("plan_id", "standard")
            )
            if not billing_response.success:
                # Partial failure: rollback identity
                self._rollback_identity(user_id)
                return OnboardingResult(
                    OnboardingStatus.FAILURE,
                    error=f"Billing provisioning failed: {billing_response.error}"
                )
            result.details["billing"] = {"status": "success", "subscription_id": billing_response.subscription_id}
            
            # Step 3: Register with ParagoN
            try:
                paragon_response = self.paragon.register_user(user_data)
                if paragon_response.success:
                    result.details["paragon"] = {"status": "success"}
                else:
                    # Non-critical failure: mark as partial
                    result.status = OnboardingStatus.PARTIAL_FAILURE
                    result.details["paragon"] = {"status": "failed", "error": paragon_response.error}
            except Exception as e:
                # Log but continue
                result.status = OnboardingStatus.PARTIAL_FAILURE
                result.details["paragon"] = {"status": "error", "message": str(e)}
            
            # Step 4: Send welcome email (fire-and-forget)
            try:
                self.notifications.send_welcome_email(
                    email=user_data["email"],
                    user_id=user_id
                )
                result.details["notifications"] = {"status": "sent"}
            except Exception as e:
                # Log but don't fail onboarding
                result.details["notifications"] = {"status": "failed", "message": str(e)}
            
            return result
        
        except Exception as e:
            return OnboardingResult(
                OnboardingStatus.FAILURE,
                error=f"Unexpected error: {str(e)}"
            )
    
    def _rollback_identity(self, user_id: str):
        """Rollback identity creation on failure."""
        try:
            self.identity.delete_user(user_id)
        except Exception as e:
            # Log rollback failure
            print(f"Rollback failed for user {user_id}: {e}")


# Usage
facade = OnboardingFacade(
    identity_client=IdentityClient(),
    billing_client=BillingClient(),
    paragon_client=ParagoNClient(),
    notification_client=NotificationClient(),
)

# Controllers are now clean
@app.post("/onboard")
def onboard_user_handler(user_data: Dict):
    result = facade.onboard_user(user_data)
    
    if result.status == OnboardingStatus.SUCCESS:
        return {"success": True, "user_id": result.user_id}
    elif result.status == OnboardingStatus.PARTIAL_FAILURE:
        return {"success": True, "user_id": result.user_id, "warnings": result.details}
    else:
        return {"success": False, "error": result.error}, 400
```

## Advantages

| Pros | Cons |
|------|------|
| Hides complex orchestration | Can become complex itself over time |
| Reusable across controllers | Might do too much (God object) |
| Clean error handling and rollback | Hard to test all failure paths |
| Idempotent operations | Performance overhead of abstraction |
| Easy to extend | |

## Testing

```python
class MockOnboardingFacade(OnboardingFacade):
    """Mock facade for testing."""
    
    def onboard_user(self, user_data):
        # Return success immediately
        return OnboardingResult(
            OnboardingStatus.SUCCESS,
            user_id="mock_user_123"
        )

@pytest.fixture
def onboarding_facade():
    return MockOnboardingFacade(
        None, None, None, None  # All mocked
    )

def test_onboarding_success(onboarding_facade):
    result = onboarding_facade.onboard_user({"email": "test@example.com"})
    assert result.status == OnboardingStatus.SUCCESS
```

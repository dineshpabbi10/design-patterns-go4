# State Pattern

## Problem

You are designing an Order Lifecycle State Machine for a distributed, microservice-based system. An order is processed by multiple independent services (Validation, Provisioning, Billing, etc.), each responsible for a specific step in the lifecycle.

The system must ensure:

- Valid state transitions
- No illegal or out-of-order transitions
- Consistency despite retries, failures, and concurrent updates

Order Lifecycle States

An order can be in exactly one of the following states at any time:

- CREATED — Order accepted but not yet validated
- VALIDATED — Order data and prerequisites verified
- PROVISIONED — Resources successfully provisioned
- BILLED — Payment captured
- COMPLETED — Order fully processed
- FAILED — Order permanently failed (terminal state)

Transition Rules

Transitions must follow explicit, predefined rules:

| From State | Allowed Next States |
|------------|-------------------|
| CREATED | VALIDATED, FAILED |
| VALIDATED | PROVISIONED, FAILED |
| PROVISIONED | BILLED, FAILED |
| BILLED | COMPLETED, FAILED |
| COMPLETED | — (terminal) |
| FAILED | — (terminal) |

Any transition not listed above is invalid and must be rejected.

## Solution

Define an abstract `OrderState` class with methods for each possible action, and concrete state classes that implement the behavior for each state. Use an enum to define the states and a transition table to validate state changes.

```python
"""
Context

You are designing an Order Lifecycle State Machine for a distributed, microservice-based system.
An order is processed by multiple independent services (Validation, Provisioning, Billing, etc.), each responsible for a specific step in the lifecycle.

The system must ensure:

Valid state transitions

No illegal or out-of-order transitions

Consistency despite retries, failures, and concurrent updates

Order Lifecycle States

An order can be in exactly one of the following states at any time:

CREATED — Order accepted but not yet validated

VALIDATED — Order data and prerequisites verified

PROVISIONED — Resources successfully provisioned

BILLED — Payment captured

COMPLETED — Order fully processed

FAILED — Order permanently failed (terminal state)

Transition Rules

Transitions must follow explicit, predefined rules:

From State	Allowed Next States
CREATED	VALIDATED, FAILED
VALIDATED	PROVISIONED, FAILED
PROVISIONED	BILLED, FAILED
BILLED	COMPLETED, FAILED
COMPLETED	— (terminal)
FAILED	— (terminal)

Any transition not listed above is invalid and must be rejected.
"""

from enum import Enum, auto
from abc import ABC, abstractmethod


class OrderStateEnum(Enum):
    CREATED = auto()
    VALIDATED = auto()
    PROVISIONED = auto()
    BILLED = auto()
    COMPLETED = auto()
    FAILED = auto()


allowed_transitions = {
    OrderStateEnum.CREATED: [OrderStateEnum.VALIDATED, OrderStateEnum.FAILED],
    OrderStateEnum.VALIDATED: [OrderStateEnum.PROVISIONED, OrderStateEnum.FAILED],
    OrderStateEnum.PROVISIONED: [OrderStateEnum.BILLED, OrderStateEnum.FAILED],
    OrderStateEnum.BILLED: [OrderStateEnum.COMPLETED, OrderStateEnum.FAILED],
    OrderStateEnum.COMPLETED: [],
    OrderStateEnum.FAILED: [],
}


class Order:
    """Represents an order in the order lifecycle state machine."""

    def __init__(self) -> None:
        """Initialize the order with default state and flags."""
        self.state = CreateState()
        self.is_created = False
        self.is_validated = False
        self.is_provisioned = False
        self.is_billed = False
        self.is_completed = False
        self.is_failed = False

    def create_order(self) -> None:
        """Create the order, transitioning from CREATED to VALIDATED state."""
        self.state.create_order(self)

    def validate_order(self) -> None:
        """Validate the order, transitioning from VALIDATED to PROVISIONED state."""
        self.state.validate_order(self)

    def provision_order(self) -> None:
        """Provision the order, transitioning from PROVISIONED to BILLED state."""
        self.state.provision_order(self)

    def bill_order(self) -> None:
        """Bill the order, transitioning from BILLED to COMPLETED state."""
        self.state.bill_order(self)

    def complete_order(self) -> None:
        """Complete the order, marking it as fully processed."""
        self.state.complete_order(self)

    def set_state(self, new_state: "OrderState") -> None:
        """Set the new state if the transition is allowed.

        Args:
            new_state: The new state to transition to.

        Raises:
            Exception: If the state transition is not allowed.
        """
        if new_state.state in allowed_transitions[self.state.state]:
            self.state = new_state
        else:
            raise Exception(
                f"Invalid state transition from {self.state.state} to {new_state.state}"
            )


class OrderState(ABC):
    """Abstract base class for order states in the state machine."""

    def __init__(self, state_enum: OrderStateEnum) -> None:
        """Initialize the state with its enum value.

        Args:
            state_enum: The enum value representing this state.
        """
        self.state = state_enum

    @abstractmethod
    def create_order(self, order: Order) -> None:
        """Handle create_order action for this state.

        Args:
            order: The order object to operate on.
        """
        pass

    @abstractmethod
    def validate_order(self, order: Order) -> None:
        """Handle validate_order action for this state.

        Args:
            order: The order object to operate on.
        """
        pass

    @abstractmethod
    def provision_order(self, order: Order) -> None:
        """Handle provision_order action for this state.

        Args:
            order: The order object to operate on.
        """
        pass

    @abstractmethod
    def bill_order(self, order: Order) -> None:
        """Handle bill_order action for this state.

        Args:
            order: The order object to operate on.
        """
        pass

    @abstractmethod
    def complete_order(self, order: Order) -> None:
        """Handle complete_order action for this state.

        Args:
            order: The order object to operate on.
        """
        pass


class CreateState(OrderState):
    """Represents the CREATED state of an order."""

    def __init__(self) -> None:
        """Initialize the CREATED state."""
        super().__init__(OrderStateEnum.CREATED)

    def create_order(self, order: Order) -> None:
        """Create the order and transition to VALIDATED state.

        Args:
            order: The order object to create.

        Raises:
            Exception: If the order is already created.
        """
        if not order.is_created:
            order.is_created = True
            order.set_state(ValidateState())
            print("Order created and moved to VALIDATED state.")
        else:
            raise Exception("Order already created.")

    def validate_order(self, order: Order) -> None:
        """Validate order action - not allowed in CREATED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order must be created before validation.")

    def provision_order(self, order: Order) -> None:
        """Provision order action - not allowed in CREATED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order must be validated before provisioning.")

    def bill_order(self, order: Order) -> None:
        """Bill order action - not allowed in CREATED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order must be provisioned before billing.")

    def complete_order(self, order: Order) -> None:
        """Complete order action - not allowed in CREATED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order must be billed before completion.")


class ValidateState(OrderState):
    """Represents the VALIDATED state of an order."""

    def __init__(self) -> None:
        """Initialize the VALIDATED state."""
        super().__init__(OrderStateEnum.VALIDATED)

    def create_order(self, order: Order) -> None:
        """Create order action - not allowed in VALIDATED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order already created.")

    def validate_order(self, order: Order) -> None:
        """Validate the order and transition to PROVISIONED state.

        Args:
            order: The order object to validate.

        Raises:
            Exception: If the order is already validated.
        """
        if not order.is_validated:
            order.is_validated = True
            order.set_state(ProvisionState())
            print("Order validated and moved to PROVISIONED state.")
        else:
            raise Exception("Order already validated.")

    def provision_order(self, order: Order) -> None:
        """Provision order action - not allowed in VALIDATED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order must be validated before provisioning.")

    def bill_order(self, order: Order) -> None:
        """Bill order action - not allowed in VALIDATED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order must be provisioned before billing.")

    def complete_order(self, order: Order) -> None:
        """Complete order action - not allowed in VALIDATED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order must be billed before completion.")


class ProvisionState(OrderState):
    """Represents the PROVISIONED state of an order."""

    def __init__(self) -> None:
        """Initialize the PROVISIONED state."""
        super().__init__(OrderStateEnum.PROVISIONED)

    def create_order(self, order: Order) -> None:
        """Create order action - not allowed in PROVISIONED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order already created.")

    def validate_order(self, order: Order) -> None:
        """Validate order action - not allowed in PROVISIONED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order already validated.")

    def provision_order(self, order: Order) -> None:
        """Provision the order and transition to BILLED state.

        Args:
            order: The order object to provision.

        Raises:
            Exception: If the order is already provisioned.
        """
        if not order.is_provisioned:
            order.is_provisioned = True
            order.set_state(BillState())
            print("Order provisioned and moved to BILLED state.")
        else:
            raise Exception("Order already provisioned.")

    def bill_order(self, order: Order) -> None:
        """Bill order action - not allowed in PROVISIONED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order must be provisioned before billing.")

    def complete_order(self, order: Order) -> None:
        """Complete order action - not allowed in PROVISIONED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order must be billed before completion.")


class BillState(OrderState):
    """Represents the BILLED state of an order."""

    def __init__(self) -> None:
        """Initialize the BILLED state."""
        super().__init__(OrderStateEnum.BILLED)

    def create_order(self, order: Order) -> None:
        """Create order action - not allowed in BILLED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order already created.")

    def validate_order(self, order: Order) -> None:
        """Validate order action - not allowed in BILLED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order already validated.")

    def provision_order(self, order: Order) -> None:
        """Provision order action - not allowed in BILLED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order already provisioned.")

    def bill_order(self, order: Order) -> None:
        """Bill the order and transition to COMPLETED state.

        Args:
            order: The order object to bill.

        Raises:
            Exception: If the order is already billed.
        """
        if not order.is_billed:
            order.is_billed = True
            order.set_state(CompleteState())
            print("Order billed and moved to COMPLETED state.")
        else:
            raise Exception("Order already billed.")

    def complete_order(self, order: Order) -> None:
        """Complete order action - not allowed in BILLED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order must be billed before completion.")


class CompleteState(OrderState):
    """Represents the COMPLETED state of an order."""

    def __init__(self) -> None:
        """Initialize the COMPLETED state."""
        super().__init__(OrderStateEnum.COMPLETED)

    def create_order(self, order: Order) -> None:
        """Create order action - not allowed in COMPLETED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order already created.")

    def validate_order(self, order: Order) -> None:
        """Validate order action - not allowed in COMPLETED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order already validated.")

    def provision_order(self, order: Order) -> None:
        """Provision order action - not allowed in COMPLETED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order already provisioned.")

    def bill_order(self, order: Order) -> None:
        """Bill order action - not allowed in COMPLETED state.

        Args:
            order: The order object (unused).

        Raises:
            Exception: Always raised as this action is invalid in this state.
        """
        raise Exception("Order already billed.")

    def complete_order(self, order: Order) -> None:
        """Complete the order, marking it as fully processed.

        Args:
            order: The order object to complete.

        Raises:
            Exception: If the order is already completed.
        """
        if not order.is_completed:
            order.is_completed = True
            print("Order completed successfully.")
        else:
            raise Exception("Order already completed.")


# Example usage
if __name__ == "__main__":
    # Valid state transitions
    order = Order()

    try:
        order.create_order()
        order.validate_order()
        order.provision_order()
        order.bill_order()
        order.complete_order()
    except Exception as e:
        print(f"Error: {e}")

    # Invalid state transition
    order2 = Order()
    try:
        order2.validate_order()  # This should raise an exception
    except Exception as e:
        print(f"Error: {e}")
```

## When to Use

Use the State pattern when you have an object that behaves differently depending on its current state, and the state transitions are complex or need to be enforced. It's particularly useful for implementing state machines where:

- The object can be in one of several states
- The behavior changes based on the current state
- State transitions need to be controlled and validated
- You want to avoid large conditional statements in the main class

The State pattern helps avoid monolithic classes with many conditional statements and makes state transitions explicit and enforceable.</content>
<parameter name="filePath">/workspaces/design-patterns-gog/docs/behavioral/state.md
"""
Problem: You need to encapsulate complex operations (e.g., "create customer across services", "provision resources") as
commands that can be queued, retried, logged, and undone when possible. Design a `Command` object model that supports
asynchronous execution and persistent queuing.

Constraints & hints:
- Commands should be serializable to store in a durable queue.
- Support undo/compensating commands for failure recovery.
- Useful for implementing background workers and sagas across microservices.

Deliverable: specify the command interface and how commands are scheduled and retried in your system.
"""
from abc import ABC, abstractmethod
from enum import Enum
import random
import os

def simulate_failure():
    if random.random() < float(os.getenv("FAILURE_RATE", 0.3)):  # 30% chance to fail
        raise Exception("Simulated command failure")
class CommandTypes(str, Enum):
    CREATE_CUSTOMER = "create_customer"
    PROVISION_RESOURCES = "provision_resources"
    
class Command(ABC):
    """
    Abstract base class for commands that can be executed, undone, and serialized.
    """

    @abstractmethod
    async def execute(self):
        """
        Execute the command.
        """
        pass

    @abstractmethod
    async def undo(self):
        """
        Undo the command if possible.
        """
        pass

    @abstractmethod
    async def serialize(self) -> dict:
        """
        Serialize the command to a dictionary for storage.
        """
        pass

    @classmethod
    @abstractmethod
    async def deserialize(cls, data: dict) -> 'Command':
        """
        Deserialize a command from a dictionary.
        """
        pass

    def __str__(self):
        return f"{self.__class__.__name__}()"

class CreateCustomerCommand(Command):
    def __init__(self, customer_id: str, customer_data: dict):
        self.customer_id = customer_id
        self.customer_data = customer_data

    async def execute(self):
        simulate_failure()
        print(f"Creating customer {self.customer_id} with data {self.customer_data}")

    async def undo(self):
        print(f"Deleting customer {self.customer_id}")

    async def serialize(self) -> dict:
        return {
            "type": CommandTypes.CREATE_CUSTOMER,
            "customer_id": self.customer_id,
            "customer_data": self.customer_data
        }
    
    def __str__(self):
        return f"CreateCustomerCommand(customer_id={self.customer_id})"

    @classmethod
    async def deserialize(cls, data: dict) -> 'CreateCustomerCommand':
        return cls(customer_id=data["customer_id"], customer_data=data["customer_data"])

class ProvisionResourcesCommand(Command):
    def __init__(self, resource_id: str, resource_config: dict):
        self.resource_id = resource_id
        self.resource_config = resource_config

    async def execute(self):
        simulate_failure()
        print(f"Provisioning resources {self.resource_id} with config {self.resource_config}")

    async def undo(self):
        print(f"Deprovisioning resources {self.resource_id}")

    async def serialize(self) -> dict:
        return {
            "type": CommandTypes.PROVISION_RESOURCES,
            "resource_id": self.resource_id,
            "resource_config": self.resource_config
        }

    def __str__(self):
        return f"ProvisionResourcesCommand(resource_id={self.resource_id})"

    @classmethod
    async def deserialize(cls, data: dict) -> 'ProvisionResourcesCommand':
        return cls(resource_id=data["resource_id"], resource_config=data["resource_config"])
    
class CommandFactory:
    """
    Factory to create command instances from serialized data.
    """
    command_map = {
        CommandTypes.CREATE_CUSTOMER: CreateCustomerCommand,
        CommandTypes.PROVISION_RESOURCES: ProvisionResourcesCommand
    }

    @classmethod
    async def create_command(cls, data: dict) -> Command:
        command_type = data.get("type")
        command_class = cls.command_map.get(command_type)
        if not command_class:
            raise ValueError(f"Unknown command type: {command_type}")
        return await command_class.deserialize(data)

class CommandScheduler:
    """
    Schedules and retries commands.
    """
    def __init__(self):
        self.queue = []

    async def schedule(self, command: Command):
        serialized_command = await command.serialize()
        self.queue.append(serialized_command)
        print(f"Scheduled command: {serialized_command}")

    async def execute_next(self):
        if not self.queue:
            print("No commands to execute.")
            return

        serialized_command = self.queue.pop(0)
        command = await CommandFactory.create_command(serialized_command)
        try:
            await command.execute()
            print(f"Executed command: {serialized_command}")
        except Exception as e:
            print(f"Command execution failed: {e}. Attempting to undo.")
            await command.undo()
            print(f"Undid command: {serialized_command}")

# Example usage:

async def main():
    scheduler = CommandScheduler()
    command = CreateCustomerCommand(customer_id="123", customer_data={"name": "John Doe"})
    await scheduler.schedule(command)
    await scheduler.execute_next()
    # Another example usage:
    command2 = ProvisionResourcesCommand(resource_id="res-456", resource_config={"type": "vm", "size": "large"})
    await scheduler.schedule(command2)
    await scheduler.execute_next()
    
    # Test logging
    print("Testing command execution and logging.")
    print(command)
    print(command2)

import asyncio
if __name__ == "__main__":
    asyncio.run(main())


# Pytest
import pytest
import asyncio

@pytest.mark.asyncio
async def test_create_customer_command():
    os.environ["FAILURE_RATE"] = "0.0"
    command = CreateCustomerCommand(customer_id="test123", customer_data={"name": "Test User"})
    serialized = await command.serialize()
    deserialized_command = await CreateCustomerCommand.deserialize(serialized)
    assert command.customer_id == deserialized_command.customer_id
    assert command.customer_data == deserialized_command.customer_data
    await command.execute()
    await command.undo()

@pytest.mark.asyncio
async def test_provision_resources_command():
    os.environ["FAILURE_RATE"] = "0.0"
    command = ProvisionResourcesCommand(resource_id="res-test", resource_config={"type": "db", "size": "small"})
    serialized = await command.serialize()
    deserialized_command = await ProvisionResourcesCommand.deserialize(serialized)
    assert command.resource_id == deserialized_command.resource_id
    assert command.resource_config == deserialized_command.resource_config
    await command.execute()
    await command.undo()

@pytest.mark.asyncio
async def test_command_scheduler():
    os.environ["FAILURE_RATE"] = "0.0"
    scheduler = CommandScheduler()
    command = CreateCustomerCommand(customer_id="sched123", customer_data={"name": "Scheduler User"})
    await scheduler.schedule(command)
    assert len(scheduler.queue) == 1
    await scheduler.execute_next()
    assert len(scheduler.queue) == 0
    command2 = ProvisionResourcesCommand(resource_id="res-sched", resource_config={"type": "cache", "size": "medium"})
    await scheduler.schedule(command2)
    assert len(scheduler.queue) == 1
    await scheduler.execute_next()
    assert len(scheduler.queue) == 0

@pytest.mark.asyncio
async def test_command_logging(): 
    os.environ["FAILURE_RATE"] = "0.0"
    command = CreateCustomerCommand(customer_id="log123", customer_data={"name": "Log User"})
    assert str(command) == "CreateCustomerCommand(customer_id=log123)"
    command2 = ProvisionResourcesCommand(resource_id="res-log", resource_config={"type": "queue", "size": "large"})
    assert str(command2) == "ProvisionResourcesCommand(resource_id=res-log)"

@pytest.mark.asyncio
async def test_command_failure_and_undo():
    os.environ["FAILURE_RATE"] = "1.0"  # Force failure
    scheduler = CommandScheduler()
    command = CreateCustomerCommand(customer_id="fail123", customer_data={"name": "Fail User"})
    await scheduler.schedule(command)
    await scheduler.execute_next()  # This should fail and trigger undo

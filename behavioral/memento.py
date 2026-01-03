"""
Problem: Long-running data pipelines occasionally need checkpoints and the ability to rollback to a prior state when a
failed transformation corrupts downstream data. Design a `Memento` mechanism that captures checkpointed pipeline state
(including offsets, schema versions, and short-lived credentials) and allows safe restoration.

Constraints & hints:
- Mementos must be stored durably and be small enough to transfer between workers.
- Respect sensitive data handling—avoid storing secrets in plaintext.
- Useful for reproducible retries and disaster recovery.

Deliverable: describe what a `PipelineMemento` contains and how the orchestration layer applies it to resume or rollback.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import copy


class PipelineMemento:
    """A memento that captures the state of a data pipeline at a specific checkpoint.

    This class encapsulates the pipeline's state including offsets, schema versions,
    and credentials, providing a way to save and restore the state securely.
    """

    def __init__(
        self,
        offsets: Dict[str, Any],
        schema_versions: Dict[str, Any],
        credentials: Dict[str, str],
    ) -> None:
        """Initialize the PipelineMemento.

        Args:
            offsets: A dictionary mapping data source names to their current offsets.
            schema_versions: A dictionary mapping data source names to their schema versions.
            credentials: A dictionary of short-lived credentials (should be handled securely).
        """
        self._offsets = copy.deepcopy(offsets)
        self._schema_versions = copy.deepcopy(schema_versions)
        self._credentials = self._secure_credentials(credentials)

    def _secure_credentials(self, credentials: Dict[str, str]) -> Dict[str, str]:
        """Securely handle credentials (e.g., encrypt or mask sensitive data).

        Args:
            credentials: A dictionary of credentials.

        Returns:
            A secured version of the credentials.
        """
        # Placeholder for actual secure handling logic
        secured = {k: f"secured_{v}" for k, v in credentials.items()}
        return secured

    @property
    def offsets(self) -> Dict[str, Any]:
        """Get the stored offsets.

        Returns:
            A deep copy of the offsets dictionary.
        """
        return copy.deepcopy(self._offsets)

    @property
    def schema_versions(self) -> Dict[str, Any]:
        """Get the stored schema versions.

        Returns:
            A deep copy of the schema versions dictionary.
        """
        return copy.deepcopy(self._schema_versions)

    @property
    def credentials(self) -> Dict[str, str]:
        """Get the stored credentials.

        Returns:
            A deep copy of the credentials dictionary.
        """
        return copy.deepcopy(self._credentials)


class PipelineOrchestrator:
    """Orchestration layer that manages pipeline execution and state restoration.

    This class handles the creation of mementos for checkpointing and restoration
    of pipeline state in case of failures.
    """

    def __init__(self) -> None:
        """Initialize the PipelineOrchestrator with empty state."""
        self.current_offsets: Dict[str, Any] = {}
        self.current_schema_versions: Dict[str, Any] = {}
        self.current_credentials: Dict[str, str] = {}

    def create_memento(self) -> PipelineMemento:
        """Create a memento capturing the current pipeline state.

        Returns:
            A PipelineMemento object containing the current state.
        """
        return PipelineMemento(
            offsets=self.current_offsets,
            schema_versions=self.current_schema_versions,
            credentials=self.current_credentials,
        )

    def restore_from_memento(self, memento: PipelineMemento) -> None:
        """Restore the pipeline state from a given memento.

        Args:
            memento: The PipelineMemento to restore from.
        """
        self.current_offsets = memento.offsets
        self.current_schema_versions = memento.schema_versions
        self.current_credentials = memento.credentials
        print("Pipeline state restored from memento.")


# Example usage:
orchestrator = PipelineOrchestrator()
orchestrator.current_offsets = {"source1": 100, "source2": 200}
orchestrator.current_schema_versions = {"source1": "v1.2", "source2": "v3.4"}
orchestrator.current_credentials = {"db_user": "user123", "db_pass": "pass123"}
memento = orchestrator.create_memento()

# Simulate a failure and restore from memento
orchestrator.current_offsets = {}
orchestrator.current_schema_versions = {}
orchestrator.current_credentials = {}
orchestrator.restore_from_memento(memento)
print(f"Current Offsets: {orchestrator.current_offsets}")
print(f"Current Schema Versions: {orchestrator.current_schema_versions}")
print(f"Current Credentials: {orchestrator.current_credentials}")


# Unit tests with pytest
def test_pipeline_memento_creation_and_restoration():
    orchestrator = PipelineOrchestrator()
    orchestrator.current_offsets = {"sourceA": 50, "sourceB": 75}
    orchestrator.current_schema_versions = {"sourceA": "v2.0", "sourceB": "v1.5"}
    orchestrator.current_credentials = {"api_key": "key123", "api_secret": "secret123"}

    memento = orchestrator.create_memento()

    # Change current state
    orchestrator.current_offsets = {}
    orchestrator.current_schema_versions = {}
    orchestrator.current_credentials = {}

    # Restore from memento
    orchestrator.restore_from_memento(memento)

    assert orchestrator.current_offsets == {"sourceA": 50, "sourceB": 75}
    assert orchestrator.current_schema_versions == {
        "sourceA": "v2.0",
        "sourceB": "v1.5",
    }
    assert orchestrator.current_credentials == {
        "api_key": "secured_key123",
        "api_secret": "secured_secret123",
    }

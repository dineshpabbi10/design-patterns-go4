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
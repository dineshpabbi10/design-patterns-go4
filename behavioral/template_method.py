"""
Problem: Define a `TemplateMethod` for ETL jobs where the high-level algorithm is fixed (extract -> transform -> load),
but specific steps vary per dataset. Provide base skeleton and subclass hooks for dataset-specific behavior.

Constraints & hints:
- Template should enforce common pre/post steps like validation and monitoring.
- Allow subclasses to override transform and enrichment steps safely.
- Useful for maintaining consistent lifecycle across many pipelines.

Deliverable: sketch the base ETL template and an example subclass for a specific data source.
"""
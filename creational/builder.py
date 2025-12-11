"""
Problem: Define a `SparkJobBuilder` that assembles complex Spark job configurations for your data pipelines. Jobs
have many optional parts: input sources, transforms, windowing, triggers, resource settings, and monitoring hooks.
Create a builder that produces an immutable job spec used by the pipeline runner.

Constraints & hints:
- Many fields are optional; builder should allow fluent chaining.
- Final spec must be serializable and versioned for reproducible runs.
- Builders help in generating similar jobs programmatically from templates.

Deliverable: implement a `SparkJobBuilder` API that callers in orchestration code can use to produce job specs.
"""
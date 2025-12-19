"""
Problem: Create a small domain-specific language (DSL) for expressing data transformations your team uses in Spark
pipelines (e.g., filter, map, join, window). Implement an interpreter that can parse the DSL and produce an executable
plan for the Spark runner.

Constraints & hints:
- DSL should be expressive but constrained to safe operations.
- Interpreter output should be validated before execution.
- Useful for letting data engineers describe jobs declaratively.

Deliverable: outline the DSL grammar and the interpreter API that converts DSL scripts into Spark job specs.
"""

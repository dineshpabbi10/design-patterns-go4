"""
Problem: In your ETL orchestration, you often need to create variations of complex pipeline configurations rapidly. Design
a prototype mechanism to clone pipeline job specs (or client config objects) and customize a few fields without rebuilding
from scratch.

Constraints & hints:
- Cloning should be efficient and allow shallow or deep copy semantics where appropriate.
- Preserve provenance metadata so clones record their origin.
- Useful for templated jobs or spinning up test instances of real jobs.

Deliverable: show how a `PipelineSpec` prototype can be copied and mutated safely before submission.
"""
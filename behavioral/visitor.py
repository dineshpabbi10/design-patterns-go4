"""
Problem: You need to perform different operations over a tree-like structure of configuration nodes (e.g., validation,
metrics collection, migration). Implement a `Visitor` that can traverse config trees and run operations without
modifying the tree classes.

Constraints & hints:
- Visitors should be easy to add for new operations.
- Traversal should support pre/post-order hooks and short-circuiting.
- Useful for decoupling operations from the data model.

Deliverable: define the visitor interface and an example visitor for validating config versions.
"""

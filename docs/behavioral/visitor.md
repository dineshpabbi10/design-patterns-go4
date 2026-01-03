# Visitor Pattern

## Problem

You need to perform different operations over a tree-like structure of configuration nodes (e.g., validation, metrics collection, migration). Implement a `Visitor` that can traverse config trees and run operations without modifying the tree classes.

Constraints & hints:
- Visitors should be easy to add for new operations.
- Traversal should support pre/post-order hooks and short-circuiting.
- Useful for decoupling operations from the data model.

Deliverable: define the visitor interface and an example visitor for validating config versions.

## Solution

Define an abstract `ConfigVisitor` class with `pre_hook`, `post_hook`, and `visit` methods, and a `traverse` method for tree traversal. Define an abstract `ConfigNode` class with an `accept` method. Implement concrete nodes and visitors.

```python
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

from abc import ABC, abstractmethod
from typing import List, Optional


class ConfigNode(ABC):
    """Abstract base class for configuration nodes in a tree structure."""

    def __init__(self, children: Optional[List["ConfigNode"]] = None):
        """Initialize a ConfigNode with optional children."""
        self.children = children

    @abstractmethod
    def accept(self, visitor: "ConfigVisitor") -> None:
        """Accept a visitor to perform operations on this node."""
        pass


class ConcreteConfigNode(ConfigNode):
    """A concrete configuration node with a name and version."""

    def __init__(
        self, name: str, version: int, children: Optional[List["ConfigNode"]] = None
    ):
        self.name = name
        self.version = version
        super().__init__(children)

    def accept(self, visitor: "ConfigVisitor") -> None:
        visitor.traverse(self)


class ConfigVisitor(ABC):
    """Abstract base class for visitors that can operate on ConfigNode objects."""

    @abstractmethod
    def pre_hook(self) -> bool:
        """Pre-hook method called before visiting a node. Return True to continue traversal."""
        pass

    @abstractmethod
    def post_hook(self) -> None:
        """Post-hook method called after visiting a node and its children."""
        pass

    @abstractmethod
    def visit(self, node: ConfigNode) -> None:
        """Visit a specific node and perform operations on it."""
        pass

    def traverse(self, node: ConfigNode) -> None:
        """Traverse the tree starting from the given node, calling hooks and visit."""
        # Pre hook for short circuiting the traversal
        if self.pre_hook():
            self.visit(node)

            if node.children:
                for c in node.children:
                    self.traverse(c)

        self.post_hook()


class VersionValidationVisitor(ConfigVisitor):
    """Visitor that validates the version of all ConfigNode objects in a tree."""

    def __init__(self, version_id: int) -> None:
        """Initialize the visitor with the expected version ID."""
        self.is_valid = True
        self.version_id = version_id

    def pre_hook(self) -> bool:
        """Pre-hook to check if traversal should continue. Returns True if valid so far."""
        return self.is_valid

    def post_hook(self) -> None:
        """Post-hook called after traversal. No operation needed."""
        pass

    def visit(self, node: ConfigNode) -> None:
        """Visit a node and validate its version if it's a ConcreteConfigNode."""
        if isinstance(node, ConcreteConfigNode):
            if node.version != self.version_id:
                print("Version mismatch found")
                self.is_valid = False
        else:
            print("Unknown node type encountered during validation.")
            self.is_valid = False


# Example usage:
if __name__ == "__main__":
    # Create a sample config tree
    root = ConcreteConfigNode(
        "root",
        1,
        [
            ConcreteConfigNode("child1", 1),
            ConcreteConfigNode("child2", 2),  # This will cause a version mismatch
        ],
    )

    # Create a visitor for version validation
    validator = VersionValidationVisitor(version_id=1)

    # Traverse the config tree with the visitor
    root.accept(validator)

    if validator.is_valid:
        print("All config nodes have the correct version.")
    else:
        print("Some config nodes have incorrect versions.")

    # Valid case
    valid_root = ConcreteConfigNode(
        "root", 1, [ConcreteConfigNode("child1", 1), ConcreteConfigNode("child2", 1)]
    )
    valid_validator = VersionValidationVisitor(version_id=1)
    valid_root.accept(valid_validator)
    if valid_validator.is_valid:
        print("All config nodes have the correct version.")
    else:
        print("Some config nodes have incorrect versions.")


# Unit tests with pytest
import pytest


def test_version_validation_visitor():
    # Create a sample config tree with matching versions
    root = ConcreteConfigNode(
        "root", 1, [ConcreteConfigNode("child1", 1), ConcreteConfigNode("child2", 1)]
    )

    validator = VersionValidationVisitor(version_id=1)
    root.accept(validator)
    assert validator.is_valid == True

    # Create a sample config tree with a version mismatch
    root_mismatch = ConcreteConfigNode(
        "root",
        1,
        [
            ConcreteConfigNode("child1", 1),
            ConcreteConfigNode("child2", 2),  # Mismatch here
        ],
    )

    validator_mismatch = VersionValidationVisitor(version_id=1)
    root_mismatch.accept(validator_mismatch)
    assert validator_mismatch.is_valid == False
```

## When to Use

Use the Visitor pattern when you need to perform operations on elements of a complex object structure without modifying the classes of the elements. It's particularly useful for tree-like structures where you want to add new operations without changing the node classes, and when operations involve different types of nodes that require type-specific behavior.</content>
<parameter name="filePath">/workspaces/design-patterns-gog/docs/behavioral/visitor.md
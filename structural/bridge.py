"""
Problem: Your ingestion logic must support multiple storage backends (S3, GCS, local FS). Implement a bridge that
decouples the ingestion `Abstraction` (e.g., `IngestJob`) from concrete `Implementation`s (S3Client, GCSClient),
allowing the two to vary independently.

Constraints & hints:
- New storage backends should be pluggable without changing ingestion logic.
- The bridge should minimize data-copying overhead.
- Useful for testing with local mocks and for multi-cloud deployments.

Deliverable: show the abstraction API and how to bind it to different storage implementations at runtime.
"""
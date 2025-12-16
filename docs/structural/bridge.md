# Bridge Pattern

## Problem

Your **ingestion logic** must support multiple storage backends:
- **Production**: S3 for large-scale data storage
- **Testing/Dev**: Local filesystem for quick iteration
- **Multi-cloud**: GCS for Google Cloud deployments

**Without Bridge**, you'd have conditional logic sprinkled everywhere:

```python
# ❌ Tight coupling to specific backends
def ingest_data(backend_type, data):
    if backend_type == "s3":
        s3 = boto3.client("s3")
        s3.put_object(Bucket="my-bucket", Key="data", Body=data)
    elif backend_type == "local":
        with open("/data/local", "wb") as f:
            f.write(data)
    elif backend_type == "gcs":
        gcs = storage.Client()
        bucket = gcs.bucket("my-bucket")
        blob = bucket.blob("data")
        blob.upload_from_string(data)
```

**Problem**: Ingestion logic is tightly coupled to storage implementation.

## Solution

Use **Bridge** to decouple **abstraction** (ingestion job) from **implementation** (storage backend):

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, BinaryIO
import boto3
from google.cloud import storage as gcs_storage
import os

# Implementation interface (storage backends)
class StorageImplementation(ABC):
    """Abstract storage backend."""
    
    @abstractmethod
    def write(self, key: str, data: bytes) -> None:
        """Write data to storage."""
        raise NotImplementedError
    
    @abstractmethod
    def read(self, key: str) -> bytes:
        """Read data from storage."""
        raise NotImplementedError
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        raise NotImplementedError


# Concrete implementations
class S3Storage(StorageImplementation):
    """S3 backend implementation."""
    
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.client = boto3.client("s3", region_name=region)
    
    def write(self, key: str, data: bytes) -> None:
        self.client.put_object(Bucket=self.bucket_name, Key=key, Body=data)
    
    def read(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket_name, Key=key)
        return response["Body"].read()
    
    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False


class LocalStorage(StorageImplementation):
    """Local filesystem backend implementation."""
    
    def __init__(self, base_path: str = "/data"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def write(self, key: str, data: bytes) -> None:
        file_path = os.path.join(self.base_path, key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(data)
    
    def read(self, key: str) -> bytes:
        file_path = os.path.join(self.base_path, key)
        with open(file_path, "rb") as f:
            return f.read()
    
    def exists(self, key: str) -> bool:
        return os.path.exists(os.path.join(self.base_path, key))


class GCSStorage(StorageImplementation):
    """Google Cloud Storage backend implementation."""
    
    def __init__(self, bucket_name: str, project_id: str = None):
        self.bucket_name = bucket_name
        if project_id:
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        self.client = gcs_storage.Client()
        self.bucket = self.client.bucket(bucket_name)
    
    def write(self, key: str, data: bytes) -> None:
        blob = self.bucket.blob(key)
        blob.upload_from_string(data)
    
    def read(self, key: str) -> bytes:
        blob = self.bucket.blob(key)
        return blob.download_as_bytes()
    
    def exists(self, key: str) -> bool:
        blob = self.bucket.blob(key)
        return blob.exists()


# Abstraction (ingestion logic)
class IngestJob:
    """Ingestion job - independent of storage backend."""
    
    def __init__(self, storage: StorageImplementation, job_config: Dict[str, Any]):
        self.storage = storage  # Bridge to implementation
        self.config = job_config
    
    def ingest(self, source_data: bytes, destination_key: str) -> None:
        """Ingest data - storage backend is pluggable."""
        print(f"Ingesting data to {destination_key}...")
        
        # Check if already exists (idempotency)
        if self.storage.exists(destination_key):
            print(f"Data already exists at {destination_key}, skipping...")
            return
        
        # Write to storage (backend-agnostic)
        self.storage.write(destination_key, source_data)
        print(f"Successfully wrote to {destination_key}")
    
    def process_batch(self, batch_items: list) -> None:
        """Process multiple items."""
        for item in batch_items:
            self.ingest(item["data"], item["key"])
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return job metadata."""
        return {
            "name": self.config.get("name"),
            "backend": self.storage.__class__.__name__,
            "status": "running",
        }
```

## Usage: Pluggable Storage Backends

```python
# Production: use S3
prod_storage = S3Storage(bucket_name="prod-data-lake", region="us-west-2")
prod_job = IngestJob(prod_storage, {"name": "prod_etl"})
prod_job.ingest(b"production data", "2025-12-16/customer_data.parquet")

# Testing: use local filesystem
test_storage = LocalStorage(base_path="/tmp/test-data")
test_job = IngestJob(test_storage, {"name": "test_etl"})
test_job.ingest(b"test data", "2025-12-16/customer_data.parquet")

# Multi-cloud: use GCS
gcs_storage = GCSStorage(bucket_name="multi-cloud-data")
gcs_job = IngestJob(gcs_storage, {"name": "gcs_etl"})
gcs_job.ingest(b"gcs data", "2025-12-16/customer_data.parquet")

# Same ingestion logic, different backends!
```

## Benefits

| Pros | Cons |
|------|------|
| Decouple job logic from storage | Extra abstraction layers |
| Add new backends without changing job code | More code upfront |
| Easy to test with mock storage | Potential performance overhead |
| Swap backends at runtime | Interface mismatches between backends |
| Support multi-cloud deployments | |

## Advanced: Storage Factory

```python
def create_storage(backend_type: str, **config) -> StorageImplementation:
    """Factory for creating storage backends."""
    backends = {
        "s3": lambda: S3Storage(**config),
        "local": lambda: LocalStorage(**config),
        "gcs": lambda: GCSStorage(**config),
    }
    
    if backend_type not in backends:
        raise ValueError(f"Unknown storage backend: {backend_type}")
    
    return backends[backend_type]()

# Configuration-driven backend selection
backend_type = os.getenv("STORAGE_BACKEND", "s3")
storage = create_storage(backend_type, bucket_name="my-bucket")
job = IngestJob(storage, {"name": "my_job"})
```

"""Use cases.

Each module here implements one application use case, such as
validating and ingesting a dataset. Use cases depend only on ports,
never on concrete adapters.
"""

from src.application.use_cases.validate_and_ingest_dataset import ValidateAndIngestDataset

__all__ = ["ValidateAndIngestDataset"]

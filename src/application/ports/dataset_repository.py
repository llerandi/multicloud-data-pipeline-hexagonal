"""DatasetRepository port.

Persists a dataset that has already passed validation. Adapters
implement this against a specific destination (BigQuery, Postgres).

rows is typed as a sequence of plain mappings (dict-like objects), one
per record, instead of a dataframe type. That keeps this port free of
any dependency on pandas or a specific dataframe library, the
application layer only needs to move data, not analyze it.
"""

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence


class DatasetRepository(ABC):
    """Abstract contract for storing a validated dataset."""

    @abstractmethod
    def save(self, dataset_name: str, rows: Sequence[Mapping[str, Any]]) -> None:
        """Persist rows under dataset_name.

        dataset_name identifies the destination table or collection.
        What that means (a BigQuery table id, a Postgres table name)
        is up to each adapter.
        """
        raise NotImplementedError

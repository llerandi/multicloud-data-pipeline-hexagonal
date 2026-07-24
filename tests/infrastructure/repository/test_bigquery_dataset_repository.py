"""Unit tests for BigqueryDatasetRepository.

FakeBigQueryClient implements just the one method this adapter calls,
insert_rows_json, and lets each test control what it returns, an empty
list for success or a list of error dicts for a partial failure, the
same shape the real google-cloud-bigquery client returns. Since the
adapter never imports that package, none of these tests need it
installed either.
"""

import pytest

from src.application.ports import DatasetRepository
from src.infrastructure.repository import BigqueryDatasetRepository


class FakeBigQueryClient:
    def __init__(self, errors_to_return=None):
        self.calls = []
        self._errors_to_return = errors_to_return if errors_to_return is not None else []

    def insert_rows_json(self, table_id, rows):
        self.calls.append((table_id, rows))
        return self._errors_to_return


def test_bigquery_dataset_repository_is_a_dataset_repository():
    assert issubclass(BigqueryDatasetRepository, DatasetRepository)


def test_save_does_nothing_for_an_empty_list_of_rows():
    client = FakeBigQueryClient()
    repository = BigqueryDatasetRepository(client, dataset_id="analytics")

    repository.save("customers", [])

    assert client.calls == []


def test_save_inserts_into_the_fully_qualified_table_id():
    client = FakeBigQueryClient()
    repository = BigqueryDatasetRepository(client, dataset_id="analytics")

    rows = [{"id": "1", "email": "a@b.com"}, {"id": "2", "email": "c@d.com"}]
    repository.save("customers", rows)

    assert len(client.calls) == 1
    table_id, sent_rows = client.calls[0]
    assert table_id == "analytics.customers"
    assert sent_rows == rows


def test_save_raises_when_bigquery_returns_row_errors():
    row_errors = [{"index": 1, "errors": [{"reason": "invalid", "message": "bad email"}]}]
    client = FakeBigQueryClient(errors_to_return=row_errors)
    repository = BigqueryDatasetRepository(client, dataset_id="analytics")

    with pytest.raises(RuntimeError) as exc_info:
        repository.save("customers", [{"id": "1", "email": "not-an-email"}])

    # The raised error should carry BigQuery's own error detail, not just
    # a generic "something went wrong", so whoever reads it (a log, a
    # notification) can actually tell what BigQuery rejected and why.
    assert "bad email" in str(exc_info.value)
    assert "analytics.customers" in str(exc_info.value)


def test_save_does_not_raise_when_bigquery_returns_no_errors():
    client = FakeBigQueryClient(errors_to_return=[])
    repository = BigqueryDatasetRepository(client, dataset_id="analytics")

    repository.save("customers", [{"id": "1", "email": "a@b.com"}])

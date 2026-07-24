"""BigqueryDatasetRepository: a DatasetRepository adapter backed by BigQuery.

Same reasoning as PostgresDatasetRepository: this module does not import
google-cloud-bigquery at all. It only calls .insert_rows_json(table_id,
rows) on whatever client object it is given, the one method any object
shaped like a google.cloud.bigquery.Client needs to expose for this
adapter to work.
"""

from typing import Any, Mapping, Sequence

from src.application.ports import DatasetRepository


class BigqueryDatasetRepository(DatasetRepository):
    """Inserts rows into a BigQuery table using a caller-supplied client.

    client is expected to already be authenticated against a specific
    GCP project, built by whoever constructs this class, same role a
    connection plays for PostgresDatasetRepository.

    dataset_id is BigQuery's own "dataset", a namespace that groups
    tables inside a project, for example "analytics". This is an
    unfortunate but unavoidable name collision: everywhere else in this
    project, "dataset" means the CSV or JSON file being validated and
    ingested. Here, for one constructor argument, it means BigQuery's
    own grouping concept instead, because that is what BigQuery calls
    it and renaming it in this adapter would only make the official
    BigQuery documentation harder to match against this code, not
    easier. save's own dataset_name parameter keeps its usual meaning,
    the two together form the fully qualified table id.
    """

    def __init__(self, client: Any, dataset_id: str) -> None:
        self._client = client
        self._dataset_id = dataset_id

    def save(self, dataset_name: str, rows: Sequence[Mapping[str, Any]]) -> None:
        """Insert rows into the table dataset_id.dataset_name.

        Does nothing for an empty sequence of rows, same reasoning as
        PostgresDatasetRepository, there is nothing to insert.

        Unlike Postgres or either FileStorage adapter, a failed insert
        here does not raise on its own. BigQuery's insert_rows_json
        returns a list describing which specific rows were rejected and
        why, instead of raising, a row-level partial failure is a
        normal, expected outcome of that call, not an exceptional one.
        Left alone, that list would be silently discarded and this
        method would look like it succeeded even if every single row
        was rejected, which is exactly backwards for a project whose
        entire point is catching bad data. So this adapter checks that
        list itself and raises if it is not empty, translating
        BigQuery's return-errors-as-data convention into the same
        raise-on-failure behavior every other adapter in this project
        already has.
        """
        if not rows:
            return

        table_id = f"{self._dataset_id}.{dataset_name}"
        errors = self._client.insert_rows_json(table_id, list(rows))

        if errors:
            raise RuntimeError(
                f"BigQuery rejected some rows when inserting into {table_id}: {errors}"
            )

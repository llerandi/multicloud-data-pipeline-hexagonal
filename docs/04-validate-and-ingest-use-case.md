# PR 4: ValidateAndIngestDataset use case

Branch: `feature/validate-and-ingest-use-case`

Files added: `src/domain/rules.py`, `tests/domain/test_rules.py`,
`src/application/use_cases/validate_and_ingest_dataset.py`,
`src/application/use_cases/__init__.py` (updated),
`tests/application/use_cases/test_validate_and_ingest_dataset.py`.

## Where "compute the report from rows" belongs, and why it is not on the use case

The ports PR left `DataQualityReport` able to judge whether a report is
acceptable, but nothing yet built the report itself from actual data.
That logic lives in a new `src/domain/rules.py`, not inside the use case,
and not as a method on `DataQualityReport`.

The reasoning: deciding what counts as a null value, or what counts as a
duplicate row, is a business decision, the same kind of decision as "5%
nulls is too many". It has nothing to do with GCS, BigQuery, or CSV
parsing, so it belongs in the domain layer, testable on its own, with
plain dictionaries as input, no file storage or use case involved. It is a
separate function rather than a method on `DataQualityReport` because
building a report from rows and asking an existing report whether it is
acceptable are two different responsibilities. Keeping them apart means a
future second way of building a report (from a database query result,
for example) would not need to touch `DataQualityReport` at all.

## Why null detection checks both `None` and `""`

```python
def _has_null_value(row: Mapping[str, Any]) -> bool:
    return any(value is None or value == "" for value in row.values())
```

The two file formats this pipeline reads represent "missing" differently.
A JSON `null` becomes Python `None` after parsing. A CSV file has no
concept of null at all, an empty field becomes an empty string. If this
check only looked for `None`, every missing value coming from a CSV file
would silently not count as null, and the 5% rule would be checking a
number that does not mean what it claims to mean. Checking for both is
what makes the rule behave the same regardless of which file format a
dataset arrived in.

Note what does not count: `0` and `False` are real values, not missing
data, `_has_null_value` explicitly does not treat them as null. Getting
this wrong (for example by checking `if value:` instead of
`if value is None or value == ""`) is an easy way to over-count nulls in a
dataset that legitimately has zero or false values, so `test_zero_and_false_do_not_count_as_null`
exists specifically to lock that in.

## How duplicates are counted

```python
def _count_duplicates(rows):
    seen = set()
    duplicates = 0
    for row in rows:
        key = tuple(sorted(row.items()))
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return duplicates
```

Two things worth noticing. First, the first occurrence of a row is never
counted, only repeats are, three identical rows count as two duplicates,
not three, which matches how most people would describe "how many
duplicates are there". Second, `row.items()` is sorted before being turned
into a set key. A plain `dict` does not guarantee key order is meaningful
for equality purposes here, sorting means two rows with the exact same
values, but whose keys happened to come back in a different order from
whatever parser produced them, still compare as the same row.

## Why `out_of_range_count` is hardcoded to 0

Deciding whether a value is "out of range" needs a schema: an expected
type and bounds for each column. This project has not designed a schema
representation yet, that is future work. `compute_quality_report` returns
`out_of_range_count=0` explicitly, with a comment explaining why, rather
than a real computation, because a fake computation that always says
"nothing is out of range" would look identical to a real one that checked
and found nothing wrong. Being honest that the check has not run yet
matters more than making the report look more complete than it is.

## Why file parsing lives in the use case, not in the domain

`ValidateAndIngestDataset._parse_rows` turns raw CSV or JSON bytes into a
list of dictionaries. This is deliberately not in `src/domain`, unlike the
null and duplicate counting. Parsing a specific file format is a technical
detail of how this particular pipeline ingests data, it is not a business
rule, nothing about "how do you read a CSV file" reflects a decision the
business cares about. It also is not in `src/infrastructure`, because it
does not depend on any specific cloud provider or database either, it only
depends on the Python standard library (`csv`, `json`, `io`). For now it
lives as a private method on the use case that needs it. If a second use
case needs the same parsing later, it is a small, safe refactor to pull it
out into its own module, there is no cost today to not doing that
prematurely.

## Why the constructor takes four ports and an optional thresholds argument

```python
def __init__(
    self,
    file_storage: FileStorage,
    dataset_repository: DatasetRepository,
    metrics_publisher: MetricsPublisher,
    notification_port: NotificationPort,
    thresholds: Optional[QualityThresholds] = None,
) -> None:
    ...
    self._thresholds = thresholds or QualityThresholds()
```

This is dependency injection: the use case receives its four
dependencies as constructor arguments, it does not construct a GCS
client or a BigQuery client itself anywhere inside its own code. That is
what makes it possible to test this class completely, exercising the real
`execute` method, using in-memory fakes instead of any real cloud
service, and it is what will make it possible to run the exact same use
case against GCS+BigQuery in one environment and S3+Postgres in another,
without changing this file at all.

`thresholds` defaults to `None` and falls back to `QualityThresholds()`
(5% by default) inside the constructor, rather than every caller having
to pass `QualityThresholds()` explicitly. `test_execute_accepts_custom_thresholds`
exists to prove this is a real, used parameter and not a value that looks
configurable but is actually ignored: it feeds the use case a dataset
with a 67% null ratio, once with the default threshold (rejected) and
once with an explicit `QualityThresholds(max_null_ratio=0.9)` (accepted).

## Why the tests use real subclasses of the ports instead of a mocking library

```python
class FakeFileStorage(FileStorage):
    def __init__(self, files):
        self._files = files
    def read(self, path):
        return self._files[path]
```

Each fake in the test file is written as `class Fake... (RealPort)`, not
as a `Mock()` or a `MagicMock()`. This means the test file itself would
fail to even import if a fake forgot to implement one of the port's
abstract methods, the same `abc` enforcement described in the ports PR
protects these tests too. A generic mock would happily accept any method
call, real or not, and would not catch a typo in a method name the way a
real subclass does.

## What each test scenario is actually checking

`test_execute_saves_and_publishes_metrics_for_a_valid_csv_dataset` and
its JSON counterpart check the whole happy path end to end: parsing,
building the report, saving, and publishing all happened, and none of the
failure-only behavior did. `test_execute_rejects_a_dataset_with_too_many_nulls_and_notifies`
checks the opposite: the exception was raised, the notifier was called
exactly once, and, just as importantly, that the repository and the
publisher were **not** called, a rejected dataset must not be
half-persisted or have its metrics published as if it were fine.
`test_execute_raises_for_unsupported_file_extension` checks the pipeline
fails loudly for a file type it was never asked to support, rather than
silently treating it as empty.

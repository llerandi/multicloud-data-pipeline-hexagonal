"""Domain rules that derive a DataQualityReport from raw rows.

Still plain Python only, same restriction as the rest of the domain
layer: rows are generic mappings, there is no dependency on how they
were read (CSV, JSON, a database cursor) or where they will be stored.
"""

from typing import Any, Mapping, Sequence

from src.domain.models import DataQualityReport


def compute_quality_report(rows: Sequence[Mapping[str, Any]]) -> DataQualityReport:
    """Count nulls and duplicates in rows and build a DataQualityReport.

    out_of_range_count is always 0 for now. Deciding whether a value is
    out of range requires a schema, an expected type and bounds per
    column, and this project has not defined one yet. Leaving the count
    at 0 rather than guessing keeps the report honest about what was
    actually checked, instead of silently claiming a check that never
    ran.
    """
    total_rows = len(rows)
    null_count = sum(1 for row in rows if _has_null_value(row))
    duplicate_count = _count_duplicates(rows)

    return DataQualityReport(
        total_rows=total_rows,
        null_count=null_count,
        duplicate_count=duplicate_count,
        out_of_range_count=0,
    )


def _has_null_value(row: Mapping[str, Any]) -> bool:
    """A row counts as null if any of its fields is None or an empty string.

    Both show up as "missing" depending on the source format: JSON
    tends to use null, CSV tends to leave the field as an empty
    string. Checking only one of the two would undercount nulls
    depending on which file format a dataset happened to arrive in.
    """
    return any(value is None or value == "" for value in row.values())


def _count_duplicates(rows: Sequence[Mapping[str, Any]]) -> int:
    """Count rows that repeat an earlier row exactly.

    The first occurrence of a row is not a duplicate, only the ones
    that repeat it are. Sorting each row's items before turning it
    into a set key means two rows with the same values would still
    compare equal even if their keys came back in a different order,
    which can happen with some CSV or JSON parsers.
    """
    seen: set[tuple[Any, ...]] = set()
    duplicates = 0
    for row in rows:
        key = tuple(sorted(row.items()))
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return duplicates

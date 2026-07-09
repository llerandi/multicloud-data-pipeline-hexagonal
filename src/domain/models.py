# src/domain/models.py

"""Domain models for the data quality pipeline.

Everything in this module is plain Python: no pandas, no cloud SDK, no
database driver. That is intentional. The domain layer describes the
business concepts and rules on their own terms, so it can be tested and
understood without running infrastructure code.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class QualityThresholds:
    """Limits a dataset must respect to be accepted.

    This is a value object: it has no identity, only a value. Two
    instances with the same ratio are interchangeable. It is frozen
    (immutable) because thresholds should not change once decided for
    a given validation run.

    max_null_ratio is a fraction, not a percentage: 0.05 means 5%.
    """

    max_null_ratio: float = 0.05


@dataclass(frozen=True)
class DataQualityReport:
    """Result of running quality checks against a dataset.

    Also a value object. It only holds the counts a validation step
    produced (how many rows, how many nulls, and so on) and exposes
    the business rule that decides whether those counts are good
    enough. It does not know how the dataset was read or where it
    will be stored, that is the job of the application and
    infrastructure layers.
    """

    total_rows: int
    null_count: int
    duplicate_count: int
    out_of_range_count: int

    @property
    def null_ratio(self) -> float:
        """Fraction of rows that contain at least one null value.

        Guards against division by zero: an empty dataset has a null
        ratio of 0.0 rather than raising an error, since "no rows"
        and "bad rows" are different problems.
        """
        if self.total_rows == 0:
            return 0.0
        return self.null_count / self.total_rows

    def is_acceptable(self, thresholds: QualityThresholds) -> bool:
        """Apply the rule: reject a dataset with too many null values.

        Right now this only checks nulls, which is the rule the
        project scope defines first. duplicate_count and
        out_of_range_count are already tracked on the report so
        further rules can use them later without changing this class
        shape again.
        """
        return self.null_ratio <= thresholds.max_null_ratio

# PR 3: Application ports

Branch: `feature/application-ports`

Files added: `src/application/ports/file_storage.py`,
`src/application/ports/dataset_repository.py`,
`src/application/ports/metrics_publisher.py`,
`src/application/ports/notification_port.py`,
`src/application/ports/__init__.py` (updated),
`tests/application/ports/test_ports.py`.

## The problem a port solves

The `application` layer needs to read a raw file, store a validated
dataset, publish metrics, and send a failure notification. It cannot import
`boto3` or `google-cloud-storage` directly to do that, because then the use
case would be tied to a specific cloud provider, exactly the coupling this
whole project exists to avoid. A port is the way out: it is a contract that
says "I need something that can do X", without saying which concrete thing
provides it. The concrete thing (an adapter) is written later, against the
same contract, in the `infrastructure` layer.

## The Python mechanism: `ABC` and `abstractmethod`

```python
from abc import ABC, abstractmethod

class FileStorage(ABC):
    @abstractmethod
    def read(self, path: str) -> bytes:
        raise NotImplementedError
```

`ABC` (Abstract Base Class) marks `FileStorage` as a class that is not meant
to be used directly, only inherited from. `@abstractmethod` marks `read` as
a method every subclass is required to implement. This is enforced by
Python at runtime, not just a naming convention. Trying to instantiate the
class directly fails:

```
>>> FileStorage()
TypeError: Can't instantiate abstract class FileStorage with abstract method read
```

And it is not only about the base class. A subclass that forgets to
implement the method fails exactly the same way:

```python
class Incomplete(FileStorage):
    pass

Incomplete()
# TypeError: Can't instantiate abstract class Incomplete with abstract method read
```

Only a subclass that actually implements `read` can be instantiated:

```python
class LocalFileStorage(FileStorage):
    def read(self, path):
        with open(path, "rb") as f:
            return f.read()

LocalFileStorage()  # works
```

This matters later, not just now. When the GCS or S3 adapters get written
against these ports, if one of them forgets to implement a required method,
the failure happens immediately, at the moment the adapter is constructed,
with a clear error naming the missing method. It does not wait until
something calls the missing method in production.

## Why `raise NotImplementedError` inside a method Python already blocks

`abc` already prevents the abstract method's body from ever running, since
the class cannot be instantiated in the first place. The `raise` is a
convention, not a requirement: it documents, to a human reading the code,
that this body is a placeholder and not a real implementation. It also acts
as a safety net if the `@abstractmethod` decorator were ever accidentally
removed during a refactor, the method would still fail loudly instead of
silently returning `None`.

## Why the type hints are `Sequence[Mapping[str, Any]]`, not `list[dict]`

```python
def save(self, dataset_name: str, rows: Sequence[Mapping[str, Any]]) -> None:
```

This is the same underlying idea as the port itself, applied to data types
instead of behavior: depend on the least specific type that still does the
job. `Sequence` means "something ordered and indexable", it could be a
`list`, a `tuple`, or any other sequence, not necessarily a `list`
specifically. `Mapping` means "something with keys and values", it could be
a `dict`, or any dict-like object, not necessarily a `dict` specifically.
Typing the parameter as `list[dict]` would work today, but it would also
force every caller to build an actual `list` of actual `dict` objects even
in cases where a more general type would have done, which is an unnecessary
constraint the port does not actually need to impose.

## Why `MetricsPublisher` imports `DataQualityReport` and the other three ports do not

```python
def publish(self, dataset_name: str, report: DataQualityReport) -> None:
```

`FileStorage` moves raw bytes, `DatasetRepository` moves generic rows,
`NotificationPort` moves a plain string reason. None of those three need to
know what a `DataQualityReport` is. `MetricsPublisher` exists specifically
to publish quality metrics, so it makes sense for it to receive the actual
domain object, with its fields already defined (`null_ratio`,
`total_rows`, and so on), rather than an untyped dictionary where a typo in
a key name would only surface at runtime, in whichever adapter tries to read
that key.

## Why `ports/__init__.py` re-exports the four classes

```python
from src.application.ports.dataset_repository import DatasetRepository
from src.application.ports.file_storage import FileStorage
from src.application.ports.metrics_publisher import MetricsPublisher
from src.application.ports.notification_port import NotificationPort

__all__ = ["DatasetRepository", "FileStorage", "MetricsPublisher", "NotificationPort"]
```

Without this, importing a port would require knowing which exact file it
lives in: `from src.application.ports.file_storage import FileStorage`. With
this re-export, any caller can do
`from src.application.ports import FileStorage`, treating `ports` as a
single namespace instead of needing to know the internal file layout. This
is a general Python packaging convention, not something specific to
hexagonal architecture.

## What the tests check, and why exactly that

Each port gets exactly two tests. One confirms the port cannot be
instantiated directly, guarding against someone later removing the
`@abstractmethod` decorator by accident, in which case the class would
silently stop enforcing the contract and this test would catch it. The
other builds the smallest possible concrete subclass that implements the
required method, and checks it behaves as expected, this documents, in
executable form, what "implementing this port" actually looks like, which
is useful as a reference when the real adapters (GCS, S3, BigQuery,
Postgres, Slack, scikit-learn, Vertex AI) get written against these same
four contracts.

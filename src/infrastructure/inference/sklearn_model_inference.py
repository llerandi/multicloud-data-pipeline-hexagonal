"""SklearnModelInference: a ModelInferencePort adapter backed by a
pre-trained local scikit-learn estimator.

Meant for local development and for datasets small enough to score on
the same machine that runs the pipeline. The Vertex AI adapter, once
written, implements the exact same port against a deployed model
instead, that comparison, same interface, two different places
inference actually runs, is what this half of the project exists to
demonstrate.
"""

from typing import Any, Mapping, Sequence

from src.application.ports import ModelInferencePort


class SklearnModelInference(ModelInferencePort):
    """Runs predict() on an already-fitted scikit-learn estimator.

    model is expected to already be trained, fit elsewhere, loaded from
    disk, whatever it takes to get a fitted estimator. This adapter only
    calls predict on it, it does not train or load models itself,
    training is a separate concern from serving predictions inside a
    pipeline.

    feature_names is the ordered list of keys read from each row to
    build the input matrix the model expects. Order matters:
    scikit-learn models take a 2D array of plain values with no column
    names attached, so the order used here must match the order the
    model was trained with, this adapter has no way to verify that on
    its own, the caller is responsible for getting it right.
    """

    def __init__(self, model: Any, feature_names: Sequence[str]) -> None:
        self._model = model
        self._feature_names = feature_names

    def predict(
        self, dataset_name: str, rows: Sequence[Mapping[str, Any]]
    ) -> Sequence[Any]:
        matrix = [[row[name] for name in self._feature_names] for row in rows]
        predictions = self._model.predict(matrix)

        # scikit-learn returns a numpy array. Converting it here, rather
        # than leaving it to whoever calls predict(), keeps this port's
        # promise: every adapter returns a plain Sequence, not a
        # numpy-specific type only some callers would know how to
        # handle. tolist() is used when available since it returns
        # native Python numbers, plain list() on a numpy array would
        # instead give a list of numpy scalar types.
        if hasattr(predictions, "tolist"):
            return predictions.tolist()
        return list(predictions)

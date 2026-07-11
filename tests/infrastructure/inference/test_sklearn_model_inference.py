"""Unit tests for SklearnModelInference that do not need scikit-learn
installed.

FakeModel below is not scikit-learn, it is a minimal stand-in for
anything with a .predict(matrix) method, which is the only thing this
adapter actually calls on the object it wraps. That is enough to prove
the row-to-matrix conversion and the return type conversion are each
correct on their own, dependency-free and fast. The one test that needs
the real package is test_sklearn_model_inference_integration.py, kept
separate and skipped automatically where scikit-learn is not installed.
"""

from src.application.ports import ModelInferencePort
from src.infrastructure.inference import SklearnModelInference


class FakeModel:
    """Stands in for a fitted scikit-learn estimator's predict method."""

    def __init__(self, predictions):
        self._predictions = predictions
        self.received_matrix = None

    def predict(self, matrix):
        self.received_matrix = matrix
        return self._predictions


def test_sklearn_model_inference_is_a_model_inference_port():
    assert issubclass(SklearnModelInference, ModelInferencePort)


def test_predict_builds_the_matrix_in_feature_name_order():
    model = FakeModel(predictions=[0, 1])
    inference = SklearnModelInference(model=model, feature_names=["age", "income"])

    inference.predict(
        "customers",
        [{"income": 50000, "age": 30}, {"income": 20000, "age": 22}],
    )

    # feature_names is ["age", "income"], so each row must turn into
    # [age, income], regardless of what order the keys were in the
    # original row dict.
    assert model.received_matrix == [[30, 50000], [22, 20000]]


def test_predict_returns_a_plain_list_when_the_model_already_returns_one():
    model = FakeModel(predictions=[0, 1])
    inference = SklearnModelInference(model=model, feature_names=["age"])

    predictions = inference.predict("customers", [{"age": 30}, {"age": 22}])

    assert predictions == [0, 1]
    assert type(predictions) is list


def test_predict_converts_a_numpy_like_result_via_tolist():
    class NumpyLikeArray(list):
        """Mimics the one thing this adapter relies on: a .tolist() method."""

        def tolist(self):
            return list(self)

    model = FakeModel(predictions=NumpyLikeArray([1, 0]))
    inference = SklearnModelInference(model=model, feature_names=["age"])

    predictions = inference.predict("customers", [{"age": 30}, {"age": 22}])

    assert predictions == [1, 0]
    # NumpyLikeArray.tolist() returns a genuine list(), not another
    # NumpyLikeArray, this checks the adapter actually returned that,
    # rather than the untouched numpy-like object.
    assert type(predictions) is list

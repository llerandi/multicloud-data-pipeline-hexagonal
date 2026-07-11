"""Integration test for SklearnModelInference using a real, fitted
scikit-learn model.

Everything in test_sklearn_model_inference.py uses a fake standing in
for a model. This test is the one place in the project that fits and
runs an actual scikit-learn estimator, to prove the adapter works
against the real library, not just against something shaped like it.
pytest.importorskip skips this file with a clear reason instead of
failing if scikit-learn is not installed in the current environment.
"""

import pytest

pytest.importorskip("sklearn")

from sklearn.linear_model import LogisticRegression  # noqa: E402

from src.infrastructure.inference import SklearnModelInference  # noqa: E402


def test_predict_runs_a_real_fitted_model_end_to_end():
    model = LogisticRegression()
    # A trivial, perfectly separable training set: the label matches
    # the sign of a single feature. This is not meant to demonstrate
    # anything about machine learning, only that predict() runs end to
    # end through this adapter with a real scikit-learn estimator.
    model.fit(X=[[-10], [-5], [5], [10]], y=[0, 0, 1, 1])

    inference = SklearnModelInference(model=model, feature_names=["score"])

    predictions = inference.predict("customers", [{"score": -8}, {"score": 8}])

    assert predictions == [0, 1]
    assert isinstance(predictions, list)

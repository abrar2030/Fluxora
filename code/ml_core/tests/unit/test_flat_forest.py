import pandas as pd
from tests.factories import hourly_frame


class TestFlatForest:
    def test_matches_sklearn_predictions(self):
        import numpy as np
        from ml_core import FlatForest
        from ml_core.training.trainer import train_model

        bundle, _ = train_model(hourly_frame())
        rng = np.random.default_rng(0)
        samples = rng.normal(50, 20, size=(25, len(bundle.feature_columns)))
        flat = FlatForest(bundle.model)
        expected = bundle.model.predict(
            pd.DataFrame(samples.astype("float32"), columns=bundle.feature_columns)
        )
        actual = np.array([flat.predict_one(row) for row in samples])
        assert np.allclose(expected, actual)

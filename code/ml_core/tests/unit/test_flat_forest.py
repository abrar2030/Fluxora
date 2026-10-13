import pandas as pd
from tests.factories import hourly_frame


class TestFlatForest:
    def test_matches_sklearn_predictions(self):
        import numpy as np
        from src import FlatForest
        from src.training.trainer import train_model

        bundle, _ = train_model(hourly_frame())
        rng = np.random.default_rng(0)
        samples = rng.normal(50, 20, size=(25, len(bundle.feature_columns)))
        flat = FlatForest(bundle.model)
        expected = bundle.model.predict(
            pd.DataFrame(samples.astype("float32"), columns=bundle.feature_columns)
        )
        actual = np.array([flat.predict_one(row) for row in samples])
        assert np.allclose(expected, actual)


class TestFloat32Behaviour:
    def test_values_next_to_thresholds_follow_sklearn(self):
        import numpy as np
        from sklearn.ensemble import RandomForestRegressor
        from src import FlatForest

        rng = np.random.default_rng(3)
        X = rng.normal(0, 1, size=(400, 4))
        y = X[:, 0] * 2 + np.sin(X[:, 1]) + rng.normal(0, 0.1, 400)
        forest = RandomForestRegressor(n_estimators=8, random_state=0).fit(X, y)
        flat = FlatForest(forest)

        samples = []
        for estimator in forest.estimators_[:4]:
            tree = estimator.tree_
            for node in np.flatnonzero(tree.children_left != -1)[:10]:
                for nudge in (-1e-9, 0.0, 1e-9):
                    row = rng.normal(0, 1, 4)
                    row[tree.feature[node]] = tree.threshold[node] * (1 + nudge)
                    samples.append(row)
        samples = np.array(samples)

        expected = forest.predict(samples)  # sklearn casts to float32 internally
        actual = np.array([flat.predict_one(row) for row in samples])
        assert np.allclose(expected, actual)

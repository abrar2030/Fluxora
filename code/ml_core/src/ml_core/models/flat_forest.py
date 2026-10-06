import numpy as np
from sklearn.ensemble import RandomForestRegressor


class FlatForest:
    def __init__(self, forest: RandomForestRegressor) -> None:
        trees = [estimator.tree_ for estimator in forest.estimators_]
        tree_count = len(trees)
        width = max(tree.node_count for tree in trees)

        self.left = np.zeros((tree_count, width), dtype=np.int64)
        self.right = np.zeros((tree_count, width), dtype=np.int64)
        self.feature = np.zeros((tree_count, width), dtype=np.int64)
        self.threshold = np.full((tree_count, width), np.inf, dtype=np.float64)
        self.value = np.zeros((tree_count, width), dtype=np.float64)
        self.depth = max(tree.max_depth for tree in trees)
        self._rows = np.arange(tree_count)

        for i, tree in enumerate(trees):
            count = tree.node_count
            positions = np.arange(count)
            is_leaf = tree.children_left == -1
            self.left[i, :count] = np.where(is_leaf, positions, tree.children_left)
            self.right[i, :count] = np.where(is_leaf, positions, tree.children_right)
            self.feature[i, :count] = np.where(is_leaf, 0, tree.feature)
            self.threshold[i, :count] = np.where(is_leaf, np.inf, tree.threshold)
            self.value[i, :count] = tree.value[:, 0, 0]

    def predict_one(self, x: np.ndarray) -> float:
        sample = np.asarray(x, dtype=np.float32).astype(np.float64)
        nodes = np.zeros(len(self._rows), dtype=np.int64)
        rows = self._rows
        for _ in range(self.depth):
            go_left = sample[self.feature[rows, nodes]] <= self.threshold[rows, nodes]
            nodes = np.where(go_left, self.left[rows, nodes], self.right[rows, nodes])
        return float(self.value[rows, nodes].mean())

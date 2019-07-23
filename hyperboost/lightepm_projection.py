import typing

import numpy as np
from lightgbm import LGBMRegressor
from scipy.spatial import cKDTree
from sklearn.random_projection import SparseRandomProjection

from smac.epm.base_epm import AbstractEPM


class LightEPMProjection(AbstractEPM):
    def __init__(self, types: np.ndarray, bounds: typing.List[typing.Tuple[float, float]],
                 instance_features: np.ndarray = None, pca_components: float = None, seed=None, scaling="var"):
        super().__init__(types=types, bounds=bounds, instance_features=instance_features, pca_components=pca_components)
        self.light = LGBMRegressor(verbose=-1, min_child_samples=1, objective="quantile", num_leaves=8,
                                   alpha=0.10, min_data_in_bin=1, n_jobs=4, n_estimators=100, random_state=seed)

        self.scaling = scaling

        # A KDTree to be constructed for measuring distance
        self.kdtree = None

        # Types and bounds
        self.bounds = bounds
        self.types = types

        # Observed values
        self.X = None
        self.y = None
        self.X_transformed = None

        # The incumbent value
        self.inc = None

        # Selection of hyperparameters that require one-hot-encoding
        self.selection = types != 0

        # Flag that checks if there are any nominal parameters
        self.contains_nominal = any(self.selection)

        # The number of possible categories per nominal parameter
        self.categories = types[self.selection]

        # The maximum L1 distance between two points in hyperparameter space
        self.max_distance = sum(np.maximum(i, 1) for i in types)

        self.projector = SparseRandomProjection(2)

    def _train(self, X, y):
        X_ = X
        y_ = y

        self.X = X_
        self.y = y_
        self.X_transformed = self.transform(X)
        self.kdtree = cKDTree(self.projector.fit_transform(self.X_transformed))
        self.inc = np.max(y_)
        n_samples = X_.shape[0]
        if n_samples >= 2:
            self.light.fit(X_, y_.flatten())

    def _predict(self, X):

        # Zeros returned in case model was not fitted
        loss = np.zeros(X.shape[0])

        # Variance only returned for compatibility
        closeness = np.zeros(X.shape[0])

        # Model not fitted
        if self.light._n_features is None:
            return loss, closeness
        else:
            loss = self.light.predict(X)
            X_transformed = self.transform(X)
            dist, ind = self.kdtree.query(self.projector.transform(X_transformed), k=1, p=1)

            scale = np.std(self.y)
            # print("var_y:", np.var(self.y), "var_x:", np.var(self.X))
            unscaled_dist = dist.reshape(-1) / self.max_distance
            # loss[unscaled_dist == 0] = 1
            dist = unscaled_dist * scale
            closeness = 1 - dist

        return loss, closeness

    def transform(self, X):
        if not self.contains_nominal:
            return X

        result = []
        for i in X:
            # Split
            nominal = i[self.selection].astype(int)
            numerical = i[~self.selection]

            # Concatenate one-hot encoded together with numerical
            r = np.concatenate(
                [self.one_hot_vector(self.categories[index], indicator) for index, indicator in enumerate(nominal)])
            r = np.concatenate([numerical, r])

            result.append(r)

        return np.array(result)

    @staticmethod
    def one_hot_vector(length, indicator):
        result = np.zeros(length)
        result[indicator] = 1
        return result
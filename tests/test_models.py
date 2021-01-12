import unittest

import torch
import numpy as np
from torch.utils.data import TensorDataset

from deep_logic.models.relunn import XReluClassifier
from deep_logic.models.linear import LogisticRegressionClassifier
from deep_logic.models.tree import XDecisionTreeClassifier
from deep_logic.utils.base import set_seed, validate_network, validate_data
from deep_logic.utils.metrics import Accuracy, TopkAccuracy


class TestTemplateObject(unittest.TestCase):
    def test_relunn(self):

        set_seed(0)

        # Test with 1 target
        x = torch.tensor([[0, 1], [1, 1], [1, 0], [0, 0]], dtype=torch.float).cpu()
        y = torch.tensor([0, 1, 1, 0], dtype=torch.float).unsqueeze(1).cpu()
        train_data = TensorDataset(x, y)
        x_sample = torch.tensor([0, 1], dtype=torch.float)

        loss = torch.nn.BCELoss()
        metric = Accuracy()
        model = XReluClassifier(n_classes=1, n_features=2, hidden_neurons=[20, 10, 5], loss=loss, l1_weight=0.001)

        results = model.fit(train_data, train_data, batch_size=4, epochs=100, l_r=0.01, metric=metric)
        reduced_model = model.get_reduced_model(x_sample)
        explanation = model.get_explanation(x_sample, k=2)

        assert results.shape == (100, 4)
        assert isinstance(reduced_model, torch.nn.Sequential)
        assert explanation == '~f0 & f1'

        # Test with multiple targets
        x = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=torch.float).cpu()
        y = torch.tensor([[0, 1], [1, 0], [1, 0], [0, 1]], dtype=torch.float).cpu()
        train_data = TensorDataset(x, y)
        x_sample = torch.tensor([0, 1], dtype=torch.float)

        loss = torch.nn.BCELoss()
        metric = TopkAccuracy()
        model = XReluClassifier(n_classes=2, n_features=2, hidden_neurons=[20, 10, 3], loss=loss, l1_weight=0)

        results = model.fit(train_data, train_data, batch_size=4, epochs=100, l_r=0.1, metric=metric)
        reduced_model = model.get_reduced_model(x_sample)
        explanation = model.get_explanation(x_sample, k=2)

        assert results.shape == (100, 4)
        assert isinstance(reduced_model, torch.nn.Sequential)
        assert explanation == '~f0 & f1'

        return

    def test_linear(self):

        set_seed(0)

        x = torch.tensor([[0, 1], [1, 1], [1, 0], [0, 0]], dtype=torch.float).cpu()
        y = torch.tensor([0, 1, 0, 0], dtype=torch.float).unsqueeze(1).cpu()
        train_data = TensorDataset(x, y)

        loss = torch.nn.BCELoss()
        metric = Accuracy()
        model = LogisticRegressionClassifier(n_classes=1, n_features=2, loss=loss)

        results = model.fit(train_data, train_data, batch_size=4, epochs=100, l_r=0.01, metric=metric)

        assert results.shape == (100, 4)

        x = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=torch.float).cpu()
        y = torch.tensor([[0, 1], [1, 0], [1, 0], [0, 1]], dtype=torch.float).cpu()
        train_data = TensorDataset(x, y)

        loss = torch.nn.BCELoss()
        metric = TopkAccuracy()
        model = LogisticRegressionClassifier(n_classes=2, n_features=2, loss=loss)

        results = model.fit(train_data, train_data, batch_size=4, epochs=100, l_r=0.01, metric=metric)

        assert results.shape == (100, 4)

        return

    def test_tree(self):

        set_seed(0)

        x = torch.tensor([[0, 1], [1, 1], [1, 0], [0, 0]], dtype=torch.float).cpu()
        y = torch.tensor([0, 1, 1, 0], dtype=torch.float).unsqueeze(1).cpu()
        train_data = TensorDataset(x, y)

        metric = Accuracy()
        model = XDecisionTreeClassifier(n_classes=1, n_features=2)

        results = model.fit(train_data, train_data, metric=metric)

        assert results.shape == (1, 4)

        x = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=torch.float).cpu()
        y = torch.tensor([[0, 1], [1, 0], [1, 0], [0, 1]], dtype=torch.float).cpu()
        train_data = TensorDataset(x, y)

        metric = TopkAccuracy()
        model = XDecisionTreeClassifier(n_classes=2, n_features=2)

        results = model.fit(train_data, train_data, metric=metric)

        assert results.shape == (1, 4)

        return


if __name__ == '__main__':
    unittest.main()
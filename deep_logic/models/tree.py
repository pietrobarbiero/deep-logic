from typing import Tuple

import numpy as np
import pandas as pd
import torch
from sklearn.tree import DecisionTreeClassifier
from torch.utils.data import Dataset

from .base import BaseXClassifier, ClassifierNotTrainedError
from ..utils.metrics import Metric, TopkAccuracy


class XDecisionTreeClassifier(BaseXClassifier):
    """
        Decision Tree class module. It does provides for explanations.

        :param n_classes: int
            number of classes to classify - dimension of the output layer of the network
        :param n_features: int
            number of features - dimension of the input space
        :param max_depth: int
            maximum depth for the classifier. The deeper is the tree, the more complex are the explanations provided.
     """

    def __init__(self, n_classes: int, n_features: int, max_depth: int = None, device: torch.device = torch.device('cpu'),
                 name: str = "net"):

        super().__init__(name, device)
        assert device == torch.device('cpu'), "Only cpu training is provided with decision tree models."

        self.n_classes = n_classes
        self.n_features = n_features

        self.model = DecisionTreeClassifier(max_depth=max_depth)

    def forward(self, x) -> torch.Tensor:
        """
        forward method extended from Classifier. Here input data goes through the layer of the ReLU network.
        A probability value is returned in output after sigmoid activation

        :param x: input tensor
        :return: output classification
        """
        super(XDecisionTreeClassifier, self).forward(x)
        x = x.detach().cpu().numpy()
        output = self.model.predict_proba(x)
        return output

    def get_loss(self, output: torch.Tensor, target: torch.Tensor) -> None:
        """
        Loss is not used in the decision tree as it is not a gradient based algorithm. Therefore, if this function
        is called an error is thrown.
        :param output: output tensor from the forward function
        :param target: label tensor
        :raise: NotAvailableError
        """
        raise NotAvailableError()

    def get_device(self) -> torch.device:
        """
        Return the device on which the classifier is actually loaded. For DecisionTree is always cpu

        :return: device in use
        """
        return torch.device("cpu")

    def fit(self, train_set: Dataset, val_set: Dataset, metric: Metric = TopkAccuracy(),
            verbose: bool = True, **kwargs) -> pd.DataFrame:
        """
        fit function that execute many of the common operation generally performed by many method during training.
        Adam optimizer is always employed

        :param train_set: training set on which to train
        :param val_set: validation set used for early stopping
        :param metric: metric to evaluate the predictions of the network
        :param verbose: whether to output or not epoch metrics
        :return: pandas dataframe collecting the metrics from each epoch
        """

        # Laoding dataset
        train_loader = torch.utils.data.DataLoader(train_set, 64)#, shuffle=True, pin_memory=True, num_workers=8)
        train_data, train_labels = [], []
        for data in train_loader:
            train_data.append(data[0]), train_labels.append(data[1])
        train_data, train_labels = torch.cat(train_data).numpy(), torch.cat(train_labels).numpy()

        # Fitting decision tree
        if train_labels.shape[1] > 1:
            train_labels = np.argmax(train_labels, axis=1)
        self.model = self.model.fit(X=train_data, y=train_labels)

        # Compute accuracy, f1 and constraint_loss on the whole train, validation dataset
        train_acc = self.evaluate(train_set, metric)
        val_acc = self.evaluate(val_set, metric)

        if verbose:
            print({"Train_acc": f"{train_acc:.1f}", "Val_acc": f"{val_acc:.1f}"})

        self.save()

        # Performance dictionary
        performance_dict = {
            "tot_loss": [0],
            "train_accs": [train_acc],
            "val_accs": [val_acc],
            "best_epoch": [0],
        }
        performance_df = pd.DataFrame(performance_dict)
        return performance_df

    def evaluate(self, dataset: Dataset, metric: Metric = TopkAccuracy(), **kwargs) -> float:
        """
        Evaluate function to test without training the performance of the decision tree on a certain dataset

        :param dataset: dataset on which to test
        :param metric: metric to evaluate the predictions of the network
        :return: metric evaluated on the dataset
        """
        outputs, labels = self.predict(dataset)
        outputs, labels = torch.FloatTensor(outputs), torch.FloatTensor(labels)
        metric_val = metric(outputs, labels)
        return metric_val

    def predict(self, dataset, **kwargs) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Predict function to compute the prediction of the decision tree on a certain dataset

        :param dataset: dataset on which to test
        :return: a tuple containing the outputs computed on the dataset and the labels
        """
        outputs, labels = [], []
        loader = torch.utils.data.DataLoader(dataset, 2)#, num_workers=8, pin_memory=True)
        for data in loader:
            batch_data = data[0]
            batch_output = self.forward(batch_data)
            if data[1].shape[1] == 1:
                batch_output = batch_output[:, 1].squeeze()
            outputs.append(batch_output)
            labels.append(data[1].squeeze().cpu().detach().numpy())

        if data[1].shape[1] == 1:
            return np.hstack(outputs), np.hstack(labels)
        else:
            return np.vstack(outputs), np.vstack(labels)

    def save(self, name=None, **kwargs) -> None:
        from joblib import dump

        """
        Save model on a file named with the name of the model if parameter name is not set.

        :param name: Save the model with a name different from the one assigned in the __init__
        """
        if name is None:
            name = self.name
        dump(self.model, name)

    def load(self, name=None, **kwargs) -> None:
        from joblib import load
        """
        Load decision tree model.

        :param name: Load a model with a name different from the one assigned in the __init__
        """
        if name is None:
            name = self.name
        try:
            self.model = load(name)
        except FileNotFoundError:
            raise ClassifierNotTrainedError() from None


class NotAvailableError(Exception):
    """
    Error raised when we try to access methods that are not available for a given class.
    """

    def __init__(self):
        self.message = "Method not existing for the given class"

    def __str__(self):
        return self.message


if __name__ == "__main__":
    pass
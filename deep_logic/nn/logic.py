import torch
from torch import Tensor
from torch.nn import Linear

from .concepts import XConceptizator


class XLogic(Linear):
    """Applies a linear transformation to the incoming data: :math:`y = xA^T + b`
    """

    def __init__(self, in_features: int, bias: bool = True, activation: str = 'sigmoid', top: bool = False) -> None:
        super(XLogic, self).__init__(in_features, in_features, bias)
        self.in_features = in_features
        self.top = top
        self.activation = activation
        self.conceptizator = XConceptizator(activation)

    def forward(self, input: Tensor) -> Tensor:
        x = torch.nn.functional.linear(input, self.weight, self.bias)
        x = self.conceptizator(x)
        return x

    def extra_repr(self) -> str:
        return 'in_features={}, out_features={}, bias={}'.format(
            self.in_features, self.out_features, self.bias is not None
        )


class XRaxor(Linear):
    """Applies a linear transformation to the incoming data: :math:`y = xA^T + b`
    """

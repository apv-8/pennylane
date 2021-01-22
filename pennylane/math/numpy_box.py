# Copyright 2018-2020 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module contains the NumpyBox implementation of the TensorBox API.
"""
import numpy as np
import pennylane as qml


wrap_output = qml.math.wrap_output


class NumpyBox(qml.math.TensorBox):
    """Implements the :class:`~.TensorBox` API for ``numpy.ndarray``.

    For more details, please refer to the :class:`~.TensorBox` documentation.
    """

    abs = wrap_output(lambda self: np.abs(self.data))
    angle = wrap_output(lambda self: np.angle(self.data))
    arcsin = wrap_output(lambda self: np.arcsin(self.data))
    cast = wrap_output(lambda self, dtype: np.array(self.data, dtype=dtype))
    diag = staticmethod(wrap_output(lambda values, k=0: np.diag(values, k=k)))
    expand_dims = wrap_output(lambda self, axis: np.expand_dims(self.data, axis=axis))
    ones_like = wrap_output(lambda self: np.ones_like(self.data))
    reshape = wrap_output(lambda self, shape: np.reshape(self.data, shape))
    sqrt = wrap_output(lambda self: np.sqrt(self.data))
    sum = wrap_output(
        lambda self, axis=None, keepdims=False: np.sum(self.data, axis=axis, keepdims=keepdims)
    )
    T = wrap_output(lambda self: self.data.T)
    take = wrap_output(lambda self, indices, axis=None: np.take(self.data, indices, axis=axis))
    squeeze = wrap_output(lambda self: self.data.squeeze())

    def __init__(self, tensor):
        if not isinstance(tensor, np.ndarray):
            tensor = np.asarray(tensor)

        super().__init__(tensor)

    @staticmethod
    def astensor(tensor):
        return np.asarray(tensor)

    @staticmethod
    @wrap_output
    def concatenate(values, axis=0):
        return np.concatenate(NumpyBox.unbox_list(values), axis=axis)

    @staticmethod
    @wrap_output
    def dot(x, y):
        x, y = NumpyBox.unbox_list([x, y])
        x = np.asarray(x)
        y = np.asarray(y)

        if x.ndim == 0 and y.ndim == 0:
            return x * y

        if x.ndim == 2 and y.ndim == 2:
            return x @ y

        return np.dot(x, y)

    @property
    def interface(self):
        return "numpy"

    def numpy(self):
        return self.data

    @property
    def requires_grad(self):
        return False

    @wrap_output
    def scatter_element_add(self, index, value):
        self.data[tuple(index)] += value
        return self.data

    @property
    def shape(self):
        return self.data.shape

    @staticmethod
    @wrap_output
    def stack(values, axis=0):
        return np.stack(NumpyBox.unbox_list(values), axis=axis)

    @staticmethod
    @wrap_output
    def where(condition, x, y):
        return np.where(condition, *NumpyBox.unbox_list([x, y]))

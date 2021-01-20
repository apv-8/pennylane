# Copyright 2018-2021 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
TODO
"""
# pylint: disable=protected-access
import pennylane as qml
from pennylane.devices import DefaultMixed
from .jacobian_tape import JacobianTape
import numpy as np


class RewindTape(JacobianTape):
    r"""TODO
    """

    def jacobian(self, device, params=None, **options):
        """TODO

        Args:
            device:
            params:
            **options:

        Returns:
        """

        # The rewind tape only support differentiating expectation values of observables for now.
        for m in self.measurements:
            if (
                m.return_type is not qml.operation.Expectation
            ):
                raise ValueError(
                    f"The {m.return_type.value} return type is not supported with the rewind gradient method"
                )

        method = options.get("method", "analytic")

        if method == "device":
            # Using device mode; simply query the device for the Jacobian
            return self.device_pd(device, params=params, **options)
        elif method == "numeric":
            raise ValueError("RewindTape does not support numeric differentiation")

        if not device.capabilities().get("returns_state") or isinstance(device, DefaultMixed) \
            or not hasattr(device, "_apply_operation"):
            # TODO: consider renaming returns_state to, e.g., uses_statevector
            # TODO: consider adding a capability for mixed/pure state
            # TODO: consider adding capability for apply_operation
            raise qml.QuantumFunctionError("The rewind gradient method is only supported on statevector-based devices")

        # Perform the forward pass
        # TODO: Could we use lower-level like device.apply, since we just need the state?
        self.execute(device, params=params)
        phi = device._state  # TODO: Do we need dev._state or dev.state?

        lambdas = [device._apply_operation(phi, obs) for obs in self.observables]

        jac = np.zeros((len(lambdas), len(self.trainable_params)))

        for i, op in enumerate(reversed(self.operations)):
            adj = op.inv()
            phi = device._apply_operation(phi, adj)

            # TODO: Only use a matrix when necessary
            d_op_matrix = operator_derivative(op)
            mu = device._apply_unitary(phi, d_op_matrix, op.wires)

            jac_column = np.array([2 * np.real(dot_product(lambda_, mu)) for lambda_ in lambdas])
            jac[:, i] = jac_column

            lambdas = [device._apply_operation(lambda_, adj) for lambda_ in lambdas]

        return np.flip(jac, axis=1)


def dot_product(a, b):
    """TODO"""
    return np.sum(a.conj() * b)


def operator_derivative(operator):
    """TODO: do this better"""
    generator, prefactor = operator.generator
    param = operator.parameters[0]

    return (- prefactor * np.sin(param * prefactor) * np.eye(2)
                        - 1j * prefactor * np.cos(param * prefactor) * generator.matrix).T.conj()








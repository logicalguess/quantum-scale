import numpy as np
import math

from circuit_util import controlled_ry

from quantum_dictionary import QDictionary

class QQUBODictionary(QDictionary):
    # A Quantum Dictionary built from a function

    @staticmethod
    def prepare(d, circuit, key, value, ancilla, extra):
        for i in range(len(value)):
            for j in range(len(key)):
                controlled_ry(circuit, 1/2 ** len(value) * 2 * np.pi * 2 ** (i + 1) * d[j],
                              [key[j], value[i]], extra, ancilla[0])  # sum on powers of 2

        for i in range(len(value)):
            for k, v in d.items():
                if isinstance(k, tuple):
                    controlled_ry(circuit, 1/2 ** len(value) * 2 * np.pi * 2 ** (i+1) * v, [key[k[0]], key[k[1]]] + [value[i]], extra, ancilla)

    @staticmethod
    def unprepare(d, circuit, key, value, ancilla, extra):
        for i in range(len(value)):
            for j in range(len(key)):
                controlled_ry(circuit, -1/2 ** len(value) * 2 * np.pi * 2 ** (i + 1) * d[j],
                              [key[j], value[i]], extra, ancilla[0])  # sum on powers of 2

        for i in range(len(value)):
            for k, v in d.items():
                if isinstance(k, tuple):
                    controlled_ry(circuit, -1/2 ** len(value) * 2 * np.pi * 2 ** (i+1) * v, [key[k[0]], key[k[1]]] + [value[i]], extra, ancilla)

    def __init__(self, key_bits, value_bits, precision_bits, d):
        QDictionary.__init__(self, key_bits, value_bits, precision_bits, d, QQUBODictionary.prepare, QQUBODictionary.unprepare)

    def get_sum(self):
        self.get_value_for_key(2 ** self.key_bits - 1)

if __name__ == "__main__":

    def test_qubo_2():
        d = {}
        d[0] = 12
        d[1] = 1
        d[(0,1)] = 3

        n_key = 2
        n_value = 5

        qd = QQUBODictionary(n_key, n_value, 0, d)
        qd.get_value_for_key(3)

    def test_qubo_3():
        # f(x_0, x_1, x_2) = 12*x_0 + 1*x_1 - 15*x_2 + 3*x_0*x_1 - 9*x_1*x_2
        # f(0, 1, 1) = 1 - 15 - 9 = -23
        d = {0: 12, 1: 1, 2: -15, (0, 1): 3, (1, 2): -9}

        n_key = 3
        n_value = 6

        qd = QQUBODictionary(n_key, n_value, 0, d)
        v = qd.get_value_for_key(3)

        k = v[0:n_key]
        v = int(v[n_key:n_key + n_value], 2)
        if v >= 2**(n_value-1):
            v = v - 2**n_value
        print("QUBO value for " + k, " = ", v)

    def test_qubo_count():
        # f(x_0, x_1, x_2) = 12*x_0 + 1*x_1 - 15*x_2 + 3*x_0*x_1 - 9*x_1*x_2
        # f(0, 1, 1) = 1 - 15 - 9 = -23
        d = {0: 12, 1: 1, 2: -15, (0, 1): 3, (1, 2): -9}

        n_key = 3
        n_value = 6
        n_precision = 4

        qd = QQUBODictionary(n_key, n_value, n_precision, d)
        qd.get_zero_count()

    # test_qubo_2()
    test_qubo_3()
    # test_qubo_count()


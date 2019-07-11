import numpy as np
import math

from circuit_util import controlled_ry, cry

from quantum_dictionary import QDictionary

class QQUBODictionary(QDictionary):
    # A Quantum Dictionary built from a function

    @staticmethod
    def prepare(d, circuit, key, value, ancilla, extra):
        for i in range(len(value)):
            if d.get(-1, 0) > 0:
                cry(1/2 ** len(value) * 2 * np.pi * 2 ** (i + 1) * d[-1], circuit, value[i], ancilla[0])
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
        d = {0: 12, 1: 1, (0, 1): 3}

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
        # f(x_0, x_1, x_2) = 23 + 12*x_0 + 1*x_1 - 15*x_2 + 3*x_0*x_1 - 9*x_1*x_2
        # f(0, 1, 1) = 23 + 1 - 15 - 9 = 0
        d = {-1: 23, 0: 12, 1: 1, 2: -15, (0, 1): 3, (1, 2): -9}

        n_key = 3
        n_value = 6
        n_precision = 4

        qd = QQUBODictionary(n_key, n_value, n_precision, d)
        qd.get_zero_count()

    # test_qubo_2()
    test_qubo_3()
    # test_qubo_count()


# 0  =  000  ->  000000  =  0
# 6  =  110  ->  010000  =  16
# 7  =  111  ->  111000  =  56
# 4  =  100  ->  001100  =  12
# 2  =  010  ->  000001  =  1
# 1  =  001  ->  110001  =  49
# 3  =  011  ->  101001  =  41
# 5  =  101  ->  111101  =  61
# Outcomes [('3 -> 41', 0.94531), ('0 -> 0', 0.00781), ('6 -> 16', 0.00781), ('7 -> 56', 0.00781), ('4 -> 12', 0.00781), ('2 -> 1', 0.00781), ('1 -> 49', 0.00781), ('5 -> 61', 0.00781)]
# QUBO value for 011  =  -23


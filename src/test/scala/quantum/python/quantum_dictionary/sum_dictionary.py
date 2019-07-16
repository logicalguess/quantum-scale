import numpy as np
import math

from circuit_util import controlled_ry

from quantum_dictionary import QDictionary

class QSumDictionary(QDictionary):
    # A Quantum Dictionary built from a function

    @staticmethod
    def prepare(f, circuit, key, value, ancilla, extra):
        # controlled rotations only n powers of 2
        for i in range(len(value)):
            for j in range(len(key)):
                controlled_ry(circuit, 1/2 ** len(value) * 2 * np.pi * 2 ** (i + 1) * f[j],
                              [key[j], value[i]], extra, ancilla[0])  # sum on powers of 2

    def __init__(self, key_bits, value_bits, f):
        QDictionary.__init__(self, key_bits, value_bits, 0, f, QSumDictionary.prepare)

    def get_sum(self):
        self.get_value_for_key(2 ** self.key_bits - 1)

    def is_sum_negative(self):
        sum = self.get_value_for_key(2 ** self.key_bits - 1, True)
        return True if sum[self.key_bits] == '1' else False


if __name__ == "__main__":
    def test_sum():
        f = [12, 3, -1]

        n_key = len(f)
        n_value = math.ceil(np.log2(sum(f)))

        qd = QSumDictionary(n_key, n_value, f)
        qd.get_sum()

    def test_compare():
        f = [12, -38]

        n_key = len(f)
        n_value = math.ceil(np.log2(max(f))) + 2

        qd = QSumDictionary(n_key, n_value, f)
        print(qd.is_sum_negative())

    def test_binomial_distribution():
        f = [1 for _ in range(5)] # binomial
        # f = [2**i for i in range(5)] # uniform
        # f = [i*i for i in range(5)] # uniform
        # f = [i for i in range(5)] #?

        n_key = len(f)
        n_value = math.ceil(np.log2(sum(f)))

        qd = QSumDictionary(n_key, n_value, f)
        qd.get_value_distribution()

    # test_sum()
    test_compare()
    # test_binomial_distribution()
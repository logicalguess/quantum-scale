import numpy as np

from circuit_util import controlled_ry

from quantum_dictionary import QDictionary

class QPartitionDictionary(QDictionary):
    # A Quantum Dictionary built from a function

    @staticmethod
    def prepare(f, circuit, key, value, ancilla, extra):
        # controlled rotations only n powers of 2
        for i in range(len(value)):
            for j in range(len(key)):
                controlled_ry(circuit, 1/2 ** len(value) * 2 * np.pi * 2 ** (i + 1) * f[len(key) - 1 - j],
                              [key[j], value[i]], extra, ancilla[0])  # sum on powers of 2


    @staticmethod
    def unprepare(f, circuit, key, value, ancilla, extra):
        # controlled rotations only n powers of 2
        for i in range(len(value)):
            for j in range(len(key)):
                controlled_ry(circuit, -1/2 ** len(value) * 2 * np.pi * 2 ** (i + 1) * f[len(key) - 1 - j],
                              [key[j], value[i]], extra, ancilla[0])  # sum on powers of 2

    def __init__(self, key_bits, value_bits, precision_bits, f):
        QDictionary.__init__(self, key_bits, value_bits, precision_bits, f, QPartitionDictionary.prepare, QPartitionDictionary.unprepare)

    def get_zero_sum_count(self):
        return QDictionary.get_zero_count(self) - 1


if __name__ == "__main__":
    def test_zero_sum_subsets():
        f = [1, 1, -1] # 2
        # f = [2, 2, 2, -3] # 0

        n_key = len(f)
        n_value = 3
        n_precision = 5

        qd = QPartitionDictionary(n_key, n_value, n_precision, f)
        print("Number of zero sum subsets = ", qd.get_zero_sum_count())

    def test_partition():
        f = [1, 2, 3, 0] # 4

        n_key = len(f)
        n_value = 4
        n_precision = 5

        qd = QPartitionDictionary(n_key, n_value, n_precision, f)
        print("Number of half sum subsets = ", qd.get_count_for_value(3))

    # test_zero_sum_subsets()
    test_partition()
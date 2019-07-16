import numpy as np
import math

from circuit_util import controlled_ry, cry, qft, iqft

from quantum_dictionary import QDictionary

class QFiboDictionary(QDictionary):
    # A Quantum Dictionary built from a function

    @staticmethod
    def prepare(_, circuit, key, value, ancilla, extra):
        for i in range(len(value)):
            for j in range(len(key) - 1):
                controlled_ry(circuit, 1/2 ** len(value) * 2 * np.pi * 2 ** (i + 1),
                              [key[j], key[j+1], value[i]], extra, ancilla[0])  # sum on powers of 2

        iqft(circuit, [value[i] for i in range(len(value))])

    @staticmethod
    def unprepare(_, circuit, key, value, ancilla, extra):
        qft(circuit, [value[i] for i in range(len(value))])

        for i in range(len(value)):
            for j in range(len(key) - 1):
                controlled_ry(circuit, -1/2 ** len(value) * 2 * np.pi * 2 ** (i + 1),
                              [key[j], key[j+1], value[i]], extra, ancilla[0])  # sum on powers of 2

    def __init__(self, key_bits, value_bits, precision_bits, d):
        QDictionary.__init__(self, key_bits, value_bits, precision_bits, d, QFiboDictionary.prepare, QFiboDictionary.unprepare)


if __name__ == "__main__":

    def fibo(n, precision_bits):
        n_key = n
        n_value = int(math.log2(n_key - 1)) + 1

        qd = QFiboDictionary(n_key, n_value, precision_bits, None)
        qd.get_value_for_key(None)
        fibo = qd.get_zero_count()
        print("F(", n, ") = ", fibo)
        return fibo


    # fibo(2, 3)
    # 0 = 00 -> 0 = 0
    # 1 = 01 -> 0 = 0
    # 2 = 10 -> 0 = 0
    # 3 = 11 -> 1 = 1
    # F( 2 ) =  3

    fibo(3, 5)
    # 0 = 000 -> 00 = 0
    # 1 = 001 -> 00 = 0
    # 2 = 010 -> 00 = 0
    # 3 = 011 -> 01 = 1
    # 4 = 100 -> 00 = 0
    # 5 = 101 -> 00 = 0
    # 6 = 110 -> 01 = 1
    # 7 = 111 -> 10 = 2
    # F( 3 ) =  5

    # fibo(5, 5)
    # F( 5 ) =  13


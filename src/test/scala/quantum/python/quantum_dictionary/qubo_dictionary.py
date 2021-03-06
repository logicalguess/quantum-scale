import numpy as np
import math

from circuit_util import controlled_X, controlled_ry, cry, qft, iqft, oracle_first_bit_one

from quantum_dictionary import QDictionary

class QQUBODictionary(QDictionary):
    # A Quantum Dictionary built from a function

    @staticmethod
    def shift_negatives_up(shift, circuit, extra, value):
        l = len(value)
        for power in range(math.ceil(math.log2(shift)) + 1):
            if shift & 1 << power != 0:
                for j in reversed(range(0, l - power)):
                    tgt = l - 1 - power - j
                    ctrl = list(set([0] + list(range(tgt + 1, l - power))))
                    # print(tgt, ctrl)
                    controlled_X(circuit, [value[i] for i in ctrl], extra, [value[tgt]])

    @staticmethod
    def prepare(d, circuit, key, value, ancilla, extra):
        for i in range(len(value)):
            if d.get(-1, 0) != 0:
                cry(1/2 ** len(value) * 2 * np.pi * 2 ** (i + 1) * d[-1], circuit, value[i], ancilla[0])
            for j in range(len(key)):
                if d.get(j, 0) != 0:
                    controlled_ry(circuit, 1/2 ** len(value) * 2 * np.pi * 2 ** (i + 1) * d[j],
                              [key[j], value[i]], extra, ancilla[0])  # sum on powers of 2

        for i in range(len(value)):
            for k, v in d.items():
                if isinstance(k, tuple):
                    controlled_ry(circuit, 1/2 ** len(value) * 2 * np.pi * 2 ** (i+1) * v, [key[k[0]], key[k[1]]] + [value[i]], extra, ancilla)

        # cry(1/2 ** len(value) * 2 * np.pi * 2 * -1, circuit, value[0], ancilla[0]) # flips 0 sign bit to 1
        # circuit.u1(1/2 ** len(value) * 2 * np.pi * 1, value[0])
        # controlled_X(circuit, [value[0]] + [ value[i] for i in range(len(value) - bit, len(value))], extra, value[len(value) - bit])

        iqft(circuit, [value[i] for i in range(len(value))])

        # QQUBODictionary.shift_negatives_up(10, circuit, extra, value)

    @staticmethod
    def unprepare(d, circuit, key, value, ancilla, extra):
        qft(circuit, [value[i] for i in range(len(value))])

        for i in range(len(value)):
            if d.get(-1, 0) != 0:
                cry(-1/2 ** len(value) * 2 * np.pi * 2 ** (i + 1) * d[-1], circuit, value[i], ancilla[0])
            for j in range(len(key)):
                if d.get(j, 0) != 0:
                    controlled_ry(circuit, -1/2 ** len(value) * 2 * np.pi * 2 ** (i + 1) * d[j],
                              [key[j], value[i]], extra, ancilla[0])  # sum on powers of 2

        for i in range(len(value)):
            for k, v in d.items():
                if isinstance(k, tuple):
                    controlled_ry(circuit, -1/2 ** len(value) * 2 * np.pi * 2 ** (i+1) * v, [key[k[0]], key[k[1]]] + [value[i]], extra, ancilla)

    def __init__(self, key_bits, value_bits, precision_bits, d):
        QDictionary.__init__(self, key_bits, value_bits, precision_bits, d, QQUBODictionary.prepare, QQUBODictionary.unprepare)

    def get_count_for_value_less_than(self, v):
        self.f[-1] = -v
        return self.get_value_count(oracle_first_bit_one)


if __name__ == "__main__":

    def test_qubo_2():
        d = {0: -2, 1: 1, (0, 1): 3}

        n_key = 2
        n_value = 3
        n_precision = 3

        qd = QQUBODictionary(n_key, n_value, n_precision, d)
        # qd.get_value_for_key(3)
        qd.get_value_for_key(None, True)
        # 0 = 00 -> 000 = 0
        # 1 = 01 -> 001 = 1
        # 2 = 10 -> 110 = -2
        # 3 = 11 -> 010 = 2
        qd.get_negative_value_count() # 1
        # qd.get_count_for_value(-2) # 1
        # qd.get_count_for_value(-1) # 0

    def test_qubo_2_1():
        d = {0: -2, 1: -1, (0, 1): 3}

        n_key = 2
        n_value = 3
        n_precision = 3

        qd = QQUBODictionary(n_key, n_value, n_precision, d)
        # qd.get_value_for_key(3)
        qd.get_value_for_key(None, True)
        # 0 = 00 -> 000 = 0
        # 1 = 01 -> 111 = -1
        # 2 = 10 -> 110 = -2
        # 3 = 11 -> 000 = 0

        # qd.get_count_for_value(-3) #0
        # qd.get_count_for_value(-5) #0
        # qd.get_count_for_value(-2) # 1
        # qd.get_count_for_value(-1) # 1

        # qd.get_count_for_value(0) # 2
        # sines =  [(2.0, 1.00032)]
        # Best Estimate =  2

        qd.get_count_for_value_less_than(-1) # 1

        # qd.get_negative_value_count() # 2
        # sines =  [(2.0, 1.00032)]
        # Best Estimate =  2

    def test_qubo_2_2():
        d = {0: -2, 1: -1, (0, 1): 3}

        n_key = 2
        n_value = 3
        n_precision = 3

        d[-1] = 2
        qd = QQUBODictionary(n_key, n_value, n_precision, d)
        qd.get_value_for_key(None, True)
        # 0 = 00 -> 010 = 2
        # 1 = 01 -> 001 = 1
        # 2 = 10 -> 000 = 0
        # 3 = 11 -> 010 = 2

        qd.get_negative_value_count()
        # sines =  [(0.0, 1.0)]
        # Best Estimate =  0

    def test_qubo_3():
        # f(x_0, x_1, x_2) = 12*x_0 + 1*x_1 - 15*x_2 + 3*x_0*x_1 - 9*x_1*x_2
        # f(0, 1, 1) = 1 - 15 - 9 = -23
        d = {0: 12, 1: 1, 2: -15, (0, 1): 3, (1, 2): -9}

        n_key = 3
        n_value = 6

        qd = QQUBODictionary(n_key, n_value, 6, d)
        v = qd.get_value_for_key(3, True)
        # 0 = 000 -> 000000 = 0
        # 1 = 001 -> 110001 = -15
        # 2 = 010 -> 000001 = 1
        # 3 = 011 -> 101001 = -23
        # 4 = 100 -> 001100 = 12
        # 5 = 101 -> 111101 = -3
        # 6 = 110 -> 010000 = 16
        # 7 = 111 -> 111000 = -8

        k = v[0:n_key]
        v = int(v[n_key:n_key + n_value], 2)
        if v >= 2**(n_value-1):
            v = v - 2**n_value
        print("QUBO value for " + k, " = ", v) # -23

        # qd.get_negative_value_count() # 4
        # sines =  [(4.0, 1.003512)]
        # Best Estimate =  4

    def test_fibonacci():
        def fibo(m):
            d = {}
            for i in range(m-1):
                d[(i, i+1)] = 1

            qd = QQUBODictionary(m, int(math.log2(m - 1)) + 1, 6, d)
            fibo = qd.get_count_for_value(0)
            print("F(", m, ") = ", fibo)
            return fibo

        for m in range(2, 6):
            fibo(m)

        # F( 2 ) =  3
        # F( 3 ) =  5
        # F( 4 ) =  8
        # F( 5 ) =  13


    # test_qubo_2()
    # test_qubo_2_1()
    # test_qubo_2_2()
    test_qubo_3()
    # test_fibonacci()



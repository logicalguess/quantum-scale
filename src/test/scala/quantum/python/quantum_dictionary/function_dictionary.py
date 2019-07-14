import numpy as np

from circuit_util import on_match_ry, controlled, cxzx, cry, czxzx, cx, controlled_X, oracle_first_bit_one
from quantum_dictionary import QDictionary

class QFunctionDictionary(QDictionary):
    # A Quantum Dictionary built from a function

    @staticmethod
    def prepare(f, circuit, key, value, ancilla, extra):
        for i in range(len(value)):
            for k in range(2**len(key)):
                on_match_ry(len(key), k, circuit, 1/2 ** len(value) * 2 * np.pi * 2 ** (i+1) * f[k], [key[j] for j in range(0, len(key))] + [value[i]], extra, ancilla)

    @staticmethod
    def unprepare(f, circuit, key, value, ancilla, extra):
        for i in range(len(value)):
            for k in range(2**len(key)):
                on_match_ry(len(key), k, circuit, -1/2 ** len(value) * 2 * np.pi * 2 ** (i+1) * f[k], [key[j] for j in range(0, len(key))] + [value[i]], extra, ancilla)

    def __init__(self, key_bits, value_bits, precision_bits, f):
        QDictionary.__init__(self, key_bits, value_bits, precision_bits, f, QFunctionDictionary.prepare, QFunctionDictionary.unprepare)

    @staticmethod
    def random(key_bits, value_bits):
        rs = np.random.random(2**value_bits)
        p = rs/rs.sum()
        freq = QFunctionDictionary.distribution_to_frequency(key_bits, p)[1]
        f = QFunctionDictionary.frequency_to_function(key_bits, freq)
        return QDictionary(key_bits, value_bits, 0, f, QFunctionDictionary.prepare)

    @staticmethod
    def distribution_to_frequency(key_bits, p):
        assert(np.isclose(sum(p), 1))
        assert(len(p == 2**key_bits))

        freqs = {}
        N = 2**key_bits
        for i, v in enumerate(p):
            freqs[i] = int(np.round(v*N))
        s = sum(freqs.values())
        if s < N:
            freqs[0] = freqs[0] + N - s
        elif s > N:
            km = max(freqs, key=freqs.get)
            freqs[km] = freqs[km] - s + N

        ps = dict(
            map(lambda item: (item[0], np.round(item[1], 4)), enumerate(p)))

        print("Value Probabilities", ps)
        print("Value Frequencies", freqs)

        return ps, freqs

    @staticmethod
    def frequency_to_function(key_bits, freqs):
        f = {}
        idx = 0
        counter = 0
        for k in range(2**key_bits):
            if counter == freqs[idx]:
                counter = 0
                idx = idx + 1
                while freqs[idx] == 0:
                    idx = idx + 1

            f[k] = idx
            counter = counter + 1

        print("Function", f)
        return f


if __name__ == "__main__":

    def test_value_for_key():
        n_key = 2
        n_value = 4

        f = [k*k for k in range(2**n_key)]

        qd = QFunctionDictionary(n_key, n_value, 0, f)
        qd.get_value_for_key(3)

    def test_zero_value_count():
        n_key = 2
        n_value = 2
        n_precision = 5

        f = [0, 0, 0, 0]

        qd = QFunctionDictionary(n_key, n_value, n_precision, f)
        qd.get_zero_count()

    def test_negative_value_count():
        n_key = 3
        n_value = 2
        n_precision = 5

        f = [0, -2, -1, 0, -1, 1, 0, 0]

        qd = QFunctionDictionary(n_key, n_value, n_precision, f)
        qd.get_value_for_key()
        # qd.get_zero_count()
        qd.get_negative_value_count()

    def oracle(qc, c, q, e, a):
        qc.x(q[0])
        controlled(qc, [c[i] for i in range(len(c))] + [q[i] for i in range(len(q))], e, a, c_gate = czxzx)
        # controlled(qc, [c[i] for i in range(len(c))] + [q[0]], e, a, c_gate = czxzx)
        qc.x(q[0])

    def test_value_count():
        n_key = 2
        n_value = 2 # values between -2**(n_value-1) and 2**(n_value-1) - 1
        n_precision = 4

        f = [1, 0, 1, -1]

        qd = QFunctionDictionary(n_key, n_value, n_precision, f)
        qd.get_value_for_key()
        qd.get_count_for_value(1)

    def test_distribution_value():
        n_key = 3
        n_value = 6

        # f = [k*k for k in range(2**n_key)]
        f = [2, 3, 5, 7, 7, 7, 2, 1]

        qd = QFunctionDictionary(n_key, n_value, 0, f)
        qd.get_value_distribution()

    def test_random_distribution():
        qd = QFunctionDictionary.random(5, 3)
        qd.get_value_distribution()

    # test_value_for_key()
    test_negative_value_count()
    # test_distribution_value()
    # test_random_distribution()
    # test_value_count()

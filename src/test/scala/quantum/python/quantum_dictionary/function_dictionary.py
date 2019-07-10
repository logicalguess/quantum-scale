import numpy as np

from circuit_util import on_match_ry

from quantum_dictionary import QDictionary

class QFunctionDictionary(QDictionary):
    # A Quantum Dictionary built from a function

    @staticmethod
    def prepare(f, circuit, key, value, ancilla, extra):
        for i in range(len(value)):
            for k in range(2**len(key)):
                on_match_ry(len(key), k, circuit, 1/2 ** len(value) * 2 * np.pi * 2 ** (i+1) * f[k], [key[j] for j in range(0, len(key))] + [value[i]], extra, ancilla)


    def __init__(self, key_bits, value_bits, f):
        QDictionary.__init__(self, key_bits, value_bits, 0, f, QFunctionDictionary.prepare)

    def __init__(self, key_bits, value_bits):
        rs = np.random.random(2**value_bits)
        p = rs/rs.sum()
        freq = QFunctionDictionary.distribution_to_frequency(key_bits, p)[1]
        f = QFunctionDictionary.frequency_to_function(key_bits, freq)
        QDictionary.__init__(self, key_bits, value_bits, 0, f, QFunctionDictionary.prepare)

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

        qd = QFunctionDictionary(n_key, n_value, f)
        qd.get_value_for_key(3)

    def test_distribution_value():
        n_key = 3
        n_value = 6

        # f = [k*k for k in range(2**n_key)]
        f = [2, 3, 5, 7, 7, 7, 2, 1]

        qd = QFunctionDictionary(n_key, n_value, f)
        qd.get_value_distribution()

    def test_random_distribution():
        qd = QFunctionDictionary(5, 3)
        qd.get_value_distribution()

    # test_value_for_key()
    # test_distribution_value()
    test_random_distribution()

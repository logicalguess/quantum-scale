from qiskit import QuantumRegister, QuantumCircuit

import numpy as np

from circuit_util import on_match_ry, qft, is_bit_not_set, controlled_X, controlled_Z, czxzx, controlled, iqft
from util import get_probs, plot_histogram


class QValueSearchDictionary():
    # A Quantum Dictionary

    def __init__(self, key_bits, value_bits, f):
        self.key_bits = key_bits
        self.value_bits = value_bits
        self.f = f

    def prepare(self, f, circuit, key, value, ancilla, extra):
        for i in range(len(value)):
            for k in range(2**len(key)):
                on_match_ry(len(key), k, circuit, 1/2 ** len(value) * 2 * np.pi * 2 ** (i+1) * f[k], [key[j] for j in range(0, len(key))] + [value[i]], extra, ancilla)

        iqft(circuit, [value[i] for i in range(len(value))])

    def unprepare(self, f, circuit, key, value, ancilla, extra):
        qft(circuit, [value[i] for i in range(len(value))])

        for i in range(len(value)):
            for k in range(2**len(key)):
                on_match_ry(len(key), k, circuit, -1/2 ** len(value) * 2 * np.pi * 2 ** (i+1) * f[k], [key[j] for j in range(0, len(key))] + [value[i]], extra, ancilla)

    def __build_circuit(self, n_qbits, c_qbits, f, search_key):
        key = QuantumRegister(n_qbits)
        value = QuantumRegister(c_qbits)
        ancilla = QuantumRegister(1)
        extra = QuantumRegister(max(n_qbits, c_qbits) + 1)
        circuit = QuantumCircuit(key, value, ancilla, extra)

        def prepare_once():
            circuit.h(key)
            circuit.h(value)

            circuit.rx(np.pi/2, ancilla[0])
            circuit.z(ancilla[0])
            circuit.x(ancilla[0])

        def unprepare_once():
            circuit.rx(-np.pi/2, ancilla[0])

        prepare_once()

        # if search_key is not None:
        #     iterations = 1 if n_qbits == 2 else 2**(math.floor(n_qbits/2))
        #     for i in range(iterations):
        #         grover(search_key, circuit, key, extra, ancilla)

        self.prepare(f, circuit, key, value, ancilla, extra)

        unprepare_once()

        if search_key is not None:
            for i in range(1):
                self.grover(search_key, circuit, [key[i] for i in range(len(key))] + [value[i] for i in range(len(value))],
                    [value[i] for i in range(len(value))], extra, ancilla)
        else:
            for i in range(1):
                self.grover_n(circuit, [key[i] for i in range(len(key))] + [value[i] for i in range(len(value))],
                            [value[0]], extra, ancilla)

        return circuit

    def grover(self, m, qc, all, q, e, a):
        # qc.x(a[0])
        # qc.h(a[0])

        n = len(q)
        for i in range(0, n):
            if is_bit_not_set(m, i):
                qc.x(q[n - i - 1])

        # oracle
        # controlled_X(qc, q, e, a)
        controlled(qc, q, e, a, c_gate = lambda qc, ctrl, tgt: czxzx(qc, ctrl, tgt))

        # diffusion
        for i in range(0, len(all)):
            qc.h(all[i])
            qc.x(all[i])

        # controlled Z
        controlled_Z(qc, [all[i] for i in range(0, len(all) - 1)], e, [all[len(all) - 1]])

        for i in range(0, len(q)):
            qc.x(all[i])
            qc.h(all[i])

        for i in range(0, n):
            if is_bit_not_set(m, i):
                qc.x(q[n - i - 1])

        # qc.h(a[0])
        # qc.x(a[0])

    def grover_n(self, qc, all, q, e, a):
        qc.x(a[0])
        qc.h(a[0])

        # oracle
        controlled_X(qc, q, e, a)
        # controlled(qc, q, e, a, c_gate = lambda qc, ctrl, tgt: czxzx(qc, ctrl, tgt))

        # diffusion
        for i in range(0, len(all)):
            qc.h(all[i])
            qc.x(all[i])

        # controlled Z
        controlled_Z(qc, [all[i] for i in range(0, len(all) - 1)], e, [all[len(all) - 1]])

        for i in range(0, len(all)):
            qc.x(all[i])
            qc.h(all[i])

        qc.h(a[0])
        qc.x(a[0])


    def __process(self, n_bits, c_bits, probs, neg=False):
        kvs = {}
        entries = {}
        outcomes = {}
        for b, c in probs.items():
            key = int(b[0:n_bits], 2)
            value = int(b[n_bits:n_bits + c_bits], 2)
            kvs[key] = value
            if neg is True and value >= 2**(c_bits-1):
                value = value - 2**c_bits
            entries[key] = '%d' % key + " = " + b[0:n_bits] + " -> " + b[n_bits:n_bits + c_bits] + " = " + '%d' % value
            outcomes['%d' %  key + " -> " + '%d' % value] = c

        # for v in sorted(entries.items(), key=lambda x: x[1]):
        #     print(v[1])
        return sorted(kvs.items(), key=lambda x: x[1]), outcomes

    def __process_values(self, n_bits, c_bits, probs):
        value_freq = {}
        for b, c in probs.items():
            value = int(b[n_bits:n_bits + c_bits], 2)
            value_freq[value] = value_freq.get(value, 0) + c

        factor=1.0/sum(value_freq.values())
        value_freq = {k: v*factor for k, v in value_freq.items()}

        return value_freq

    def get_value_distribution(self):
        circuit = self.__build_circuit(self.key_bits, self.value_bits, self.f, None, None)
        probs = get_probs((circuit, None, None), 'sim', False)

        ordered_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        print("Probabilities: ", ordered_probs)

        v_freq = self.__process_values(self.key_bits, self.value_bits, probs)

        from qiskit.tools import visualization
        visualization.plot_histogram(v_freq)

        ordered_freq = sorted(v_freq.items(), key=lambda x: x[1], reverse=True)

        print("Value Distribution", ordered_freq)

    def get_value_for_key(self, key, neg = False):
        circuit = self.__build_circuit(self.key_bits, self.value_bits, self.f, key)
        probs = get_probs((circuit, None, None), 'sim', False)

        from qiskit.tools import visualization
        visualization.plot_histogram(probs)

        ordered_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        print("Probabilities: ", ordered_probs)

        _, outcomes = self.__process(self.key_bits, self.value_bits, probs, neg)
        ordered_outcomes = sorted(outcomes.items(), key=lambda x: x[1], reverse=True)

        print("Outcomes", ordered_outcomes)
        return ordered_probs[0][0]


if __name__ == "__main__":

    n_key = 3
    n_value = 4

    f = [0, -1, -2, 3, 4, 5, 6, 7]

    qd = QValueSearchDictionary(n_key, n_value, f)

    def test_get_value(v):
        qd.get_value_for_key(2**n_value*v + v, True)
        # qd.get_value_distribution()

    def test_get_negative_value():
        qd.get_value_for_key(None, True)
        # qd.get_value_distribution()

    # test_get_value(-2) # ('2 -> -2', 0.04785), ('0 -> 0', 0.01562)
    # test_get_value(5) # ('5 -> 5', 0.04785), ('0 -> 0', 0.01562)
    test_get_negative_value() # ('2 -> -2', 0.14111), ('1 -> -1', 0.14111), ('0 -> 0', 0.10987), ('4 -> 4', 0.10987)
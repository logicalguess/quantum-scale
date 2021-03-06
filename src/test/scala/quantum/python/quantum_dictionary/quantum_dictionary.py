from qiskit import QuantumRegister, QuantumCircuit

import numpy as np
import math

from circuit_util import qft, iqft, grover, oracle0, diffusion, get_oracle, oracle_first_bit_one
from util import get_probs, plot_histogram


class QDictionary():
    # A Quantum Dictionary

    def __init__(self, key_bits, value_bits, precision_bits, f, prepare, unprepare = None):
        self.key_bits = key_bits
        self.value_bits = value_bits
        if precision_bits > 0:
            self.precision_bits = precision_bits
        self.f = f
        self.prepare = prepare
        self.unprepare = unprepare

    def __build_circuit(self, n_qbits, c_qbits, f, search_key = None):
        key = QuantumRegister(n_qbits)
        value = QuantumRegister(c_qbits)
        ancilla = QuantumRegister(1)
        extra = QuantumRegister(max(n_qbits, c_qbits))
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

        if search_key is not None:
            iterations = 1 if n_qbits == 2 else 2**(math.floor(n_qbits/2))
            for i in range(iterations):
                grover(search_key, circuit, key, extra, ancilla)

        self.prepare(f, circuit, key, value, ancilla, extra)

        unprepare_once()


        return circuit

    def __build_circuit_count(self, n_qbits, c_qbits, f, oracle):
        key = QuantumRegister(n_qbits)
        value = QuantumRegister(c_qbits)
        ancilla = QuantumRegister(1)
        extra = QuantumRegister(6)
        precision = QuantumRegister(self.precision_bits)
        circuit = QuantumCircuit(precision, key, value, ancilla, extra)

        # TODO make arguments
        def prepare_once():
            circuit.h(key)
            circuit.h(value)
            circuit.h(precision)

            # eigenvector for Ry
            circuit.rx(np.pi/2, ancilla[0])
            circuit.z(ancilla[0])
            circuit.x(ancilla[0])

        def unprepare_once():
            circuit.rx(-np.pi/2, ancilla[0])

        # amplitude estimation (counting) algorithm
        prepare_once()
        for i in range(len(precision)):
            for _ in range(2**i):
                # oracle
                self.prepare(f, circuit, key, value, ancilla, extra)
                if oracle is not None:
                    oracle(circuit, [precision[i]], value, extra, ancilla)
                self.unprepare(f, circuit, key, value, ancilla, extra)

                # diffusion
                diffusion(circuit, [precision[i]], [key[i] for i in range(len(key))], extra) # if f(0) = 0
                # diffusion(circuit, [precision[i]], [key[i] for i in range(len(key))] + [value[i] for i in range(len(value))], extra)
        # inverse fourier tranform
        iqft(circuit, [precision[i] for i in range(len(precision))])
        unprepare_once()

        return circuit

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

        for v in sorted(entries.items(), key=lambda x: x[1]):
            print(v[1])
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
        circuit = self.__build_circuit(self.key_bits, self.value_bits, self.f)
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

        _, outcomes = self._QDictionary__process(self.key_bits, self.value_bits, probs, neg)
        ordered_outcomes = sorted(outcomes.items(), key=lambda x: x[1], reverse=True)

        print("Outcomes", ordered_outcomes)
        return ordered_probs[0][0]

    def get_zero_count(self):
        return self.get_value_count(oracle0)

    def get_count_for_value(self, v):
        return self.get_value_count(get_oracle(v))

    def get_negative_value_count(self):
        return self.get_value_count(oracle_first_bit_one)

    def get_value_count(self, oracle):
        count = int(round(2**self.key_bits*self.get_value_amplitude(oracle)))
        print("Count =", count)
        return count

    def get_value_amplitude(self, oracle):
        circuit = self.__build_circuit_count(self.key_bits, self.value_bits, self.f, oracle)
        probs = get_probs((circuit, None, None), 'sim', False)
        ordered_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        print("number of outcomes:", len(ordered_probs))
        print("probabilities = ", ordered_probs)

        counts = sorted(list(map(lambda item: (int(item[0][:self.precision_bits], 2), item[1]), ordered_probs)), key=lambda x: x[1], reverse=True)
        print("counts = ", counts)

        combined_frequency = {}
        for k, v in counts:
            combined_frequency[k] = np.round(combined_frequency.get(k, 0) + v, 4)
        sorted_counts = sorted(combined_frequency.items(), key=lambda x: x[1], reverse=True)
        print("combined_frequencies = ", sorted_counts)

        sines = {}
        for k, v in counts:
            key = np.round(np.cos(np.pi*k/2**self.precision_bits)**2, 4)
            sines[key] = sines.get(key, 0) + v
        sorted_sines = sorted(sines.items(), key=lambda x: x[1], reverse=True)
        print("sines = ", sorted_sines)

        estimate = round(sorted_sines[0][0], 4)
        print("Amplitude Estimate = ", estimate)
        print("Uniformly Scaled Estimate = ", 2**self.key_bits*estimate)
        return estimate

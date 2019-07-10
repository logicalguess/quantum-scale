from qiskit import QuantumRegister, QuantumCircuit

import numpy as np
import math

from circuit_util import controlled_ry, qft, iqft, grover, oracle0, diffusion, cxzx, on_match_ry
from util import get_probs, plot_histogram


class QDictionary():
    # A Quantum Dictionary

    def __init__(self, key_bits, value_bits, precision_bits, f, prepare, unprepare = None):
        self.key_bits = key_bits
        self.value_bits = value_bits
        if precision_bits > 0:
            self.precision_bits = precision_bits
        self.f = f
        self.populate = prepare
        self.unpopulate = unprepare



    def __build_circuit(self, n_qbits, c_qbits, f, search_key = None):
        key = QuantumRegister(n_qbits)
        value = QuantumRegister(c_qbits)
        ancilla = QuantumRegister(1)
        extra = QuantumRegister(max(n_qbits, c_qbits))
        circuit = QuantumCircuit(key, value, ancilla, extra)


        for i in range(n_qbits):
            circuit.h(key[i])

        for i in range(c_qbits):
            circuit.h(value[i])

        if search_key is not None:
            iterations = 1 if n_qbits == 2 else 2**(math.floor(n_qbits/2))
            for i in range(iterations):
                grover(search_key, circuit, key, extra, ancilla)

        circuit.rx(np.pi/2, ancilla[0])
        circuit.z(ancilla[0])
        circuit.x(ancilla[0])

        self.populate(f, circuit, key, value, ancilla, extra)

        # inverse fourier tranform
        iqft(circuit, [value[i] for i in range(len(value))])

        circuit.rx(-np.pi/2, ancilla[0])

        return circuit


    def __build_circuit_count(self, n_qbits, c_qbits, f):
        key = QuantumRegister(n_qbits)
        value = QuantumRegister(c_qbits)
        ancilla = QuantumRegister(1)
        extra = QuantumRegister(6)
        precision = QuantumRegister(self.precision_bits)
        circuit = QuantumCircuit(precision, key, value, ancilla, extra)


        for i in range(n_qbits):
            circuit.h(key[i])

        for i in range(c_qbits):
            circuit.h(value[i])

        for i in range(len(precision)):
            circuit.h(precision[i])

        def op():
            # controlled rotations
            self.populate(f, circuit, key, value, ancilla, extra)
            # inverse fourier to retrieve best approximations
            iqft(circuit, [value[i] for i in range(c_qbits)])

        def op_i():
            # fourier transform
            qft(circuit, [value[i] for i in range(c_qbits)])

            # controlled rotations
            self.unpopulate(f, circuit, key, value, ancilla, extra)

        for i in range(len(precision)):
            for _ in range(2**i):
                # oracle
                op()
                oracle0(circuit, [precision[i]], value, extra, ancilla)
                op_i()

                # diffusion
                diffusion(circuit, [precision[i]], key, extra)

        # inverse fourier tranform
        iqft(circuit, [precision[i] for i in range(len(precision))])

        return circuit

    def __process(self, n_bits, c_bits, probs):
        outcomes = {}
        for b, c in probs.items():
            key = int(b[0:n_bits], 2)
            value = int(b[n_bits:n_bits + c_bits], 2)
            print(key, " = ", b[0:n_bits], " -> ", b[n_bits:n_bits + c_bits], " = ", value)
            outcomes['%d' %  key + " -> " + '%d' % value] = c

        return outcomes

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


    def get_value_for_key(self, key = None):
        circuit = self._QDictionary__build_circuit(self.key_bits, self.value_bits, self.f, key)
        probs = get_probs((circuit, None, None), 'sim')

        from qiskit.tools import visualization
        visualization.plot_histogram(probs)

        ordered_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        print("Probabilities: ", ordered_probs)

        outcomes = self._QDictionary__process(self.key_bits, self.value_bits, probs)
        ordered_outcomes = sorted(outcomes.items(), key=lambda x: x[1], reverse=True)

        print("Outcomes", ordered_outcomes)

    def get_zero_count(self):
        circuit = self._QDictionary__build_circuit_count(self.key_bits, self.value_bits, self.f)
        probs = get_probs((circuit, None, None), 'sim', False)
        ordered_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        print("number of outcomes:", len(ordered_probs))
        print("probabilities = ", ordered_probs)

        counts = sorted(list(map(lambda item: (int(item[0][:self.precision_bits], 2), item[1]), ordered_probs)), key=lambda x: x[1], reverse=True)
        print("counts = ", counts)

        combined_counts = {}
        for k, v in counts:
            combined_counts[k] = np.round(combined_counts.get(k, 0) + v, 4)
        sorted_counts = sorted(combined_counts.items(), key=lambda x: x[1], reverse=True)
        print("combined_counts = ", sorted_counts)

        sines = {}
        for k, v in counts:
            key = 2**self.value_bits*np.round(np.cos(np.pi*k/2**self.precision_bits)**2, 4)
            sines[key] = sines.get(key, 0) + v
        sorted_sines = sorted(sines.items(), key=lambda x: x[1], reverse=True)
        print("sines = ", sorted_sines)

        estimate = int(round(sorted_sines[0][0]))
        print("Best Estimate = ", estimate)
        return estimate

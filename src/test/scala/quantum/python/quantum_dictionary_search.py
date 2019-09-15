import numpy as np
from qiskit import QuantumRegister, QuantumCircuit


def build_circuit(n_qbits, c_qbits, f, prepare, unprepare, oracle):
    key = QuantumRegister(n_qbits)
    value = QuantumRegister(c_qbits)
    ancilla = QuantumRegister(1)
    extra = QuantumRegister(max(n_qbits, c_qbits) + 1)
    circuit = QuantumCircuit(key, value, ancilla, extra)

    def prepare_once():
        circuit.h(key)
        circuit.h(value)

        circuit.rx(np.pi / 2, ancilla[0])
        circuit.z(ancilla[0])
        circuit.x(ancilla[0])

    def unprepare_once():
        circuit.rx(-np.pi / 2, ancilla[0])

    prepare_once()

    # prepare(f, circuit, key, value, ancilla, extra)

    for i in range(1):
        iterate(circuit, key, value, value, extra, ancilla, prepare, unprepare, oracle)

    prepare(f, circuit, key, value, ancilla, extra)

    unprepare_once()

    return circuit


def iterate(circuit, key, value, search, e, a, prepare, unprepare, oracle):
    key_value = [key[i] for i in range(len(key))] + [value[i] for i in range(len(value))]
    prepare(f, circuit, key, value, a, e)

    # oracle
    oracle(circuit, search, e, a)
    unprepare(f, circuit, key, value, a, e)

    # diffusion
    for i in range(0, len(key_value)):
        circuit.h(key_value[i])
        circuit.x(key_value[i])

    # controlled Z
    controlled_Z(circuit, [key_value[i] for i in range(0, len(key_value) - 1)], e, [key_value[len(key_value) - 1]])

    for i in range(0, len(key_value)):
        circuit.x(key_value[i])
        circuit.h(key_value[i])

    # prepare(f, circuit, key, value, a, e)


def process(n_bits, c_bits, probs, neg=False):
    kvs = {}
    entries = {}
    outcomes = {}
    for b, c in probs.items():
        key = int(b[0:n_bits], 2)
        value = int(b[n_bits:n_bits + c_bits], 2)
        kvs[key] = value
        if neg is True and value >= 2 ** (c_bits - 1):
            value = value - 2 ** c_bits
        entries[key] = '%d' % key + " = " + b[0:n_bits] + " -> " + b[n_bits:n_bits + c_bits] + " = " + '%d' % value
        idx = '%d' % key + " -> " + '%d' % value
        outcomes[idx] = outcomes.get(idx, 0) + c

    # for v in sorted(entries.items(), key=lambda x: x[1]):
    #     print(v[1])
    return sorted(kvs.items(), key=lambda x: x[1]), outcomes


def process_values(n_bits, c_bits, probs, neg=False):
    value_freq = {}
    for b, c in probs.items():
        value = int(b[n_bits:n_bits + c_bits], 2)
        if neg is True and value >= 2 ** (c_bits - 1):
            value = value - 2 ** c_bits
        value_freq[value] = value_freq.get(value, 0) + c

    factor = 1.0 / sum(value_freq.values())
    value_freq = {k: v * factor for k, v in value_freq.items()}

    return value_freq


def get_value_distribution(circuit, key_bits, value_bits, neg=False):
    probs = get_probs(circuit, False)

    ordered_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    print("Probabilities: ", ordered_probs)

    v_freq = process_values(key_bits, value_bits, probs, neg)

    from qiskit.tools import visualization
    visualization.plot_histogram(v_freq)

    ordered_freq = sorted(v_freq.items(), key=lambda x: x[1], reverse=True)

    print("Value Distribution", ordered_freq)


def get_value_for_key(circuit, key_bits, value_bits, neg=False):
    probs = get_probs(circuit, False)

    from qiskit.tools import visualization
    visualization.plot_histogram(probs)

    ordered_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    print("Probabilities: ", ordered_probs)

    _, outcomes = process(key_bits, value_bits, probs, neg)
    ordered_outcomes = sorted(outcomes.items(), key=lambda x: x[1], reverse=True)

    print("Outcomes", ordered_outcomes)
    return ordered_probs[0][0]

# ######## circuit utilities


# multiply by -1
def czxzx(qc, q_control, q_target):
    qc.cx(q_control, q_target)
    qc.cz(q_control, q_target)
    qc.cx(q_control, q_target)
    qc.cz(q_control, q_target)


def qft(qc, q):
    for j in range(len(q)):
        qc.h(q[j])
        for k in range(j + 1, len(q)):
            qc.cu1(np.pi/float(2**(k - j)), q[k], q[j])


def iqft(qc, q):
    for j in range(len(q))[::-1]:
        qc.h(q[j])
        for k in range(j)[::-1]:
            qc.cu1(-np.pi/float(2**(j-k)), q[j], q[k])


def controlled_Z(qc, ctrl, anc, tgt):
    return controlled(qc, ctrl, anc, tgt, c_gate = lambda qc, ctrl, tgt: qc.cz(ctrl, tgt))


def controlled(qc, ctrl, anc, tgt, c_gate = lambda qc, c, t: qc.cx(c, t), cc_gate = lambda qc, c1, c2, t: qc.ccx(c1, c2, t)):
    n = len(ctrl)

    if n == 1:
        c_gate(qc, ctrl[0], tgt[0])
        return

    # compute
    cc_gate(qc, ctrl[0], ctrl[1], anc[0])
    for i in range(2, n):
        cc_gate(qc, ctrl[i], anc[i-2], anc[i-1])

    # copy
    c_gate(qc, anc[n-2], tgt[0])

    # uncompute
    for i in range(n-1, 1, -1):
        cc_gate(qc, ctrl[i], anc[i-2], anc[i-1])
    cc_gate(qc, ctrl[0], ctrl[1], anc[0])


def cry(theta, qc, q_control, q_target):
    qc.ry(theta / 2, q_target)
    qc.cx(q_control, q_target)
    qc.ry(-theta / 2, q_target)
    qc.cx(q_control, q_target)


def controlled_ry(qc, theta, ctrl, anc, tgt):
    return controlled(qc, ctrl, anc, tgt, c_gate = lambda qc, c, t: cry(theta, qc, c, t))


def is_bit_not_set(m, k):
    return not (m & (1 << k))


def on_match_ry(n, m, qc, theta, q, e, t):
    for i in range(0, n):
        if is_bit_not_set(m, i):
            qc.x(q[n - i - 1])

    controlled_ry(qc, theta, q, e, t)

    for i in range(0, n):
        if is_bit_not_set(m, i):
            qc.x(q[n - i - 1])

# ####### running utilities


def histogram(state, prnt=True):
    n = len(state)
    pow = int(np.log2(n))
    keys = [bin(i)[2::].rjust(pow, '0')[::-1] for i in range(0, n)]
    #keys = [bin(i)[2::].rjust(pow, '0') for i in range(0, n)]

    if prnt:
        print("Quantum state:", dict(zip(keys, state)))

    filtered_state = dict(filter(lambda p: abs(p[1])*abs(p[1]) > 0, dict(zip(keys, state)).items()))
    from pprint import pprint
    if prnt:
        pprint(filtered_state)

    probs = [np.round(abs(a)*abs(a), 5) for a in state]
    hist = dict(zip(keys, probs))
    if prnt:
        print("hist", hist)
    filtered_hist = dict(filter(lambda p: p[1] > 0, hist.items()))
    return filtered_hist


def get_probs(qc, prnt = True):
    from qiskit import execute

    job = execute([qc], backend='local_statevector_simulator', shots=1)
    result = job.result()
    state = np.round(result.get_data(qc)['statevector'], 5)
    return histogram(state, prnt)


if __name__ == "__main__":

    def prepare_function(f, circuit, key, value, ancilla, extra):
        for i in range(len(value)):
            for k in range(2 ** len(key)):
                on_match_ry(len(key), k, circuit, 1 / 2 ** len(value) * 2 * np.pi * 2 ** (i + 1) * f[k],
                            [key[j] for j in range(0, len(key))] + [value[i]], extra, ancilla)

        iqft(circuit, [value[i] for i in range(len(value))])


    def unprepare_function(f, circuit, key, value, ancilla, extra):
        qft(circuit, [value[i] for i in range(len(value))])

        for i in range(len(value)):
            for k in range(2 ** len(key)):
                on_match_ry(len(key), k, circuit, -1 / 2 ** len(value) * 2 * np.pi * 2 ** (i + 1) * f[k],
                            [key[j] for j in range(0, len(key))] + [value[i]], extra, ancilla)


    def oracle_first_bit_one(qc, search, e, a):
        controlled(qc, [search[0]], e, a, c_gate = czxzx)

    def get_oracle(m):
        def oracle(qc, q, e, a):
            n = len(q)
            for i in range(0, n):
                if is_bit_not_set(m, i):
                    qc.x(q[n - i - 1])

            controlled(qc, [q[i] for i in range(len(q))], e, a, c_gate = czxzx)

            for i in range(0, n):
                if is_bit_not_set(m, i):
                    qc.x(q[n - i - 1])

        return oracle

    n_key = 3
    n_value = 4

    f = [0, 3, 0, -7, 0, -5, 7, -7]

    # oracle = get_oracle(0)
    oracle = oracle_first_bit_one

    circuit = build_circuit(n_key, n_value, f, prepare_function, unprepare_function, oracle)

    get_value_for_key(circuit, n_key, n_value, True)
    # get_value_distribution(circuit, n_key, n_value, True)

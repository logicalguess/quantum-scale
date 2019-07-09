import numpy as np

# importing QISKit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, compile, execute, register, available_backends, get_backend
from qiskit.tools import visualization
import Qconfig


def cry(theta, qc, q_control, q_target):
    qc.ry(theta/2, q_target)
    qc.cx(q_control, q_target)
    qc.ry(-theta/2, q_target)
    qc.cx(q_control, q_target)


def build_circuit(n):
    q = QuantumRegister(n)
    c = ClassicalRegister(n)

    qc = QuantumCircuit(q, c)

    for i in range(0, n):
        #qc.h(q[i])
        qc.ry(np.pi/2, q[i])

    for i in range(0,  n - 1):
        cry(-np.pi/2, qc, q[i], q[i + 1])

    return qc, q, c


def run(n, qc, cfg, backend = None):
    if 'url' in cfg.keys():
        register(cfg['token'], cfg['url'], cfg['hub'], cfg['group'], cfg['project'])
        print(available_backends())

    if backend is None:
        backend = cfg['backend']

    backend_config = get_backend(backend).configuration
    backend_coupling = backend_config['coupling_map']

    qc_compiled = compile([qc], backend=backend, coupling_map=backend_coupling, seed=0)
    qc_compiled_qasm = qc_compiled['circuits'][0]['compiled_circuit_qasm']
    #print(qc_compiled_qasm)

    job = execute([qc], backend=backend, shots=int(np.power(2, n + 2)))
    result = job.result()

    return result


def get_counts(n, cfg, backend = None):
    qc, qr, cr = build_circuit(n)
    qc.measure(qr, cr)
    result = run(n, qc, Qconfig.cfg[cfg], backend)
    counts = result.get_counts()
    # visualization.plot_circuit(qc)
    return counts


def histogram(state):
    n = len(state)
    pow = int(np.log2(n))
    keys = [bin(i)[2::].rjust(pow, '0')[::-1] for i in range(0, n)]
    print(dict(zip(keys, state)))

    probs = [np.round(abs(a)*abs(a), 5) for a in state]
    hist = dict(zip(keys, probs))
    filtered_hist = dict(filter(lambda p: p[1] > 0, hist.items()))
    return filtered_hist


def get_probs(n, cfg):
    qc, _, _ = build_circuit(n)
    # visualization.plot_circuit(qc)
    result = run(n, qc, Qconfig.cfg[cfg], 'local_statevector_simulator')
    state = np.round(result.get_data(qc)['statevector'], 5)
    return histogram(state)


if __name__ == "__main__":
    for i in range(1, 11):
        hist = get_counts(i, 'sim')
        print("F(", i, ") = ", len(hist))
        #visualization.plot_histogram(hist)

# F( 1 ) =  2
    # F( 2 ) =  3
    # F( 3 ) =  5
    # F( 4 ) =  8
    # F( 5 ) =  13
    # F( 6 ) =  21
    # F( 7 ) =  34
    # F( 8 ) =  55
    # F( 9 ) =  89


#######
import math
import numpy as np

# importing QISKit
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.tools import visualization

import util


def cry(theta, qc, q_control, q_target):
    qc.ry(theta / 2, q_target)
    qc.cx(q_control, q_target)
    qc.ry(-theta / 2, q_target)
    qc.cx(q_control, q_target)


def crz(theta, qc, q_control, q_target):
    qc.rz(theta / 2, q_target)
    qc.cx(q_control, q_target)
    qc.rz(-theta / 2, q_target)
    qc.cx(q_control, q_target)


def c_ry(qc, theta, ctrl, anc, tgt):
    return util.controlled(qc, ctrl, anc, tgt, c_gate = lambda qc, c, t: cry(theta, qc, c, t))


def qft(qc, q):
    for j in range(len(q)):
        qc.h(q[j])
        for k in range(j + 1, len(q)):
            qc.cu1(np.pi/float(2**(k - j)), q[k], q[j])
            # crz(-np.pi/float(2**(j-k)), qc, q[j], q[k])


def iqft(qc, q):
    for j in range(len(q))[::-1]:
        qc.h(q[j])
        for k in range(j)[::-1]:
            qc.cu1(-np.pi/float(2**(j-k)), q[j], q[k])
            # crz(-np.pi/float(2**(j-k)), qc, q[j], q[k])


def process(n_bits, c_bits, probs):
    for b, c in probs.items():
        input = int(b[0:n_bits], 2)
        output = int(b[n_bits:n_bits + c_bits], 2)
        print(input, " -> ", output)

# multiply by -1
def cxzx(qc, q_control, q_target):
    qc.cx(q_control, q_target)
    qc.cz(q_control, q_target)
    qc.cx(q_control, q_target)
    #qc.cz(q_control, q_target)


def oracle(qc, c, q, e, a):
    for i in range(0, len(q)):
        qc.x(q[i])

    util.controlled(qc, [c[i] for i in range(len(c))] + [q[i] for i in range(len(q))], e, a, c_gate = cxzx)

    for i in range(0, len(q)):
        qc.x(q[i])


def diffusion(qc, c, q, e):
    for i in range(0, len(q)):
        qc.h(q[i])
        qc.x(q[i])

    # controlled Z
    util.controlled_Z(qc, [c[i] for i in range(len(c))] + [q[i] for i in range(0, len(q) - 1)], e, [q[len(q) - 1]])

    for i in range(0, len(q)):
        qc.x(q[i])
        qc.h(q[i])


def process(n_bits, c_bits, c1_bits, probs, out = 0):
    outcomes = {}
    for b, c in probs.items():
        input = int(b[c1_bits:c1_bits + n_bits], 2)
        output = int(b[c1_bits + n_bits:c1_bits + n_bits + c_bits], 2)
        outcomes['%d' %  input + " -> " + '%d' % output] = c
        # if output == out:
        #     print(b[0:c1_bits + n_bits], " - ", input, " = ", b[c1_bits:c1_bits + n_bits], " -> ", output)

        return outcomes


def build_circuit(n_qbits, c_qbits, c1_qbits):
    t = QuantumRegister(n_qbits)
    c = QuantumRegister(c_qbits)
    a = QuantumRegister(1)
    e = QuantumRegister(5)
    c1 = QuantumRegister(c1_qbits, "control")

    qc = QuantumCircuit(c1, t, c, a, e)

    def op():
        # controlled rotations
        for i in range(c_qbits):

            # encode the number of consecutive pairs of 1
            for j in range(n_qbits):
                c_ry(qc, 1/2**c_qbits * 2*np.pi* 2**(i+1)*f[j] , [t[j], c[i]], e, a[0]) # sum on powers of 2

        # inverse fourier to retrieve best approximations
        iqft(qc, [c[i] for i in range(c_qbits)])

    def op_i():
        # fourier transform
        qft(qc, [c[i] for i in range(c_qbits)])

        # controlled rotations
        for i in range(c_qbits):

            # unencode the number of consecutive pairs of 1
            for j in range(n_qbits):
                c_ry(qc, -1/2**c_qbits * 2*np.pi* 2**(i+1)*f[j] , [t[j], c[i]], e, a[0]) # sum on powers of 2

    # counting
    for i in range(len(c1)):
        qc.h(c1[i])
    # qft(qc, [c1[i] for i in range(len(c1))])


    for i in range(n_qbits):
        qc.h(t[i])

    for i in range(c_qbits):
        qc.h(c[i])

    for i in range(len(c1)):
        for _ in range(2**i):
            # oracle
            op()
            oracle(qc, [c1[i]], c, e, a)
            op_i()

            # diffusion
            diffusion(qc, [c1[i]], t, e)

    iqft(qc, [c1[i] for i in range(len(c1))])

    return qc


if __name__ == "__main__":
    # f = [2, 2, 2, -3]
    f = [1, 1, -1]
    n_tgt_bits = len(f)
    n_ctrl_bits = len(f) #math.ceil(math.log2(n_tgt_bits))

    ctrl_bits = 5

    qc = build_circuit(n_tgt_bits, n_ctrl_bits, ctrl_bits)
    # visualization.plot_circuit(qc)

    probs = util.get_probs((qc, None, None), 'sim', False)

    outcomes  = process(n_tgt_bits, n_ctrl_bits, ctrl_bits, probs)
    print("outcomes", outcomes)
    # plot_histogram(outcomes)

    visualization.plot_histogram(outcomes)
    tgt_bits = n_tgt_bits

    ordered_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    print("number of outcomes:", len(ordered_probs))
    print("probabilities = ", ordered_probs)

    counts = sorted(list(map(lambda item: (int(item[0][:ctrl_bits], 2), item[1]), ordered_probs)), key=lambda x: x[1], reverse=True)
    print("counts = ", counts)

    combined_counts = {}
    for k, v in counts:
        combined_counts[k] = np.round(combined_counts.get(k, 0) + v, 4)
    sorted_counts = sorted(combined_counts.items(), key=lambda x: x[1], reverse=True)
    print("combined_counts = ", sorted_counts)

    sines = {}
    for k, v in counts:
        key = 2**tgt_bits*np.round(np.cos(np.pi*k/2**ctrl_bits)**2, 4)
        sines[key] = sines.get(key, 0) + v
    sorted_sines = sorted(sines.items(), key=lambda x: x[1], reverse=True)
    print("sines = ", sorted_sines)

    print("Best Estimate = ", int(round(sorted_sines[0][0])))

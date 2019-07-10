import numpy as np

# importing QISKit
from qiskit import compile, execute, register, available_backends, get_backend
from Qconfig import cfg as Qcfg

def run(shots, qc, cfg, backend = None):
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

    job = execute([qc], backend=backend, shots=shots)
    result = job.result()

    return result


def get_counts(c, cfg, backend = None):
    qc, qr, cr = c
    qc.measure(qr, cr)
    result = run(1024, qc, Qcfg[cfg], backend)
    counts = result.get_counts()
    # visualization.plot_circuit(qc)
    return counts


def histogram(state, prnt = True):
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
    # plot_state(hist)
    filtered_hist = dict(filter(lambda p: p[1] > 0, hist.items()))
    return filtered_hist


def get_probs(c, cfg, prnt = True):
    qc, _, _ = c
    # visualization.plot_circuit(qc)
    result = run(1, qc, Qcfg[cfg], 'local_statevector_simulator')
    state = np.round(result.get_data(qc)['statevector'], 5)
    return histogram(state, prnt)


def get_state_and_probs(c, cfg):
    qc, _, _ = c
    # visualization.plot_circuit(qc)
    result = run(1, qc, Qcfg[cfg], 'local_statevector_simulator')
    state = np.round(result.get_data(qc)['statevector'], 5)

    n = len(state)
    pow = int(np.log2(n))
    keys = [bin(i)[2::].rjust(pow, '0')[::-1] for i in range(0, n)]
    #keys = [bin(i)[2::].rjust(pow, '0') for i in range(0, n)]

    return dict(zip(keys, state)), histogram(state)


from collections import Counter
import matplotlib.pyplot as plt


def plot_histogram(data, number_to_keep=False):
    """Plot a histogram of data.

    data is a dictionary of  {'000': 5, '010': 113, ...}
    number_to_keep is the number of terms to plot and rest is made into a
    single bar called other values
    """

    from collections import Counter
    import matplotlib.pyplot as plt

    if number_to_keep is not False:
        data_temp = dict(Counter(data).most_common(number_to_keep))
        data_temp["rest"] = sum(data.values()) - sum(data_temp.values())
        data = data_temp

    labels = sorted(data)
    values = np.array([data[key] for key in labels], dtype=float)
    pvalues = values #/ sum(values)
    print(pvalues)
    numelem = len(values)
    ind = np.arange(numelem)  # the x locations for the groups
    width = 0.5  # the width of the bars
    _, ax = plt.subplots()
    rects = ax.bar(ind, pvalues, width, color='red')
    # add some text for labels, title, and axes ticks
    ax.set_ylabel('Measurement Probabilities', fontname='Arial', fontsize=16)
    ax.set_xlabel('Key - Value Pairs', fontname='Arial', fontsize=16)
    ax.set_xticks(ind)
    ax.set_xticklabels(labels, fontname='Arial', fontsize=10, rotation=0)
    ax.set_ylim([0., min([1., max([1.5 * val for val in pvalues])])])
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        if height > 0.02:
            ax.text(rect.get_x() + rect.get_width() / 2., height + 0.02,
                    #'%f' % float(height),
                    height, fontname='Arial', fontsize=8,
                    ha='center', va='bottom', rotation = 90 if height < 0.01 else 0)
    plt.show()
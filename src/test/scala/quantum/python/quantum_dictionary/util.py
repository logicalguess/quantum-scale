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


def plot_bin_and_arrow(x0, y0, x, y, color, alpha, factor, label=''):
    plt.scatter(x0, y0, s=50, color=color, alpha=alpha)

    text_x = x0 - len(label) - 3 if x > 0 else x0 + 2
    plt.text(text_x, y0, label, fontsize=12, verticalalignment='center')

    plt.arrow(x0, y0, x*factor, -y*factor, head_length=0, head_width=0, width=0, color=color, linewidth=5, alpha=alpha)


def plot_state(bins, colors=None):
    plt.axis('off')
    plt.grid(False)

    import math

    n_qbits = math.log2(len(bins))
    plt.axis([-40, 60, 80 + 10*len(bins), 0])

    if colors is None:
        colors =['r', 'g', 'b', 'y', 'orange', 'm', 'c', 'purple']

    i = 0
    alpha = 0
    for b in bins:
        if i % 8 and i != 0:
            alpha = alpha + 1

        alpha = 1 - 0.25*alpha

        factor = 10*n_qbits if abs(bins[b].real) < 1 or abs(bins[b].imag) < 1 else n_qbits
        plot_bin_and_arrow(10, 10 + 15*i, bins[b].real, bins[b].imag, colors[i % 8], alpha, factor, b)

        if i + 1 != len(bins):
            plt.arrow(10, 13 + 15*i, 0, 9, color='gray', width=0, linewidth=5, alpha=0.5)

        i = i + 1

    plt.show()

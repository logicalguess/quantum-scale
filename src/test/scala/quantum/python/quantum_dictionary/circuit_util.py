import numpy as np


def controlled_X(qc, ctrl, anc, tgt):
    return controlled(qc, ctrl, anc, tgt)


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


def cry(theta, qc, q_control, q_target):
    qc.ry(theta / 2, q_target)
    qc.cx(q_control, q_target)
    qc.ry(-theta / 2, q_target)
    qc.cx(q_control, q_target)


def controlled_ry(qc, theta, ctrl, anc, tgt):
    return controlled(qc, ctrl, anc, tgt, c_gate = lambda qc, c, t: cry(theta, qc, c, t))

def cx(qc, q_control, q_target):
    qc.cx(q_control, q_target)


# multiply by -1
def czxzx(qc, q_control, q_target):
    qc.cx(q_control, q_target)
    qc.cz(q_control, q_target)
    qc.cx(q_control, q_target)
    qc.cz(q_control, q_target)


# multiply by -1
def cxzx(qc, q_control, q_target):
    qc.cx(q_control, q_target)
    qc.cz(q_control, q_target)
    qc.cx(q_control, q_target)
    # qc.cz(q_control, q_target)


def grover(m, qc, q, e, a):
    qc.x(a[0])
    qc.h(a[0])

    n = len(q)
    for i in range(0, n):
        if is_bit_not_set(m, i):
            qc.x(q[n - i - 1])

    # oracle
    controlled_X(qc, q, e, a)
    # controlled(qc, q, e, a, c_gate = lambda qc, ctrl, tgt: czxzx(qc, ctrl, tgt))

    # diffusion
    for i in range(0, len(q)):
        qc.h(q[i])
        qc.x(q[i])

    # controlled Z
    controlled_Z(qc, [q[i] for i in range(0, len(q) - 1)], e, [q[len(q) - 1]])

    for i in range(0, len(q)):
        qc.x(q[i])
        qc.h(q[i])

    for i in range(0, n):
        if is_bit_not_set(m, i):
            qc.x(q[n - i - 1])

    qc.h(a[0])
    qc.x(a[0])


def get_oracle(m):
    def oracle(qc, c, q, e, a):
        n = len(q)
        for i in range(0, n):
            if is_bit_not_set(m, i):
                qc.x(q[n - i - 1])

        controlled(qc, [c[i] for i in range(len(c))] + [q[i] for i in range(len(q))], e, a, c_gate = czxzx)

        for i in range(0, n):
            if is_bit_not_set(m, i):
                qc.x(q[n - i - 1])

    return oracle


def oracle_first_bit_one(qc, c, q, e, a):
    controlled(qc, [c[i] for i in range(len(c))] + [q[0]], e, a, c_gate = czxzx)


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


def oracle0(qc, c, q, e, a):
    for i in range(0, len(q)):
        qc.x(q[i])

    controlled(qc, [c[i] for i in range(len(c))] + [q[i] for i in range(len(q))], e, a, c_gate = czxzx)

    for i in range(0, len(q)):
        qc.x(q[i])


def oracle0_trick(qc, c, q, e, a):
    qc.x(a[0])
    qc.h(a[0])

    for i in range(0, len(q)-1):
        qc.x(q[i])

    controlled(qc, [c[i] for i in range(len(c))] + [q[i] for i in range(len(q))], e, a)
    # controlled(qc, [c[i] for i in range(len(c))] + [q[i] for i in range(len(q))], e, a, c_gate = cxzx)

    for i in range(0, len(q)-1):
        qc.x(q[i])

    qc.h(a[0])
    qc.x(a[0])


def diffusion(qc, c, q, e):
    for i in range(0, len(q)):
        qc.h(q[i])
        qc.x(q[i])

    # controlled Z
    controlled_Z(qc, [c[i] for i in range(len(c))] + [q[i] for i in range(0, len(q) - 1)], e, [q[len(q) - 1]])

    for i in range(0, len(q)):
        qc.x(q[i])
        qc.h(q[i])

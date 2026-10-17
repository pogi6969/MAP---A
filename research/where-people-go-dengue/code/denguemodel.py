"""Where People Go, Dengue Goes: core model.

A residence-time (Lagrangian) host-vector model of dengue on a network of
barangays, its reproduction number, place-by-place decomposition, least-cost
vector control as a convex program, residence-to-place inversion of case
counts, and a Poisson CUSUM early-warning rule.

The independent reference implementations used to check this module live in
verify_dengue.py.
"""

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog, nnls
from scipy.stats import poisson


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

@dataclass
class Params:
    a: float = 0.29          # bites per mosquito per day
    b: float = 0.50          # mosquito-to-human transmission probability per bite
    c: float = 0.50          # human-to-mosquito transmission probability per bite
    mu_v: float = 0.10       # mosquito death rate per day (10-day mean life)
    nu: float = 1 / 8        # rate of leaving the extrinsic incubation period
    gamma: float = 1 / 5     # human recovery rate (5-day infectious period)
    mu_h: float = 1 / (70 * 365)   # human birth and death rate


def kappa(par):
    """Equation (8): two-generation constant of the Ross-Macdonald number."""
    return (par.a ** 2 * par.b * par.c * par.nu /
            (par.mu_v * (par.nu + par.mu_v) * (par.gamma + par.mu_h)))


# ---------------------------------------------------------------------------
# Mobility
# ---------------------------------------------------------------------------

def residence_time_matrix(omega, attract, travel, beta):
    """Definition 3: p_ii = 1 - omega_i, p_ij = omega_i * pi_ij for j != i,
    with pi_ij proportional to attract_j * exp(-beta * travel_ij)."""
    n = len(omega)
    P = np.zeros((n, n))
    for i in range(n):
        w = np.array([attract[j] * math.exp(-beta * travel[i][j]) if j != i else 0.0
                      for j in range(n)])
        tot = w.sum()
        P[i, i] = 1.0 - omega[i]
        if tot > 0:
            P[i] += omega[i] * w / tot
        else:
            P[i, i] = 1.0
    return P


def present_population(P, N):
    """N~_j = sum_k p_kj N_k: average number of people present in place j."""
    return P.T @ N


# ---------------------------------------------------------------------------
# Reproduction number
# ---------------------------------------------------------------------------

def weights(P, N, V, u=None):
    Nt = present_population(P, N)
    keep = np.ones(len(V)) if u is None else 1.0 - np.asarray(u)
    return keep * V / Nt ** 2


def host_host_matrix(P, N, V, par, u=None):
    """M = kappa D_N P W P^T (Proposition 1)."""
    W = weights(P, N, V, u)
    return kappa(par) * (N[:, None] * P) @ (W[:, None] * P.T)


def symmetric_matrix(P, N, V, par, u=None):
    """S = kappa D_N^1/2 P W P^T D_N^1/2, similar to M."""
    W = weights(P, N, V, u)
    Q = np.sqrt(N)[:, None] * P          # rows scaled; column j is q_j
    return kappa(par) * (Q * W[None, :]) @ Q.T


def r0_squared(P, N, V, par, u=None):
    S = symmetric_matrix(P, N, V, par, u)
    return float(np.linalg.eigvalsh(S)[-1])


def r0(P, N, V, par, u=None):
    return math.sqrt(max(0.0, r0_squared(P, N, V, par, u)))


def local_numbers(P, N, V, par, u=None):
    """R_i = kappa * sum_j p_ij (1 - u_j) m_j, with m_j = V_j / N~_j."""
    Nt = present_population(P, N)
    keep = np.ones(len(V)) if u is None else 1.0 - np.asarray(u)
    m = keep * V / Nt
    return kappa(par) * P @ m


def homogeneous_r0_squared(N, V, par):
    """Province-wide average: kappa * (total mosquitoes / total people)."""
    return kappa(par) * V.sum() / N.sum()


def isolated_r0_squared(N, V, par):
    """Each barangay alone, nobody moving: kappa * V_i / N_i."""
    return kappa(par) * V / N


def top_eigen(P, N, V, par, u=None):
    S = symmetric_matrix(P, N, V, par, u)
    vals, vecs = np.linalg.eigh(S)
    v = vecs[:, -1]
    if v.sum() < 0:
        v = -v
    return float(vals[-1]), v, float(vals[-1] - vals[-2]) if len(vals) > 1 else math.inf


def place_shares(P, N, V, par, u=None):
    """Proposition 6: share of R0^2 carried by place j; the shares sum to 1."""
    lam, v, _ = top_eigen(P, N, V, par, u)
    W = weights(P, N, V, u)
    Q = np.sqrt(N)[:, None] * P
    proj = Q.T @ v                       # q_j . v
    contrib = kappa(par) * W * proj ** 2
    return contrib / lam, contrib


def gradient(P, N, V, par, u=None):
    """d R0^2 / d u_j = -kappa * (V_j / N~_j^2) * (q_j . v)^2 (simple eigenvalue)."""
    lam, v, _ = top_eigen(P, N, V, par, u)
    Nt = present_population(P, N)
    Q = np.sqrt(N)[:, None] * P
    proj = Q.T @ v
    return -kappa(par) * (V / Nt ** 2) * proj ** 2


# ---------------------------------------------------------------------------
# Least-cost control (Definition 9, Algorithm 1)
# ---------------------------------------------------------------------------

def certificate_control(P, N, V, par, cost, ubar, r2):
    """LP: min cost.u  s.t.  R_i(u) <= r2 for all i,  0 <= u <= ubar."""
    Nt = present_population(P, N)
    m = V / Nt
    k = kappa(par)
    A = -k * P * m[None, :]              # -kappa p_ij m_j u_j
    b = r2 - k * P @ m
    res = linprog(cost, A_ub=A, b_ub=b, bounds=[(0, ub) for ub in ubar], method="highs")
    if res.status != 0:
        return None
    return res.x


def uniform_control(P, N, V, par, ubar_scalar, r2, tol=1e-10):
    """Smallest common u with R0^2 <= r2 (bisection; R0^2 is decreasing in u)."""
    n = len(V)
    if r0_squared(P, N, V, par) <= r2:
        return np.zeros(n)
    if r0_squared(P, N, V, par, np.full(n, ubar_scalar)) > r2:
        return None
    lo, hi = 0.0, ubar_scalar
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if r0_squared(P, N, V, par, np.full(n, mid)) <= r2:
            hi = mid
        else:
            lo = mid
    return np.full(n, hi)


def scaled_control(P, N, V, par, direction, ubar, r2, tol=1e-10):
    """Smallest t with u = min(t * direction, ubar) meeting R0^2 <= r2."""
    n = len(V)
    d = np.asarray(direction, dtype=float)
    if r0_squared(P, N, V, par) <= r2:
        return np.zeros(n)
    t_hi = 1.0
    while r0_squared(P, N, V, par, np.minimum(t_hi * d, ubar)) > r2:
        t_hi *= 2
        if t_hi > 1e9:
            return None
    lo, hi = 0.0, t_hi
    while hi - lo > tol * max(1.0, hi):
        mid = (lo + hi) / 2
        if r0_squared(P, N, V, par, np.minimum(mid * d, ubar)) <= r2:
            hi = mid
        else:
            lo = mid
    return np.minimum(hi * d, ubar)


def dual_lower_bound(P, N, V, par, cost, ubar, r2, Z):
    """Proposition 9: for any Z >= 0, g(sZ) <= optimal cost for every s >= 0.

    g(Z) = sum_j ubar_j * min(0, c_j - kappa w_j q_j' Z q_j) - tr(Z (r2 I - S(0))).
    The scale s is optimized exactly over the breakpoints of the concave function.
    """
    k = kappa(par)
    W = weights(P, N, V)
    Q = np.sqrt(N)[:, None] * P
    beta = np.einsum("ij,ik,kj->j", Q, Z, Q)          # q_j' Z q_j
    S0 = symmetric_matrix(P, N, V, par)
    base = float(np.trace(Z @ (r2 * np.eye(len(V)) - S0)))
    slope = k * W * beta

    def g(sv):
        return float(np.sum(ubar * np.minimum(0.0, cost - sv * slope)) - sv * base)

    cands = [0.0] + [float(cost[j] / slope[j]) for j in range(len(V)) if slope[j] > 0]
    vals = [g(sv) for sv in cands]
    return max(vals)


def least_cost_control(P, N, V, par, cost, ubar, r2, rel_gap=1e-6, mu=None, max_newton=200):
    """Least-cost control by a barrier (interior-point) method with a certified gap.

    minimize c.u  subject to  r2 I - S(u) > 0,  0 < u < ubar.
    Returns dict(u, upper, lower, iterations) with lower <= optimum <= upper,
    where lower comes from the dual bound of Proposition 9; None if infeasible.
    """
    n = len(V)
    k = kappa(par)
    W = weights(P, N, V)
    Q = np.sqrt(N)[:, None] * P
    ubar = np.asarray(ubar, dtype=float)
    cost = np.asarray(cost, dtype=float)
    if r0_squared(P, N, V, par) <= r2:
        return {"u": np.zeros(n), "upper": 0.0, "lower": 0.0, "iterations": 0}
    if r0_squared(P, N, V, par, ubar) >= r2:
        return None
    eye = np.eye(n)

    def F_of(u):
        a = k * W * (1.0 - u)
        return r2 * eye - (Q * a[None, :]) @ Q.T

    def feasible(u):
        if np.any(u <= 0) or np.any(u >= ubar):
            return False
        try:
            np.linalg.cholesky(F_of(u))
            return True
        except np.linalg.LinAlgError:
            return False

    delta = 1e-3
    u = ubar * (1 - delta)
    while not feasible(u):
        delta /= 2
        u = ubar * (1 - delta)
        if delta < 1e-12:
            return None
    nu = 3.0 * n
    if mu is None:                       # long steps for small problems, shorter for large ones
        mu = min(10.0, max(1.2, 1.0 + 4.0 / math.sqrt(nu)))
    t = nu / max(float(cost @ u), 1e-9)
    newton = 0
    best_lower = 0.0
    while True:
        # centering by damped Newton steps
        for _ in range(max_newton):
            F = F_of(u)
            L = np.linalg.cholesky(F)
            X = np.linalg.solve(L, Q)                  # L^-1 Q
            B = X.T @ X                                # Q' F^-1 Q
            kw = k * W
            grad = t * cost - kw * np.diag(B) - 1.0 / u + 1.0 / (ubar - u)
            H = (kw[:, None] * kw[None, :]) * B ** 2 + np.diag(1.0 / u ** 2 + 1.0 / (ubar - u) ** 2)
            # Newton direction with symmetric diagonal scaling (Jacobi) and a
            # Cholesky solve, which keeps the system well conditioned near the bounds
            dscale = np.sqrt(np.diag(H))
            Hs = H / np.outer(dscale, dscale)
            try:
                Lh = np.linalg.cholesky(Hs)
                y = -np.linalg.solve(Lh.T, np.linalg.solve(Lh, grad / dscale))
            except np.linalg.LinAlgError:
                y = -np.linalg.lstsq(Hs, grad / dscale, rcond=None)[0]
            step = y / dscale
            dec2 = float(-grad @ step)
            if dec2 <= 0:
                break
            newton += 1
            if dec2 / 2 <= 1e-9:
                break
            # backtracking line search that keeps the point strictly feasible
            s_len = 1.0
            phi0 = t * float(cost @ u) - 2 * np.sum(np.log(np.diag(L))) - np.sum(np.log(u)) \
                - np.sum(np.log(ubar - u))
            while True:
                un = u + s_len * step
                if np.all(un > 0) and np.all(un < ubar):
                    try:
                        Ln = np.linalg.cholesky(F_of(un))
                        phin = t * float(cost @ un) - 2 * np.sum(np.log(np.diag(Ln))) \
                            - np.sum(np.log(un)) - np.sum(np.log(ubar - un))
                        if phin <= phi0 - 0.25 * s_len * dec2:
                            break
                    except np.linalg.LinAlgError:
                        pass
                s_len *= 0.5
                if s_len < 1e-14:
                    un = None
                    break
            if un is None:          # no further progress possible in floating point
                break
            u = un
        Z = np.linalg.inv(F_of(u))
        Z = (Z + Z.T) / 2
        best_lower = max(best_lower, dual_lower_bound(P, N, V, par, cost, ubar, r2, Z))
        upper = float(cost @ u)
        if upper - best_lower <= rel_gap * max(upper, 1e-12) or nu / t <= 1e-12 * max(upper, 1.0):
            break
        t *= mu
    return {"u": u, "upper": upper, "lower": best_lower, "iterations": newton}


# ---------------------------------------------------------------------------
# The differential equations (Definition 4)
# ---------------------------------------------------------------------------

def rhs(t, y, P, N, Lam, par):
    n = len(N)
    Sh, Ih, Rh, Sv, Ev, Iv = (y[i * n:(i + 1) * n] for i in range(6))
    Nt = present_population(P, N)
    lam_h = par.a * par.b * (P @ (Iv / Nt))
    lam_v = par.a * par.c * ((P.T @ Ih) / Nt)
    dSh = par.mu_h * N - lam_h * Sh - par.mu_h * Sh
    dIh = lam_h * Sh - (par.gamma + par.mu_h) * Ih
    dRh = par.gamma * Ih - par.mu_h * Rh
    dSv = Lam - lam_v * Sv - par.mu_v * Sv
    dEv = lam_v * Sv - (par.nu + par.mu_v) * Ev
    dIv = par.nu * Ev - par.mu_v * Iv
    return np.concatenate([dSh, dIh, dRh, dSv, dEv, dIv])


def rk4(f, y0, t0, t1, h, args=()):
    n_steps = int(round((t1 - t0) / h))
    y = np.array(y0, dtype=float)
    t = t0
    traj = [y.copy()]
    for _ in range(n_steps):
        k1 = f(t, y, *args)
        k2 = f(t + h / 2, y + h / 2 * k1, *args)
        k3 = f(t + h / 2, y + h / 2 * k2, *args)
        k4 = f(t + h, y + h * k3, *args)
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += h
        traj.append(y.copy())
    return np.array(traj)


def disease_free_state(N, V):
    n = len(N)
    z = np.zeros(n)
    return np.concatenate([N.astype(float), z, z, V.astype(float), z, z])


# ---------------------------------------------------------------------------
# Residence-to-place inversion (Definition 10)
# ---------------------------------------------------------------------------

def infer_places(P, incidence_rate, nonneg=True):
    """Solve incidence_rate = P z for the place pressure z (z >= 0 by NNLS)."""
    if nonneg:
        z, _ = nnls(P, incidence_rate)
        return z
    return np.linalg.solve(P, incidence_rate)


def varah_bound(P):
    """||P^-1||_inf <= 1 / min_i (2 p_ii - 1) when p_ii > 1/2 (Varah, 1975)."""
    margin = np.min(2 * np.diag(P) - 1)
    return math.inf if margin <= 0 else 1.0 / margin


# ---------------------------------------------------------------------------
# Poisson CUSUM (Definition 11)
# ---------------------------------------------------------------------------

def cusum(x, k, h):
    """S_t = max(0, S_{t-1} + x_t - k_t); alarm at the first t with S_t >= h.

    k may be a scalar or a sequence. Returns (S, first alarm index or None).
    """
    S = []
    s = 0.0
    alarm = None
    for t, xt in enumerate(x):
        kt = k[t] if hasattr(k, "__len__") else k
        s = max(0.0, s + xt - kt)
        S.append(s)
        if alarm is None and s >= h:
            alarm = t
    return np.array(S), alarm


def arl_markov(mu, k, h):
    """Exact average run length for integer k, h and Poisson(mu) counts.

    States 0..h-1 are 'no alarm'; S >= h is the alarm. ARL = ((I - Q)^-1 1)_0.
    """
    states = list(range(h))
    Q = np.zeros((h, h))
    for i in states:
        for j in states:
            if j == 0:
                # s' = max(0, i + x - k) = 0  <=>  x <= k - i
                Q[i, j] = poisson.cdf(k - i, mu) if k - i >= 0 else 0.0
            else:
                x = j - i + k
                Q[i, j] = poisson.pmf(x, mu) if x >= 0 else 0.0
    L = np.linalg.solve(np.eye(h) - Q, np.ones(h))
    return float(L[0])


def threshold_arl(mu, c):
    """Single-week rule 'alarm when x > c': geometric run length."""
    p = 1.0 - poisson.cdf(c, mu)
    return math.inf if p <= 0 else 1.0 / p

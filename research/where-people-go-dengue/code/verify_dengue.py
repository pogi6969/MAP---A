"""Verification suite, computational cost, and worked instance D1.

Run:  python3 verify_dengue.py            (writes results.json and figures/)

Every check compares denguemodel.py with an independently written reference
(numerical Jacobians, eigenvalues of the full system, a fine grid, a general
nonlinear solver, direct simulation, or Monte Carlo) on random synthetic
instances. No real case count, barangay, or survey is used.
"""

import json
import math
import os
import time

import numpy as np
from scipy.optimize import minimize
from scipy.stats import poisson

import denguemodel as dm

SEED = 20261017
HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)


# ---------------------------------------------------------------------------
# Random synthetic instances
# ---------------------------------------------------------------------------

def random_params(rng):
    return dm.Params(a=rng.uniform(0.20, 0.35), b=rng.uniform(0.3, 0.7), c=rng.uniform(0.3, 0.7),
                     mu_v=rng.uniform(1 / 14, 1 / 7), nu=rng.uniform(1 / 12, 1 / 6),
                     gamma=rng.uniform(1 / 7, 1 / 4))


def random_instance(rng, n, omega_max=0.45):
    pts = rng.uniform(0.0, 20.0, size=(n, 2))
    travel = np.linalg.norm(pts[:, None] - pts[None, :], axis=2) / 0.4 + 5.0
    N = rng.integers(500, 8001, size=n).astype(float)
    omega = rng.uniform(0.10, omega_max, size=n)
    attract = rng.lognormal(0.0, 0.8, size=n)
    beta = rng.uniform(0.02, 0.10)
    P = dm.residence_time_matrix(omega, attract, travel, beta)
    V = rng.uniform(0.5, 4.0, size=n) * N
    return P, N, V


def scale_to_r0(P, N, V, par, target):
    """Rescale mosquito numbers so that R0 equals target (R0^2 is linear in V)."""
    r2 = dm.r0_squared(P, N, V, par)
    return V * (target ** 2 / r2)


# ---------------------------------------------------------------------------
# Independent references
# ---------------------------------------------------------------------------

def numeric_ngm(P, N, V, par, h=1e-3):
    """van den Driessche-Watmough K = F V^-1 from finite-difference Jacobians."""
    n = len(N)
    Nt = P.T @ N

    def F(x):
        Ih, Ev, Iv = x[:n], x[n:2 * n], x[2 * n:]
        lam_h = par.a * par.b * (P @ (Iv / Nt))
        lam_v = par.a * par.c * ((P.T @ Ih) / Nt)
        return np.concatenate([lam_h * N, lam_v * V, np.zeros(n)])

    def Vf(x):
        Ih, Ev, Iv = x[:n], x[n:2 * n], x[2 * n:]
        return np.concatenate([(par.gamma + par.mu_h) * Ih, (par.nu + par.mu_v) * Ev,
                               par.mu_v * Iv - par.nu * Ev])

    m = 3 * n
    JF, JV = np.zeros((m, m)), np.zeros((m, m))
    z = np.zeros(m)
    for k in range(m):
        e = np.zeros(m)
        e[k] = h
        JF[:, k] = (F(z + e) - F(z - e)) / (2 * h)
        JV[:, k] = (Vf(z + e) - Vf(z - e)) / (2 * h)
    K = JF @ np.linalg.inv(JV)
    return float(np.max(np.abs(np.linalg.eigvals(K)))), JF, JV


def finite_diff_gradient(P, N, V, par, u, eps=1e-6):
    g = np.zeros(len(V))
    for j in range(len(V)):
        up, dn = u.copy(), u.copy()
        up[j] += eps
        dn[j] -= eps
        g[j] = (dm.r0_squared(P, N, V, par, up) - dm.r0_squared(P, N, V, par, dn)) / (2 * eps)
    return g


def slsqp_least_cost(P, N, V, par, cost, ubar, r2, rng, starts=12):
    n = len(V)
    best = math.inf
    cons = [{"type": "ineq", "fun": lambda u: r2 - dm.r0_squared(P, N, V, par, u)}]
    for s in range(starts):
        x0 = rng.uniform(0, 1, n) * ubar
        res = minimize(lambda u: float(cost @ u), x0, jac=lambda u: cost, method="SLSQP",
                       bounds=[(0, ub) for ub in ubar], constraints=cons,
                       options={"maxiter": 500, "ftol": 1e-12})
        u = np.clip(res.x, 0, ubar)
        if dm.r0_squared(P, N, V, par, u) <= r2 * (1 + 1e-9):
            best = min(best, float(cost @ u))
    return best


def grid_least_cost(P, N, V, par, cost, ubar, r2, steps=801):
    best = math.inf
    xs = np.linspace(0, ubar[0], steps)
    ys = np.linspace(0, ubar[1], steps)
    for x in xs:
        # R0^2 decreases in u_2: find the smallest feasible y by bisection on the grid
        lo, hi = 0, steps - 1
        if dm.r0_squared(P, N, V, par, np.array([x, ys[hi]])) > r2:
            continue
        while lo < hi:
            mid = (lo + hi) // 2
            if dm.r0_squared(P, N, V, par, np.array([x, ys[mid]])) <= r2:
                hi = mid
            else:
                lo = mid + 1
        best = min(best, cost[0] * x + cost[1] * ys[lo])
    return best, ubar[0] / (steps - 1) * max(cost)


# ---------------------------------------------------------------------------
# Verification suite
# ---------------------------------------------------------------------------

def run_verification(rng):
    out = {}

    # V1: analytic reproduction number against the numerical NGM ----------
    errs = []
    for _ in range(300):
        n = int(rng.integers(2, 13))
        P, N, V = random_instance(rng, n)
        par = random_params(rng)
        analytic = dm.r0(P, N, V, par)
        numeric, _, _ = numeric_ngm(P, N, V, par)
        errs.append(abs(analytic - numeric) / numeric)
    out["V1"] = {"instances": 300, "max_rel_err": float(np.max(errs)),
                 "mean_rel_err": float(np.mean(errs))}

    # V2: threshold, Jacobian sign, and simulation ------------------------
    agree, n2 = 0, 0
    for _ in range(300):
        n = int(rng.integers(2, 10))
        P, N, V = random_instance(rng, n)
        par = random_params(rng)
        V = scale_to_r0(P, N, V, par, rng.uniform(0.7, 1.3))
        r = dm.r0(P, N, V, par)
        if abs(r - 1) < 1e-6:
            continue
        _, JF, JV = numeric_ngm(P, N, V, par)
        absc = float(np.max(np.linalg.eigvals(JF - JV).real))
        n2 += 1
        agree += int((r > 1) == (absc > 0))
    sim_agree, sim_n = 0, 0
    for _ in range(40):
        n = int(rng.integers(2, 7))
        P, N, V = random_instance(rng, n)
        par = dm.Params()
        target = 0.8 if rng.random() < 0.5 else 1.25
        V = scale_to_r0(P, N, V, par, target)
        y0 = dm.disease_free_state(N, V)
        seed = int(rng.integers(0, n))
        y0[n + seed] = 1.0
        y0[seed] -= 1.0
        traj = dm.rk4(dm.rhs, y0, 0.0, 730.0, 0.25, args=(P, N, V * par.mu_v, par))
        infected = traj[:, n:2 * n].sum(axis=1)
        grew = infected.max() > 10.0
        died = infected[-1] < 1.0
        sim_n += 1
        sim_agree += int((target > 1 and grew) or (target < 1 and died))
    out["V2"] = {"jacobian_instances": n2, "jacobian_agree": agree,
                 "simulations": sim_n, "simulation_agree": sim_agree}

    # V3: Collatz-Wielandt sandwich and the heterogeneity bound ------------
    viol_up, viol_lo, viol_h, n3 = 0, 0, 0, 0
    gaps, het = [], []
    above_iso, cosner = 0, 0
    for _ in range(500):
        n = int(rng.integers(2, 21))
        P, N, V = random_instance(rng, n)
        par = random_params(rng)
        r2 = dm.r0_squared(P, N, V, par)
        R = dm.local_numbers(P, N, V, par)
        hom = dm.homogeneous_r0_squared(N, V, par)
        iso = dm.isolated_r0_squared(N, V, par)
        tol = 1e-10 * r2
        n3 += 1
        viol_up += int(r2 > R.max() + tol)
        viol_lo += int(r2 < R.min() - tol)
        viol_h += int(r2 < hom - tol)
        gaps.append((R.max() - R.min()) / r2)
        het.append(r2 / hom)
        above_iso += int(r2 > iso.max() + tol)
        cosner += int(iso.max() < 1 < r2)
    out["V3"] = {"instances": n3, "upper_violations": viol_up, "lower_violations": viol_lo,
                 "homogeneous_violations": viol_h, "spread_mean": float(np.mean(gaps)),
                 "het_ratio_mean": float(np.mean(het)), "het_ratio_max": float(np.max(het)),
                 "above_isolated": above_iso, "all_isolated_below_one_network_above": cosner}

    # V4: place shares and the gradient -----------------------------------
    share_err, grad_err, n4 = 0.0, [], 0
    for _ in range(300):
        n = int(rng.integers(2, 16))
        P, N, V = random_instance(rng, n)
        par = random_params(rng)
        u = rng.uniform(0, 0.7, n)
        lam, v, gap = dm.top_eigen(P, N, V, par, u)
        if gap < 1e-6 * lam:
            continue
        shares, _ = dm.place_shares(P, N, V, par, u)
        share_err = max(share_err, abs(shares.sum() - 1.0))
        g = dm.gradient(P, N, V, par, u)
        gfd = finite_diff_gradient(P, N, V, par, u)
        grad_err.append(float(np.max(np.abs(g - gfd)) / np.max(np.abs(gfd))))
        n4 += 1
    out["V4"] = {"instances": n4, "share_sum_max_err": share_err,
                 "grad_max_rel_err": float(np.max(grad_err)),
                 "grad_mean_rel_err": float(np.mean(grad_err))}

    # V5: convexity and monotonicity of R0^2 in the control ---------------
    conv_v, mono_v, checks = 0, 0, 0
    for _ in range(300):
        n = int(rng.integers(2, 16))
        P, N, V = random_instance(rng, n)
        par = random_params(rng)
        for _ in range(20):
            u1, u2 = rng.uniform(0, 1, n), rng.uniform(0, 1, n)
            l1, l2 = dm.r0_squared(P, N, V, par, u1), dm.r0_squared(P, N, V, par, u2)
            lm = dm.r0_squared(P, N, V, par, (u1 + u2) / 2)
            conv_v += int(lm > (l1 + l2) / 2 + 1e-12 * max(l1, l2))
            hi = np.maximum(u1, u2)
            mono_v += int(dm.r0_squared(P, N, V, par, hi) > min(l1, l2) + 1e-12 * max(l1, l2))
            checks += 1
    out["V5"] = {"checks": checks, "convexity_violations": conv_v,
                 "monotonicity_violations": mono_v}

    # V6: least-cost control against a grid (n = 2) and SLSQP (n = 3..8) ---
    grid_rows, slsqp_rows, cert_prem, cert_infeas, iters = [], [], [], 0, []
    for rep in range(120):
        n = 2 if rep < 40 else int(rng.integers(3, 9))
        P, N, V = random_instance(rng, n)
        par = random_params(rng)
        V = scale_to_r0(P, N, V, par, rng.uniform(1.1, 1.8))
        cost = rng.uniform(5, 30, n)
        ubar = np.full(n, 0.8)
        r2 = 0.95 ** 2
        res = dm.least_cost_control(P, N, V, par, cost, ubar, r2, rel_gap=1e-7)
        if res is None:
            continue
        iters.append(res["iterations"])
        ucert = dm.certificate_control(P, N, V, par, cost, ubar, r2)
        if ucert is not None:
            cert_infeas += int(dm.r0_squared(P, N, V, par, ucert) > r2 * (1 + 1e-9))
            cert_prem.append(float(cost @ ucert) / res["upper"])
        if n == 2:
            g, res_tol = grid_least_cost(P, N, V, par, cost, ubar, r2)
            grid_rows.append({"lower": res["lower"], "upper": res["upper"], "grid": g, "tol": res_tol,
                              "ok": bool(res["lower"] <= g + 1e-9 and res["upper"] <= g + 1e-9 + res_tol)})
        else:
            s = slsqp_least_cost(P, N, V, par, cost, ubar, r2, rng)
            slsqp_rows.append({"upper": res["upper"], "lower": res["lower"], "slsqp": s,
                               "ok": bool(res["upper"] <= s * (1 + 1e-6) and res["lower"] <= s * (1 + 1e-9))})
    out["V6"] = {"grid_cases": len(grid_rows), "grid_ok": sum(r["ok"] for r in grid_rows),
                 "slsqp_cases": len(slsqp_rows), "slsqp_ok": sum(r["ok"] for r in slsqp_rows),
                 "slsqp_worse_by_mean": float(np.mean([r["slsqp"] / r["upper"] - 1 for r in slsqp_rows])),
                 "slsqp_worse_by_max": float(np.max([r["slsqp"] / r["upper"] - 1 for r in slsqp_rows])),
                 "max_gap": float(max(max((r["upper"] - r["lower"]) / r["upper"] for r in grid_rows),
                                      max((r["upper"] - r["lower"]) / r["upper"] for r in slsqp_rows))),
                 "iterations_mean": float(np.mean(iters)), "iterations_max": int(np.max(iters)),
                 "certificate_cases": len(cert_prem), "certificate_infeasible": cert_infeas,
                 "certificate_premium_mean": float(np.mean(cert_prem)),
                 "certificate_premium_max": float(np.max(cert_prem))}

    # V7: residence-to-place inversion ------------------------------------
    exact_err, varah_viol, n7 = 0.0, 0, 0
    for _ in range(300):
        n = int(rng.integers(2, 21))
        P, N, V = random_instance(rng, n)
        z = rng.uniform(0, 1e-3, n)
        y = P @ z
        zh = dm.infer_places(P, y, nonneg=False)
        exact_err = max(exact_err, float(np.max(np.abs(zh - z)) / np.max(z)))
        eps = rng.normal(0, 1e-5, n)
        zp = dm.infer_places(P, y + eps, nonneg=False)
        bound = dm.varah_bound(P) * np.max(np.abs(eps))
        varah_viol += int(np.max(np.abs(zp - z)) > bound * (1 + 1e-9))
        n7 += 1
    tv_inv, tv_naive, closer, n7b = [], [], 0, 0
    for _ in range(400):
        n = int(rng.integers(4, 13))
        P, N, V = random_instance(rng, n)
        z = rng.gamma(0.6, 1.0, n)                    # infection pressure by place
        z = z * 320.0 / float(N @ (P @ z))            # about 320 cases in four weeks
        cases = rng.poisson(N * (P @ z))
        Nt = P.T @ N
        truth = z * Nt / float((z * Nt).sum())        # true share of infections by place
        zh = dm.infer_places(P, cases / N)
        est = zh * Nt
        est = est / est.sum() if est.sum() > 0 else est
        naive = cases / max(cases.sum(), 1)
        a = 0.5 * float(np.abs(est - truth).sum())
        b = 0.5 * float(np.abs(naive - truth).sum())
        tv_inv.append(a)
        tv_naive.append(b)
        closer += int(a < b)
        n7b += 1
    out["V7"] = {"exact_instances": n7, "exact_max_rel_err": exact_err, "varah_violations": varah_viol,
                 "noisy_instances": n7b, "tv_inverse_mean": float(np.mean(tv_inv)),
                 "tv_naive_mean": float(np.mean(tv_naive)), "inverse_closer": closer}

    # V8: CUSUM ------------------------------------------------------------
    configs = [(2.0, 3, 4), (2.0, 3, 6), (5.0, 7, 6), (5.0, 7, 10), (10.0, 13, 10), (10.0, 13, 16)]
    arl_rows = []
    for mu, k, h in configs:
        exact = dm.arl_markov(mu, k, h)
        runs = 20000
        lengths = np.zeros(runs)
        s = np.zeros(runs)
        alive = np.ones(runs, dtype=bool)
        t = 0
        while alive.any() and t < 200000:
            t += 1
            x = rng.poisson(mu, size=runs)
            s = np.where(alive, np.maximum(0, s + x - k), s)
            hit = alive & (s >= h)
            lengths[hit] = t
            alive &= ~hit
        mc = float(lengths.mean())
        se = float(lengths.std(ddof=1) / math.sqrt(runs))
        arl_rows.append({"mu": mu, "k": k, "h": h, "markov": exact, "mc": mc, "se": se,
                         "within_ci": bool(abs(mc - exact) <= 1.96 * se)})
    delay_viol, delay_n = 0, 0
    mono_viol = 0
    for _ in range(10000):
        k = int(rng.integers(2, 15))
        h = int(rng.integers(2, 30))
        tau = int(rng.integers(0, 30))
        delta = int(rng.integers(1, 6))
        pre = rng.poisson(k * 0.7, size=tau)
        post = k + delta + rng.poisson(1.0, size=60)
        x = np.concatenate([pre, post]).astype(float)
        _, alarm = dm.cusum(x, k, h)
        bound = tau + math.ceil(h / delta) - 1
        delay_n += 1
        delay_viol += int(alarm is None or alarm > bound)
        xp = x + rng.integers(0, 3, size=len(x))
        S1, _ = dm.cusum(x, k, h)
        S2, _ = dm.cusum(xp, k, h)
        mono_viol += int(np.any(S1 > S2 + 1e-12))
    comp = []
    for mu, k, h in configs:
        arl0 = dm.arl_markov(mu, k, h)
        c = int(poisson.ppf(1 - 1 / arl0, mu))
        while dm.threshold_arl(mu, c) < arl0:
            c += 1
        row = {"mu": mu, "k": k, "h": h, "arl0_cusum": arl0, "c": c,
               "arl0_threshold": dm.threshold_arl(mu, c)}
        for f in (1.5, 2.0):
            row["arl1_cusum_%g" % f] = dm.arl_markov(mu * f, k, h)
            row["arl1_threshold_%g" % f] = dm.threshold_arl(mu * f, c)
        comp.append(row)
    out["V8"] = {"arl": arl_rows, "delay_checks": delay_n, "delay_violations": delay_viol,
                 "monotonicity_violations": mono_viol, "comparison": comp}

    # V9: ODE solution properties and RK4 order ---------------------------
    neg, cons_err = 0.0, 0.0
    for _ in range(30):
        n = int(rng.integers(2, 7))
        P, N, V = random_instance(rng, n)
        par = dm.Params()
        V = scale_to_r0(P, N, V, par, rng.uniform(1.1, 2.0))
        y0 = dm.disease_free_state(N, V)
        y0[n] = 5.0
        y0[0] -= 5.0
        traj = dm.rk4(dm.rhs, y0, 0.0, 365.0, 0.25, args=(P, N, V * par.mu_v, par))
        neg = min(neg, float(traj.min()))
        humans = traj[:, :n] + traj[:, n:2 * n] + traj[:, 2 * n:3 * n]
        cons_err = max(cons_err, float(np.max(np.abs(humans - N[None, :]) / N[None, :])))
    P, N, V = random_instance(rng, 4)
    par = dm.Params()
    V = scale_to_r0(P, N, V, par, 1.6)
    y0 = dm.disease_free_state(N, V)
    y0[4] = 10.0
    y0[0] -= 10.0
    ref = dm.rk4(dm.rhs, y0, 0.0, 60.0, 0.0125, args=(P, N, V * par.mu_v, par))[-1]
    steps, errors = [0.8, 0.4, 0.2, 0.1], []
    for hstep in steps:
        yy = dm.rk4(dm.rhs, y0, 0.0, 60.0, hstep, args=(P, N, V * par.mu_v, par))[-1]
        errors.append(float(np.max(np.abs(yy - ref))))
    slopes = [math.log(errors[i] / errors[i + 1]) / math.log(2) for i in range(len(errors) - 1)]
    out["V9"] = {"min_state": neg, "conservation_max_rel_err": cons_err,
                 "rk4_steps": steps, "rk4_errors": errors, "rk4_slopes": slopes}
    return out


# ---------------------------------------------------------------------------
# Computational cost
# ---------------------------------------------------------------------------

def run_timing(rng):
    rows = []
    for n in (50, 100, 200, 400, 720):
        P, N, V = random_instance(rng, n)
        par = dm.Params()
        V = scale_to_r0(P, N, V, par, 1.5)
        t0 = time.perf_counter()
        r = dm.r0(P, N, V, par)
        t1 = time.perf_counter()
        dm.place_shares(P, N, V, par)
        t2 = time.perf_counter()
        cost = rng.uniform(5, 30, n)
        ubar = np.full(n, 0.8)
        dm.certificate_control(P, N, V, par, cost, ubar, 0.95 ** 2)
        t3 = time.perf_counter()
        res = dm.least_cost_control(P, N, V, par, cost, ubar, 0.95 ** 2, rel_gap=1e-6)
        t4 = time.perf_counter()
        rows.append({"n": n, "r0": r, "t_r0": t1 - t0, "t_shares": t2 - t1, "t_cert": t3 - t2,
                     "t_exact": t4 - t3, "iterations": res["iterations"],
                     "gap": (res["upper"] - res["lower"]) / res["upper"]})
    return rows


# ---------------------------------------------------------------------------
# Worked instance D1
# ---------------------------------------------------------------------------

D1_ROWS = [
    # id, description, residents, mosquitoes per resident, attractiveness, share away
    ("B1", "Poblacion: central school and public market", 4000, 5.3, 10.0, 0.20),
    ("B2", "Urban residential", 6000, 1.6, 2.0, 0.40),
    ("B3", "Peri-urban", 3500, 2.0, 1.5, 0.35),
    ("B4", "Rural upland", 2000, 2.3, 0.5, 0.25),
    ("B5", "Rural lowland (rice fields)", 1800, 1.8, 0.5, 0.30),
    ("B6", "Coastal", 2500, 1.4, 1.0, 0.30),
]
D1_POS = np.array([[0.0, 0.0], [1.5, 0.5], [3.0, -1.0], [6.0, 4.0], [-4.0, -3.0], [2.0, -5.0]])


def build_d1():
    N = np.array([r[2] for r in D1_ROWS], dtype=float)
    mhat = np.array([r[3] for r in D1_ROWS])
    attract = np.array([r[4] for r in D1_ROWS])
    omega = np.array([r[5] for r in D1_ROWS])
    dist = np.linalg.norm(D1_POS[:, None] - D1_POS[None, :], axis=2)
    travel = 4.0 + dist / 0.3
    P = dm.residence_time_matrix(omega, attract, travel, 0.06)
    V = mhat * N
    households = np.round(N / 4.1)
    cost = households / 50.0                 # team-days to treat every household once
    return P, N, V, mhat, attract, omega, travel, households, cost


def run_d1(rng):
    par = dm.Params()
    P, N, V, mhat, attract, omega, travel, households, cost = build_d1()
    Nt = dm.present_population(P, N)
    m = V / Nt
    R = dm.local_numbers(P, N, V, par)
    r2 = dm.r0_squared(P, N, V, par)
    hom = dm.homogeneous_r0_squared(N, V, par)
    iso = dm.isolated_r0_squared(N, V, par)
    shares, _ = dm.place_shares(P, N, V, par)
    grad = dm.gradient(P, N, V, par)
    M = dm.host_host_matrix(P, N, V, par)
    vals, vecs = np.linalg.eig(M)
    idx = int(np.argmax(vals.real))
    perron = np.abs(vecs[:, idx].real)
    case_share = perron / perron.sum()            # residence of cases in the growth phase
    ubar = np.full(len(N), 0.8)
    target = 0.95
    r2t = target ** 2
    strategies = {}
    uni = dm.uniform_control(P, N, V, par, 0.8, r2t)
    strategies["uniform"] = uni
    strategies["case_residence"] = dm.scaled_control(P, N, V, par, case_share, ubar, r2t)
    strategies["place_share"] = dm.scaled_control(P, N, V, par, shares, ubar, r2t)
    strategies["certificate"] = dm.certificate_control(P, N, V, par, cost, ubar, r2t)
    ex = dm.least_cost_control(P, N, V, par, cost, ubar, r2t, rel_gap=1e-6)
    strategies["exact"] = ex["u"]
    strat_rows = {}
    for name, u in strategies.items():
        strat_rows[name] = {"u": [round(float(x), 4) for x in u],
                            "cost": float(cost @ u), "r0": dm.r0(P, N, V, par, u)}
    # no movement comparison
    P0 = np.eye(len(N))
    r0_still = dm.r0(P0, N, V, par)
    # residence-to-place inversion of a synthetic week of cases: the place
    # pressure follows infectious mosquitoes per person present in the growth phase
    z = m * (P.T @ case_share) / Nt
    expected_month = 320.0                       # four weeks of reported cases
    z = z * expected_month / float(N @ (P @ z))
    expected = N * (P @ z)
    cases = rng.poisson(expected)
    rate = cases / N
    zh = dm.infer_places(P, rate)
    inversion = {"place_pressure_true": [float(x) for x in z],
                 "expected_by_residence": [float(x) for x in expected],
                 "cases_by_residence": [int(c) for c in cases],
                 "rate_by_residence": [float(x) for x in rate],
                 "place_pressure_inferred": [float(x) for x in zh],
                 "infections_by_place_true": [float(x) for x in z * Nt],
                 "infections_by_place_inferred": [float(x) for x in zh * Nt],
                 "varah": dm.varah_bound(P)}
    # seasonal scaling: required team-days for a season factor s
    season = []
    for s_fac in (0.6, 0.8, 1.0, 1.2, 1.4):
        Vs = V * s_fac
        res = dm.least_cost_control(P, N, Vs, par, cost, ubar, r2t, rel_gap=1e-6)
        season.append({"s": s_fac, "r0": dm.r0(P, N, Vs, par),
                       "cost": None if res is None else res["upper"]})
    # CUSUM against a single-week threshold at an equal yearly false-alarm rate
    weeks = np.arange(1, 53)
    mu0 = 6.0 + 5.0 * np.exp(-((weeks - 32) / 8.0) ** 2)
    k_t = 0.5 * mu0 / math.log(1.5)               # designed for a 1.5-fold rise
    sims = 20000
    ic = rng.poisson(mu0, size=(sims, 52))

    def cusum_alarm_rows(x, h):
        S = np.zeros(x.shape[0])
        first = np.full(x.shape[0], -1)
        for t in range(x.shape[1]):
            S = np.maximum(0.0, S + x[:, t] - k_t[t])
            new = (first < 0) & (S >= h)
            first[new] = t
        return first

    def thr_alarm_rows(x, zval):
        over = x > (mu0 + zval * np.sqrt(mu0))[None, :]
        first = np.where(over.any(axis=1), over.argmax(axis=1), -1)
        return first

    target_fa = 0.05
    h = None
    for cand in np.arange(2.0, 60.0, 0.25):
        if np.mean(cusum_alarm_rows(ic, cand) >= 0) <= target_fa:
            h = float(cand)
            break
    zval = None
    for cand in np.arange(1.0, 6.0, 0.01):
        if np.mean(thr_alarm_rows(ic, cand) >= 0) <= target_fa:
            zval = float(cand)
            break
    fa_c = float(np.mean(cusum_alarm_rows(ic, h) >= 0))
    fa_t = float(np.mean(thr_alarm_rows(ic, zval) >= 0))
    onset = 27
    growth = np.where(weeks >= onset, np.minimum(1.0 + 0.12 * (weeks - onset + 1), 2.8), 1.0)
    ob = rng.poisson(mu0 * growth, size=(5000, 52))
    a_c = cusum_alarm_rows(ob, h)
    a_t = thr_alarm_rows(ob, zval)

    def delays(first):
        d = first + 1 - onset          # weeks after onset week (onset week counts as 0)
        ok = first + 1 >= onset
        return d[ok], float(np.mean(~ok))

    dc, early_c = delays(a_c)
    dt, early_t = delays(a_t)
    current = rng.poisson(mu0 * growth)
    S, alarm_c = dm.cusum(current, k_t, h)
    thr = mu0 + zval * np.sqrt(mu0)
    over = np.where(current > thr)[0]
    alarm_t = int(over[0]) if len(over) else None
    cus = {"weeks": weeks.tolist(), "mu0": mu0.tolist(), "threshold": thr.tolist(),
           "current": current.tolist(), "S": S.tolist(), "onset_week": onset, "h": h, "z": zval,
           "false_alarm_year_cusum": fa_c, "false_alarm_year_threshold": fa_t,
           "delay_cusum_mean": float(np.mean(dc)), "delay_cusum_median": float(np.median(dc)),
           "delay_threshold_mean": float(np.mean(dt)), "delay_threshold_median": float(np.median(dt)),
           "missed_cusum": float(np.mean(a_c < 0)), "missed_threshold": float(np.mean(a_t < 0)),
           "early_cusum": early_c, "early_threshold": early_t, "outbreak_years": 5000,
           "alarm_cusum_week": None if alarm_c is None else int(alarm_c) + 1,
           "alarm_threshold_week": None if alarm_t is None else alarm_t + 1}
    return {
        "rows": [{"id": r[0], "desc": r[1], "residents": int(r[2]), "mhat": r[3], "attract": r[4],
                  "away": r[5], "households": int(households[i]), "cost": float(cost[i])}
                 for i, r in enumerate(D1_ROWS)],
        "P": P.round(4).tolist(), "present": Nt.tolist(), "m": m.tolist(),
        "R_local": R.tolist(), "r0": math.sqrt(r2), "r0_sq": r2,
        "hom_r0": math.sqrt(hom), "iso_r0": np.sqrt(iso).tolist(), "r0_no_movement": r0_still,
        "shares": shares.tolist(), "case_share": case_share.tolist(),
        "grad": grad.tolist(), "hotspot_per_teamday": (-grad / cost).tolist(),
        "kappa": dm.kappa(par), "target": target, "strategies": strat_rows,
        "exact_iterations": ex["iterations"], "exact_gap": (ex["upper"] - ex["lower"]) / ex["upper"],
        "inversion": inversion, "season": season, "cusum": cus,
    }


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def figures(d1):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "font.serif": ["Liberation Serif", "Times New Roman"],
                         "font.size": 10})
    ids = [r["id"] for r in d1["rows"]]
    N = np.array([r["residents"] for r in d1["rows"]])
    P = np.array(d1["P"])

    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    flows = P * N[:, None]
    for i in range(len(ids)):
        for j in range(len(ids)):
            if i != j and flows[i, j] > 60:
                ax.annotate("", xy=D1_POS[j], xytext=D1_POS[i],
                            arrowprops=dict(arrowstyle="-|>", color="#7F8C8D",
                                            lw=0.4 + flows[i, j] / 250, alpha=0.75,
                                            shrinkA=14, shrinkB=14,
                                            connectionstyle="arc3,rad=0.12"))
    sc = ax.scatter(D1_POS[:, 0], D1_POS[:, 1], s=N / 12, c=d1["m"], cmap="OrRd",
                    edgecolors="#333333", linewidths=0.8, zorder=3, vmin=0.8, vmax=3.2)
    for i, name in enumerate(ids):
        ax.annotate(name, D1_POS[i], textcoords="offset points", xytext=(-24, 10) if name == "B1" else (10, 8),
                    fontsize=10, weight="bold")
    cb = fig.colorbar(sc, ax=ax, shrink=0.85)
    cb.set_label("mosquitoes per person present, $m_j$")
    ax.set_xlabel("km")
    ax.set_ylabel("km")
    ax.set_aspect("equal")
    ax.set_xlim(-6.5, 8.5)
    ax.set_ylim(-7, 6.5)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_d1_network.png"), dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    x = np.arange(len(ids))
    w = 0.27
    ax.bar(x - w, N / N.sum(), w, label="share of residents", color="#AAB7B8")
    ax.bar(x, d1["case_share"], w, label="share of cases (by residence)", color="#E59866")
    ax.bar(x + w, d1["shares"], w, label="share of transmission (by place)", color="#A93226")
    ax.set_xticks(x, ids)
    ax.set_ylabel("share")
    ax.legend(frameon=False, fontsize=8.5)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_d1_shares.png"), dpi=220)
    plt.close(fig)

    c = d1["cusum"]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.4, 4.8), sharex=True,
                                 gridspec_kw={"height_ratios": [1.4, 1]})
    a1.plot(c["weeks"], c["mu0"], color="#7F8C8D", lw=1.2, label="expected count (baseline)")
    a1.plot(c["weeks"], c["threshold"], color="#7F8C8D", lw=1.0, ls="--",
            label="single-week threshold")
    a1.bar(c["weeks"], c["current"], color="#E59866", label="current year (synthetic)")
    if c["alarm_cusum_week"]:
        a1.axvline(c["alarm_cusum_week"], color="#A93226", lw=1.5, label="CUSUM alarm")
    if c["alarm_threshold_week"]:
        a1.axvline(c["alarm_threshold_week"], color="#1F618D", lw=1.5, ls=":",
                   label="threshold alarm")
    a1.set_ylabel("cases per week")
    a1.legend(frameon=False, fontsize=7.5, ncol=2)
    a2.plot(c["weeks"], c["S"], color="#A93226", lw=1.6)
    a2.axhline(c["h"], color="#333333", ls="--", lw=1)
    a2.set_ylabel("CUSUM S_t")
    a2.set_xlabel("morbidity week")
    for a in (a1, a2):
        a.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig_cusum.png"), dpi=220)
    plt.close(fig)


def main():
    rng = np.random.default_rng(SEED)
    t0 = time.time()
    results = {"seed": SEED}
    results["verification"] = run_verification(rng)
    print("verification done", round(time.time() - t0, 1), "s", flush=True)
    results["timing"] = run_timing(rng)
    print("timing done", round(time.time() - t0, 1), "s", flush=True)
    results["d1"] = run_d1(rng)
    print("D1 done", round(time.time() - t0, 1), "s", flush=True)
    figures(results["d1"])
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print(json.dumps(results["verification"], indent=1))


if __name__ == "__main__":
    main()

"""Assemble the dengue paper from its parts and results.json, then build DOCX and PDF.

Run:  python3 make_paper.py
"""

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CODE = os.path.join(HERE, "..", "code")
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, CODE)

import build_paper  # noqa: E402
import diagram  # noqa: E402

OUT_NAME = "Where-People-Go-Dengue-Goes_MCS-T"


def fmt(n):
    return "{:,}".format(int(round(n)))


def sci(x):
    """Small positive number as inline math, e.g. 5.3 x 10^-15."""
    if x == 0:
        return "0"
    e = int(math.floor(math.log10(abs(x))))
    m = x / 10 ** e
    return "$%.1f \\times 10^{%d}$" % (m, e)


def secs(t):
    if t < 0.01:
        return "%.4f" % t
    if t < 10:
        return "%.3f" % t
    return "%.1f" % t


def table_rows(rows):
    return "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)


def framework_figure(path):
    W, H = 2.25, 1.15
    xs = [0.15, 2.6, 5.05, 7.5]
    ys = [5.2, 3.45, 1.7]
    boxes = {
        "cen": ("Open registers", "PSA census, DepEd schools, market registers, case bulletins (App. A)", xs[0], ys[0], W, H, "blue"),
        "trv": ("Travel times", "minutes between barangay centers from the companion road model (Def. 1)", xs[1], ys[0], W, H, "blue"),
        "dst": ("Destination choice", "time away and the pull of schools, markets, and jobs (Def. 2)", xs[2], ys[0], W, H, "blue"),
        "rtm": ("Residence-time matrix", "share of biting hours spent in each place; people present (Def. 3)", xs[3], ys[0], W, H, "blue"),
        "mos": ("Mosquitoes", "survey index to mosquitoes per person present (Def. 4)", xs[0], ys[1], W, H, "orange"),
        "ode": ("Host-vector model", "infection equations by residence and place (Def. 5; Prop. 3)", xs[1], ys[1], W, H, "orange"),
        "r0": ("Reproduction number", "largest eigenvalue of a symmetric matrix; bounds (Defs. 6, 7; Props. 1, 2, 4, 5)", xs[2], ys[1], W, H, "orange"),
        "shr": ("Place shares", "hotspot ranking and gradient (Def. 8; Prop. 6)", xs[3], ys[1], W, H, "orange"),
        "ctl": ("Least-cost control", "convex program, certificate plan, certified gap (Defs. 9, 10; Alg. 1; Props. 7 to 9)", xs[0], ys[2], W, H, "green"),
        "sea": ("Seasons", "season factor and the control it needs (Def. 13; Prop. 10)", xs[1], ys[2], W, H, "green"),
        "inv": ("Places of infection", "cases by residence to infections by place (Def. 11; Alg. 2; Prop. 11)", xs[2], ys[2], W, H, "green"),
        "alm": ("Outbreak alarm", "Poisson CUSUM with proven delay and exact run length (Def. 12; Alg. 3; Prop. 12)", xs[3], ys[2], W, H, "green"),
    }
    arrows = [("cen", "trv"), ("trv", "dst"), ("dst", "rtm"), ("cen", "mos"), ("mos", "ode"),
              ("rtm", "r0"), ("ode", "r0"), ("r0", "shr"), ("shr", "alm"), ("mos", "ctl"),
              ("ctl", "sea"), ("r0", "inv")]
    diagram.draw(path, boxes, arrows, size=(10.0, 6.6), wrap=27)


def main():
    res = json.load(open(os.path.join(CODE, "results.json")))
    v = res["verification"]
    d = res["d1"]
    val = {}
    val["HEADER"] = os.path.join(ROOT, "tools", "assets", "deped_header.png")
    val["FIG_SDG"] = os.path.join(HERE, "fig_sdg.png")
    val["FIG_FRAMEWORK"] = os.path.join(HERE, "fig_framework.png")
    val["FIG_NET"] = os.path.join(CODE, "figures", "fig_d1_network.png")
    val["FIG_SHARES"] = os.path.join(CODE, "figures", "fig_d1_shares.png")
    val["FIG_CUSUM"] = os.path.join(CODE, "figures", "fig_cusum.png")
    framework_figure(val["FIG_FRAMEWORK"])
    val["KAPPA"] = "%.3f" % d["kappa"]

    # verification (Table 7)
    val["V1_N"] = fmt(v["V1"]["instances"])
    val["V1_ERR"] = sci(v["V1"]["max_rel_err"])
    assert v["V1"]["max_rel_err"] < 1e-9
    val["V2_JN"], val["V2_JA"] = fmt(v["V2"]["jacobian_instances"]), fmt(v["V2"]["jacobian_agree"])
    val["V2_SN"], val["V2_SA"] = fmt(v["V2"]["simulations"]), fmt(v["V2"]["simulation_agree"])
    assert v["V2"]["jacobian_agree"] == v["V2"]["jacobian_instances"]
    assert v["V2"]["simulation_agree"] == v["V2"]["simulations"]
    v3 = v["V3"]
    assert v3["upper_violations"] == v3["lower_violations"] == v3["homogeneous_violations"] == 0
    val["V3_N"] = fmt(v3["instances"])
    val["V3_HETMEAN"] = "%.3f" % v3["het_ratio_mean"]
    val["V3_HETMAX"] = "%.3f" % v3["het_ratio_max"]
    val["V3_ABOVE"] = fmt(v3["above_isolated"])
    val["V4_N"] = fmt(v["V4"]["instances"])
    val["V4_SHERR"] = sci(v["V4"]["share_sum_max_err"])
    val["V4_GERR"] = sci(v["V4"]["grad_max_rel_err"])
    v5 = v["V5"]
    assert v5["convexity_violations"] == v5["monotonicity_violations"] == 0
    val["V5_N"] = fmt(v5["checks"])
    v6 = v["V6"]
    assert v6["grid_ok"] == v6["grid_cases"] and v6["slsqp_ok"] == v6["slsqp_cases"]
    assert v6["certificate_infeasible"] == 0
    val["V6_GN"], val["V6_GOK"] = fmt(v6["grid_cases"]), fmt(v6["grid_ok"])
    val["V6_SN"], val["V6_SOK"] = fmt(v6["slsqp_cases"]), fmt(v6["slsqp_ok"])
    val["V6_N"] = fmt(v6["grid_cases"] + v6["slsqp_cases"])
    val["V6_GAP"] = sci(v6["max_gap"])
    val["V6_PREM"] = "%.1f" % (100 * (v6["certificate_premium_mean"] - 1))
    val["V6_PREMMAX"] = "%.1f" % (100 * (v6["certificate_premium_max"] - 1))
    v7 = v["V7"]
    assert v7["varah_violations"] == 0
    val["V7_EN"] = fmt(v7["exact_instances"])
    val["V7_ERR"] = sci(v7["exact_max_rel_err"])
    val["V7_NN"] = fmt(v7["noisy_instances"])
    val["V7_CLOSER"] = fmt(v7["inverse_closer"])
    val["V7_TVI"] = "%.3f" % v7["tv_inverse_mean"]
    val["V7_TVN"] = "%.3f" % v7["tv_naive_mean"]
    v8 = v["V8"]
    assert all(r["within_ci"] for r in v8["arl"]) and len(v8["arl"]) == 6
    assert v8["delay_violations"] == 0 and v8["monotonicity_violations"] == 0
    val["V8_DN"] = fmt(v8["delay_checks"])
    v9 = v["V9"]
    val["V9_MIN"] = "0" if v9["min_state"] == 0 else sci(v9["min_state"])
    assert v9["min_state"] >= 0
    val["V9_CONS"] = sci(v9["conservation_max_rel_err"])
    val["V9_ORDER"] = "%.2f" % (sum(v9["rk4_slopes"]) / len(v9["rk4_slopes"]))

    # timing (Table 8)
    val["TAB_TIME"] = table_rows([[fmt(r["n"]), secs(r["t_r0"]), secs(r["t_shares"]), secs(r["t_cert"]),
                                   secs(r["t_exact"]), fmt(r["iterations"]), sci(r["gap"])]
                                  for r in res["timing"]])

    # D1 tables
    ids = [r["id"] for r in d["rows"]]
    val["TAB_BRGY"] = table_rows([[r["id"], r["desc"], fmt(r["residents"]), fmt(r["households"]),
                                   "%.1f" % r["mhat"], "%.1f" % r["attract"], "%.2f" % r["away"],
                                   "%.2f" % r["cost"]] for r in d["rows"]])
    val["TAB_P"] = table_rows([[ids[i]] + ["%.3f" % x for x in row] for i, row in enumerate(d["P"])])
    trows = []
    for i, b in enumerate(ids):
        trows.append([b, fmt(d["present"][i]), "%.2f" % d["m"][i], "%.3f" % d["R_local"][i],
                      "%.3f" % d["iso_r0"][i], "%.1f" % (100 * d["case_share"][i]),
                      "%.1f" % (100 * d["shares"][i]), "%.1f" % (1000 * d["hotspot_per_teamday"][i])])
    val["TAB_TRANS"] = table_rows(trows)
    val["D1_R0"] = "%.3f" % d["r0"]
    val["D1_R0SQ"] = "%.3f" % d["r0_sq"]
    val["D1_RMIN"] = "%.3f" % min(d["R_local"])
    val["D1_RMAX"] = "%.3f" % max(d["R_local"])
    assert min(d["R_local"]) <= d["r0_sq"] <= max(d["R_local"])
    val["D1_R0HOM"] = "%.3f" % d["hom_r0"]
    b2 = ids.index("B2")
    b1 = ids.index("B1")
    assert max(range(6), key=lambda i: d["case_share"][i]) == b2
    assert max(range(6), key=lambda i: d["shares"][i]) == b1
    val["D1_CASE_B2"] = "%.1f" % (100 * d["case_share"][b2])
    val["D1_SHARE_B1"] = "%.1f" % (100 * d["shares"][b1])
    val["D1_ISO_B1"] = "%.3f" % d["iso_r0"][b1]
    assert max(range(6), key=lambda i: d["iso_r0"][i]) == b1
    val["D1_TARGET"] = "%.2f" % d["target"]

    st = d["strategies"]
    names = [("uniform", "Uniform"), ("case_residence", "Where cases live"), ("place_share", "Place shares"),
             ("certificate", "Certificate (linear program)"), ("exact", "Least cost (Algorithm 1)")]
    val["TAB_STRAT"] = table_rows([[label] + ["%.1f" % (100 * x) for x in st[k]["u"]] +
                                   ["%.2f" % st[k]["cost"], "%.3f" % st[k]["r0"]] for k, label in names])
    ce = st["exact"]["cost"]
    val["D1_COST_EXACT"] = "%.2f" % ce
    val["D1_SAVE_UNI"] = "%.0f" % (100 * (1 - ce / st["uniform"]["cost"]))
    val["D1_SAVE_RES"] = "%.0f" % (100 * (1 - ce / st["case_residence"]["cost"]))
    val["D1_LOWER"] = "%.4f" % (ce * (1 - d["exact_gap"]))
    val["D1_CERT_PREM"] = "%.1f" % (100 * (st["certificate"]["cost"] / ce - 1))
    val["D1_CERT_R0"] = "%.3f" % st["certificate"]["r0"]
    assert st["case_residence"]["cost"] == max(st[k]["cost"] for k, _ in names)
    assert st["exact"]["u"][b2] == 0.0

    val["TAB_SEASON"] = table_rows([["%.1f" % r["s"], "%.3f" % r["r0"], "%.2f" % r["cost"]] for r in d["season"]])
    val["D1_SFAC_THRESH"] = "%.2f" % (1.0 / d["r0_sq"])

    inv = d["inversion"]
    val["TAB_INV"] = table_rows([[b, fmt(inv["cases_by_residence"][i]), "%.1f" % inv["infections_by_place_true"][i],
                                  "%.1f" % inv["infections_by_place_inferred"][i]] for i, b in enumerate(ids)])
    val["D1_VARAH"] = "%g" % round(inv["varah"], 6)

    c = d["cusum"]
    val["D1_H"] = "%g" % c["h"]
    val["D1_FA_C"] = "%.3f" % c["false_alarm_year_cusum"]
    val["D1_FA_T"] = "%.3f" % c["false_alarm_year_threshold"]
    val["D1_Z"] = "%.2f" % c["z"]
    val["D1_ONSET"] = fmt(c["onset_week"])
    val["D1_DELAY_C"] = "%.2f" % c["delay_cusum_mean"]
    val["D1_DELAY_T"] = "%.2f" % c["delay_threshold_mean"]
    val["D1_MED_C"] = "%g" % c["delay_cusum_median"]
    val["D1_MED_T"] = "%g" % c["delay_threshold_median"]
    assert c["missed_cusum"] == 0 and c["missed_threshold"] == 0
    val["D1_ALARM_C"] = fmt(c["alarm_cusum_week"])
    val["D1_ALARM_T"] = fmt(c["alarm_threshold_week"])
    val["D1_CUSUM_GAIN"] = "%.1f" % (c["delay_threshold_mean"] - c["delay_cusum_mean"])
    val["D1_DELAYBOUND"] = fmt(math.ceil(c["h"] / 2.0))

    arows = []
    for r in v8["comparison"]:
        assert r["arl0_threshold"] >= r["arl0_cusum"]
        arows.append(["%g" % r["mu"], "%d, %d" % (r["k"], r["h"]), "%.1f" % r["arl0_cusum"],
                      "%.1f" % r["arl0_threshold"], "%.1f" % r["arl1_cusum_1.5"], "%.1f" % r["arl1_threshold_1.5"],
                      "%.1f" % r["arl1_cusum_2"], "%.1f" % r["arl1_threshold_2"]])
    val["TAB_ARL"] = table_rows(arows)
    ex = [r for r in v8["comparison"] if r["mu"] == 5.0 and r["h"] == 10][0]
    val["D1_ARL_EX_C"] = "%.1f" % ex["arl1_cusum_1.5"]
    val["D1_ARL_EX_T"] = "%.1f" % ex["arl1_threshold_1.5"]

    parts = ["part1_front_intro.md", "part2_framework.md", "part3_findings.md", "part4_conclusions.md"]
    md = "\n\n".join(open(os.path.join(HERE, p), encoding="utf-8").read() for p in parts)
    missing = set()

    def rep(m):
        k = m.group(1)
        if k not in val:
            missing.add(k)
            return m.group(0)
        return str(val[k])

    md = re.sub(r"<<([A-Z0-9_]+)>>", rep, md)
    if missing:
        raise SystemExit("missing values: %s" % sorted(missing))
    toc = []
    for line in md.splitlines():
        m = re.match(r"^(#{1,3}) (.+)$", line)
        if m:
            toc.append([len(m.group(1)), m.group(2).strip()])
    out_md = os.path.join(HERE, "paper.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    toc_path = os.path.join(HERE, "toc.json")
    json.dump(toc, open(toc_path, "w"), indent=0)
    docx, pdf = build_paper.build(out_md, os.path.join(HERE, OUT_NAME), toc_path, HERE)
    print(docx)
    print(pdf)


if __name__ == "__main__":
    main()

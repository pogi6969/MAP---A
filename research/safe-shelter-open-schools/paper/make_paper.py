"""Assemble the evacuation paper from its parts and results.json, then build DOCX and PDF.

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
import evacmodel as em  # noqa: E402
import verify_evacuation as ve  # noqa: E402

OUT_NAME = "Safe-Shelter-Open-Schools_MCS-T"


def fmt(n):
    return "{:,}".format(int(n))


def f2(x):
    return "%.2f" % x


def table_rows(rows):
    return "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)


def framework_figure(path):
    W, H = 2.25, 1.15
    xs = [0.15, 2.6, 5.05, 7.5]
    ys = [5.2, 3.45, 1.7]
    boxes = {
        "reg": ("Open registers", "PSA census, DepEd schools, LGU evacuation centers, PHIVOLCS hazard maps, OpenStreetMap (App. A)", xs[0], ys[0], W, H, "blue"),
        "scen": ("Hazard scenario", "active danger zones and closed bridges (Def. 1)", xs[1], ys[0], W, H, "blue"),
        "orig": ("Origins", "evacuees and vulnerable residents per barangay (Def. 2)", xs[2], ys[0], W, H, "blue"),
        "road": ("Road network", "travel times and capacities per minute (Def. 3)", xs[3], ys[0], W, H, "blue"),
        "shel": ("Shelters", "Sphere capacity; non-school, open space, classrooms (Defs. 4, 5)", xs[0], ys[1], W, H, "blue"),
        "suit": ("Suitability", "reach within the trip limit, safety, accessibility (Def. 6)", xs[1], ys[1], W, H, "blue"),
        "plan": ("School-preserving plan", "lexicographic min-cost flow (Defs. 7, 8; Alg. 1; Props. 1 to 3)", xs[2], ys[1], W, H, "orange"),
        "room": ("Classrooms and learners", "classrooms closed, learners displaced (Def. 9; Props. 4, 5)", xs[3], ys[1], W, H, "orange"),
        "tex": ("Time-expanded network", "one copy of the roads per minute (Def. 10)", xs[0], ys[2], W, H, "green"),
        "clr": ("Clearance time", "bisection and lower bound (Def. 11; Alg. 2; Props. 6 to 8)", xs[1], ys[2], W, H, "green"),
        "brg": ("Bridge closures", "single bridges and whole lahar channels (Def. 12; Prop. 9)", xs[2], ys[2], W, H, "green"),
        "lpc": ("Ligtas Pinoy Centers", "greedy siting with a 63.2% guarantee (Defs. 13, 14; Alg. 3; Prop. 10)", xs[3], ys[2], W, H, "green"),
    }
    arrows = [("reg", "scen"), ("scen", "orig"), ("orig", "road"), ("reg", "shel"), ("shel", "suit"),
              ("road", "suit"), ("suit", "plan"), ("plan", "room"), ("plan", "tex"), ("tex", "clr"),
              ("clr", "brg"), ("room", "lpc")]
    diagram.draw(path, boxes, arrows, size=(10.0, 6.6), wrap=27)


def main():
    res = json.load(open(os.path.join(CODE, "results.json")))
    v = res["verification"]
    e = res["e1"]
    sc = e["scenarios"]
    val = {}
    val["HEADER"] = os.path.join(ROOT, "tools", "assets", "deped_header.png")
    val["FIG_SDG"] = os.path.join(HERE, "fig_sdg.png")
    val["FIG_FRAMEWORK"] = os.path.join(HERE, "fig_framework.png")
    val["FIG_MAP"] = os.path.join(CODE, "figures", "fig_e1_map.png")
    val["FIG_ARR"] = os.path.join(CODE, "figures", "fig_e1_arrivals.png")
    framework_figure(val["FIG_FRAMEWORK"])

    # verification
    val["V1_N"] = fmt(v["V1"]["instances"])
    val["V1_LEVELS"] = fmt(v["V1"]["levels"])
    assert v["V1"]["agree"] == v["V1"]["instances"] and v["V1"]["nonintegral"] == 0
    val["V2_N"] = fmt(v["V2"]["cases"])
    val["V2_EXACT"] = fmt(v["V2"]["exact"])
    val["V2_G1"] = fmt(v["V2"]["gap_hist"].get("1", 0))
    val["V2_G2"] = fmt(v["V2"]["gap_hist"].get("2", 0))
    val["V2_MMAX"] = fmt(v["V2"]["schools_used_max"])
    val["V2_GAPCASES"] = fmt(v["V2"]["cases"] - v["V2"]["exact"])
    assert v["V2"]["violations"] == 0
    val["V3_N"] = fmt(v["V3"]["pairs"])
    val["V3_NZ"] = fmt(v["V3"]["nonzero"])
    assert v["V3"]["agree"] == v["V3"]["pairs"]
    val["V4_N"] = fmt(v["V4"]["instances"])
    val["V4_LBMEAN"] = "%.3f" % v["V4"]["lb_ratio_mean"]
    val["V4_LBMIN"] = "%.3f" % v["V4"]["lb_ratio_min"]
    val["V4_BIS"] = "%.1f" % v["V4"]["bisection_calls_mean"]
    val["V4_SCAN"] = "%.1f" % v["V4"]["scan_calls_mean"]
    assert v["V4"]["agree"] == v["V4"]["instances"] and v["V4"]["lb_violations"] == 0
    c5, x5 = v["V5"]["checks"], v["V5"]["violations"]
    assert sum(x5.values()) == 0
    val["V5_CT"], val["V5_CR"], val["V5_AR"], val["V5_AT"], val["V5_AL"] = (
        fmt(c5["closure_time"]), fmt(c5["closure_rooms"]), fmt(c5["add_rooms"]), fmt(c5["add_time"]),
        fmt(c5["alert"]))
    val["V5_TOTAL"] = fmt(sum(c5.values()))
    assert v["V6"]["violations_total"] == 0
    val["V6_N"] = fmt(v["V6"]["checks_total"])
    val["V7_MIN"] = "%.3f" % v["V7"]["ratio_min"]
    val["V7_MEAN"] = "%.3f" % v["V7"]["ratio_mean"]
    val["V7_N"] = fmt(v["V7"]["instances"])
    val["V7_OPT"] = fmt(round(v["V7"]["share_optimal"] * v["V7"]["instances"]))
    val["V7_MIN_PCT"] = "%.1f" % (100 * v["V7"]["ratio_min"])
    val["V7_OPT_PCT"] = "%.1f" % (100 * v["V7"]["share_optimal"])

    # timing tables
    val["TAB_PLAN"] = table_rows([[fmt(r["nodes"]), fmt(r["origins"]), fmt(r["shelters"]), fmt(r["arcs"]),
                                   fmt(r["demand"]), "%.3f" % r["seconds"]] for r in res["timing"]["plan"]])
    val["TAB_EXP"] = table_rows([[fmt(r["horizon"]), fmt(r["vertices"]), fmt(r["arcs"]), "%.3f" % r["seconds"]]
                                 for r in res["timing"]["expanded"]])

    # E1 tables
    zone_name = {"PDZ": "Permanent Danger Zone", "EDZ": "Extended Danger Zone", "LAHAR": "Lahar area"}
    val["TAB_ORIG"] = table_rows([[o["id"], zone_name[o["zone"]], "%.1f" % o["dist_km"], fmt(o["pop"]),
                                   fmt(o["vul"]), "%s, %d" % (o["nearest"], o["nearest_min"])]
                                  for o in e["origins"]])
    kind = {"ec": "Non-school", "school": "School"}
    srows = []
    for s in e["shelters"]:
        srows.append([s["id"] + " (" + s["name"].lower() + ")", kind[s["kind"]], fmt(s["area"]) if s["area"] else "–",
                      fmt(s["cap_ec"]) if s["cap_ec"] else "–", fmt(s["cap_open"]) if s["cap_open"] else "–",
                      fmt(s["rooms"]) if s["rooms"] else "–", fmt(s["room_cap"]) if s["room_cap"] else "–",
                      "yes" if s["accessible"] else "no",
                      fmt(s["learners_per_room"]) if s["learners_per_room"] else "–"])
    val["TAB_SHEL"] = table_rows(srows)
    cap0 = sum(s["cap_ec"] for s in e["shelters"])
    cap1 = sum(s["cap_open"] for s in e["shelters"])
    cap2 = sum(s["room_cap"] for s in e["shelters"])
    rooms = sum(s["rooms"] for s in e["shelters"])
    val["E1_CAP0"], val["E1_CAP1"], val["E1_CAP2"], val["E1_CAPT"] = fmt(cap0), fmt(cap1), fmt(cap2), fmt(cap0 + cap1 + cap2)
    val["E1_ROOMS"] = fmt(rooms)
    names = {"AL3": "Alert Level 3", "AL4": "Alert Level 4", "AL4+L": "Compound (AL4 + lahar)"}
    prow = []
    for key in ("AL3", "AL4", "AL4+L"):
        x = sc[key]
        for pol, pname in (("blind", "time-only"), ("lex", "school-preserving")):
            p = x[pol]
            prow.append(["%s, %s" % (names[key], pname), fmt(x["demand"]), fmt(p["placed"]), fmt(p["persons_ec"]),
                         fmt(p["persons_open"]), fmt(p["persons_room"]), fmt(p["rooms_closed_total"]),
                         fmt(p["learners_displaced"]), f2(p["mean_time"])])
    val["TAB_PLANS"] = table_rows(prow)
    a3 = sc["AL3"]
    val["E1_D_AL3"] = fmt(a3["demand"])
    val["E1_V_AL3"] = fmt(a3["vulnerable"])
    val["E1_OVER_AL3"] = fmt(a3["nearest_overflow"])
    val["E1_OVER_AL4"] = fmt(sc["AL4"]["nearest_overflow"])
    val["E1_OVER_AL4L"] = fmt(sc["AL4+L"]["nearest_overflow"])
    val["E1_ROOMS_LEX"] = fmt(a3["lex"]["rooms_closed_total"])
    val["E1_ROOMS_BLIND"] = fmt(a3["blind"]["rooms_closed_total"])
    val["E1_LEARN_LEX"] = fmt(a3["lex"]["learners_displaced"])
    val["E1_LEARN_BLIND"] = fmt(a3["blind"]["learners_displaced"])
    saved = a3["blind"]["learners_displaced"] - a3["lex"]["learners_displaced"]
    val["E1_LEARN_SAVED"] = fmt(saved)
    val["E1_LD_SAVED"] = fmt(saved * 15)
    val["E1_CD_SAVED"] = fmt((a3["blind"]["rooms_closed_total"] - a3["lex"]["rooms_closed_total"]) * 15)
    val["E1_EXTRA_MIN"] = f2(a3["lex"]["mean_time"] - a3["blind"]["mean_time"])
    val["E1_ROOM_PERSONS_LEX"] = fmt(a3["lex"]["persons_room"])
    val["E1_UTIL_AL4"] = "%d" % round(100 * sc["AL4"]["demand"] / (cap0 + cap1 + cap2))
    order = {"non-school": 0, "school open space": 1, "classroom": 2}
    arows = sorted(a3["assignment"], key=lambda r: (r["origin"], order[r["space"]], r["shelter"]))
    val["TAB_ASSIGN"] = table_rows([[r["origin"], r["shelter"], r["space"], fmt(r["persons"])] for r in arows])

    crow = []
    for key in ("AL3", "AL4", "AL4+L"):
        x = sc[key]
        crow.append([names[key], fmt(x["lex"]["placed"]), fmt(x["clearance_lex"]), fmt(x["clearance_lb"]),
                     "%.2f" % (x["clearance_lb"] / x["clearance_lex"])])
    val["TAB_CLEAR"] = table_rows(crow)
    val["E1_T_AL3"] = fmt(sc["AL3"]["clearance_lex"])
    val["E1_T_AL4"] = fmt(sc["AL4"]["clearance_lex"])

    # which movement sets the clearance time at AL4
    inst, pos = ve.build_e1()
    al4 = em.Scenario("AL4", {"PDZ", "EDZ"})
    plan4 = em.lex_plan(inst, al4, "lex")

    def subset_clear(ids):
        sup, caps = {}, {}
        for (a, k, cls), f in plan4["x"].items():
            if inst.origins[a]["id"] in ids:
                node = inst.origins[a]["node"]
                sup[node] = sup.get(node, 0) + f
                snode = inst.shelters[plan4["slots"][k][0]]["node"]
                caps[snode] = caps.get(snode, 0) + f
        return em.clearance_time(inst, al4, sup, caps)[0]

    t_pdz = subset_clear({"O1", "O2", "O3"})
    t_edz = subset_clear({"O4", "O5"})
    t_all = sc["AL4"]["clearance_lex"]
    if t_all == sc["AL3"]["clearance_lex"]:
        val["E1_AL4_SENTENCE"] = (
            "Adding the Extended Danger Zone does not lengthen the evacuation in E1: under the Alert Level 4 plan "
            "the residents of the Permanent Danger Zone alone need %d minutes and those of the Extended Danger Zone "
            "alone %d minutes, and moving both groups together still takes %d." % (t_pdz, t_edz, t_all))
    else:
        val["E1_AL4_SENTENCE"] = (
            "Adding the Extended Danger Zone lengthens the evacuation to %d minutes; under the Alert Level 4 plan "
            "the Permanent Danger Zone alone needs %d minutes and the Extended Danger Zone alone %d." % (t_all, t_pdz, t_edz))

    closures = e["channel_closures"]
    label = {"none": "None", "A": "Channel A (A1 to A4)", "B": "Channel B (B1 to B3)", "A+B": "Both channels (all seven)"}

    def tfmt(t):
        return "never finishes" if (t is None or (isinstance(t, float) and math.isinf(t)) or t == "Infinity") else fmt(t)

    rowsc = []
    for key in ("none", "A", "B", "A+B"):
        c = closures[key]
        rowsc.append([label[key], tfmt(c["clearance_fixed_plan"]), fmt(c["unplaced"]), fmt(c["rooms_closed"]),
                      tfmt(c["clearance_new_plan"]), f2(c["mean_time"])])
    val["TAB_CLOSE"] = table_rows(rowsc)
    val["E1_DELTA_A"] = fmt(closures["A"]["clearance_fixed_plan"] - closures["none"]["clearance_fixed_plan"])
    val["E1_DELTA_B"] = fmt(closures["B"]["clearance_fixed_plan"] - closures["none"]["clearance_fixed_plan"])
    val["E1_TRAPPED"] = fmt(closures["A+B"]["unplaced"])
    assert closures["A+B"]["unplaced"] == sc["AL4+L"]["lex"]["unplaced"]

    s = e["siting"]
    val["E1_D_AL4L"] = fmt(sc["AL4+L"]["demand"])
    val["E1_PHI0"] = fmt(s["phi0"])
    town = {"TS": "south town", "TSW": "southwest town", "TNE": "northeast town", "TE": "east town",
            "TSE": "southeast city"}
    gains = sorted(s["single_gains"].items(), key=lambda kv: -kv[1])
    val["E1_SINGLE"] = ", ".join("%s %s" % (fmt(g), town[k]) for k, g in gains[:-1]) + \
        ", and %s for the %s" % (fmt(gains[-1][1]), town[gains[-1][0]])
    val["E1_SINGLE"] = ", ".join("%s (%s)" % (fmt(g), town[k]) for k, g in gains)
    srow = [["0", "–", "0", "–", "0", fmt(sc["AL4+L"]["lex"]["unplaced"]), fmt(sc["AL4+L"]["lex"]["persons_room"]),
             fmt(sc["AL4+L"]["lex"]["rooms_closed_total"]), fmt(sc["AL4+L"]["lex"]["learners_displaced"]),
             fmt(sc["AL4+L"]["clearance_lex"])]]
    for r in s["rows"]:
        srow.append([fmt(r["k"]), ", ".join(r["sites"]), fmt(r["gain"]),
                     ", ".join(r["best_sites"]), fmt(r["best_gain"]), fmt(r["unplaced"]),
                     fmt(r["persons_room"]), fmt(r["rooms_closed"]), fmt(r["learners"]), fmt(r["clearance"])])
        assert r["gain"] == r["best_gain"]
    val["TAB_SITE"] = table_rows(srow)
    rows = s["rows"]
    val["E1_POCKET_SAVED"] = fmt(sc["AL4+L"]["lex"]["unplaced"] - rows[0]["unplaced"])
    val["E1_SIT_ROOM0"] = fmt(rows[0]["persons_room"])
    val["E1_SIT_ROOM2"] = fmt(rows[1]["persons_room"])
    val["E1_SIT_ROOM3"] = fmt(rows[2]["persons_room"])
    val["E1_SIT_K0_ROOMS"] = fmt(rows[0]["rooms_closed"])
    val["E1_SIT_K2_ROOMS"] = fmt(rows[1]["rooms_closed"])
    val["E1_SIT_K3_ROOMS"] = fmt(rows[2]["rooms_closed"])

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

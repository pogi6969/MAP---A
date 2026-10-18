"""LIGTA-S rationale video (version without narration) and its timeline.

Run:  python3 make_video.py            -> ../LIGTA-S_Rationale_Video_v1_MCS_No_Narration.mp4
      python3 make_video.py --preview  -> a few still frames for checking
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(PROJ, ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import rationale_parts as P  # noqa: E402
import rationale_video as V  # noqa: E402
from PIL import Image  # noqa: E402

BRAND = "LIGTA-S"
OUT = os.path.join(PROJ, "video")
NAME = "LIGTA-S_Rationale_Video_v1_MCS_No_Narration.mp4"
RES = json.load(open(os.path.join(PROJ, "code", "results.json")))
E1 = RES["e1"]
VER = RES["verification"]
AL3 = E1["scenarios"]["AL3"]

SCENES = [
    {"name": "Family", "bar": "Safety", "cues": [
        {"id": "1.1", "text": "January 2026. Mayon rises to Alert Level 3.",
         "onscreen": "Mayon smokes on the right; a house and a family of four on the left; the badge \"ALERT LEVEL 3\" drops in under \"January 2026\"."},
        {"id": "1.2", "text": "A family in the danger zone packs one bag and asks one question.",
         "onscreen": "A packed bag appears beside the family; a dotted path leaves the house toward the lowlands."},
        {"id": "1.3", "text": "Where do we go, and will there be room for Lola?",
         "onscreen": "Speech bubble \"Where do we go?\", then \"Room for Lola?\" over the grandmother with a cane."},
        {"id": "1.4", "text": "The nearest shelter is a school, and it is already full.",
         "onscreen": "A school at the end of the path fills window by window; a red stamp \"FULL\" lands on it."},
    ]},
    {"name": "Community", "bar": "Learning", "cues": [
        {"id": "2.1", "text": "Zoom out to the whole province.",
         "onscreen": "Albay as a field of 720 barangay dots in 18 towns; the danger zone glows around Mayon."},
        {"id": "2.2", "text": "In January, four schools turned into evacuation centers, and 3,424 learners were affected.",
         "onscreen": "Card: \"4 schools became evacuation centers · 3,424 learners affected\" (counter), source line Philippine Daily Inquirer, 2026."},
        {"id": "2.3", "text": "By May, 34 classrooms in Camalig were sheltering about 1,315 people.",
         "onscreen": "A grid of 34 classroom tiles fills; \"34 classrooms · 488 families · about 1,315 people\", source Daily Tribune, 2026."},
        {"id": "2.4", "text": "Sustainable Development Goal 4 asks for safe places to learn. Goal 11 asks us to protect people from disasters.",
         "onscreen": "Chips slide in: \"SDG 4.a · safe places to learn\" and \"SDG 11.5 · protect people from disasters\"."},
        {"id": "2.5", "text": "In Albay, both goals meet in the same classroom.",
         "onscreen": "Both chips glide to the centre and meet over one classroom; RA 10821: \"schools are a last resort\" appears below."},
    ]},
    {"name": "Stakes", "bar": "Time", "cues": [
        {"id": "3.1", "text": "Then the alert rises, and minutes start to matter.",
         "onscreen": "Badge changes to \"ALERT LEVEL 4\"; a clock counts minutes."},
        {"id": "3.2", "text": "Heavy rain sends lahar down the river channels and closes the bridges.",
         "onscreen": "Two brown lahar channels cut across the road ring; bridges A1 to A4 and B1 to B3 turn red with a cross."},
        {"id": "3.3", "text": "Send everyone to the nearest site, and families arrive at shelters that are already full.",
         "onscreen": "Arrows from every barangay to its nearest shelter; overflow counter \"298 arrive at full shelters\" (test network)."},
        {"id": "3.4", "text": "So how do we shelter everyone, the vulnerable first, while keeping the most classrooms open?",
         "onscreen": "Three lines build: \"Everyone sheltered · Vulnerable first · Classrooms last\" with a question mark."},
    ]},
    {"name": "How MCS comes into play", "bar": "MCS", "cues": [
        {"id": "4.1", "text": "This is where MCS comes into play.",
         "onscreen": "The letters M, C and S drop in, then unfold into Mathematical, Computational, Sciences."},
        {"id": "4.2", "text": "Mathematics turns open data into a road graph, with travel times, capacities, and shelters in three tiers.",
         "onscreen": "Chain lights \"Open data → Graph\"; panel MATHEMATICS: test network E1 draws in; G = (N, E), τ_e, u_e; tiers: non-school, school open space, classrooms (18 per room)."},
        {"id": "4.3", "text": "The law's order becomes one lexicographic minimum-cost flow: vulnerable first, then everyone, then classrooms last.",
         "onscreen": "Lexicographic objective and the penalties M_O and M_Y; evacuee flows animate from O1 to O3 into their shelters (Alert Level 3 plan)."},
        {"id": "4.4", "text": "Computing solves it exactly in seconds, and a time-expanded network gives the exact clearance time.",
         "onscreen": "Chain lights \"Algorithm → Numbers\"; panel COMPUTING: copies of the road network per minute; arrival curve F(T) climbs to 1,560; T* = 53 min, lower bound 34."},
        {"id": "4.5", "text": "Optimisation sites new Ligtas Pinoy Centers, and the greedy rule is guaranteed at least sixty-three percent of the best.",
         "onscreen": "Chain lights \"Optimisation\"; panel OPTIMISATION: f(S_g) ≥ (1 − 1/e) f(S*) ≈ 0.632 f(S*); the south town lights inside the lahar pocket: 400 of 450 sheltered."},
        {"id": "4.6", "text": "On the test network, the plan closes fourteen classrooms instead of forty, for under two minutes more travel.",
         "onscreen": "Counters: classrooms closed 40 → 14; learners displaced 1,702 → 532; extra mean trip +1.70 min. Label \"test network E1 (synthetic)\"."},
        {"id": "4.7", "text": "Ten results, proven, then verified against independent code.",
         "onscreen": "Chain lights \"Proof\"; ten proof squares turn into green checks; 300/300 plans, 660/660 networks, 4,796 checks, 0 violations."},
        {"id": "4.8", "text": "LIGTA-S will not build one more shelter.", "pause": 0.6,
         "onscreen": "Boom. Screen darkens; the line appears in white."},
        {"id": "4.9", "text": "But when the alert rises, it will tell every family where to go, and keep the most classrooms open.",
         "onscreen": "The line appears in gold."},
        {"id": "4.10", "text": "[pause] Distance tells you where the shelter is. A plan tells you if there is room, in time.",
         "pause": 0.8, "hold": 1.0,
         "onscreen": "Two lines: \"Distance tells you where the shelter is.\" (white), then \"A plan tells you if there is room, in time.\" (gold)."},
    ]},
]

TITLE_LINES = ["Safe Shelter, Open Schools: A Verified Network-Flow Model",
               "for Planning Evacuations in Albay by Hazard Zone, Shelter Capacity,",
               "and Vulnerability While Keeping Classrooms Open"]

CHAIN = ["Open data", "Graph", "Algorithm", "Numbers", "Optimisation", "Proof"]


class Spec:
    def __init__(self):
        self.scenes, end = V.layout(SCENES)
        self.title_start = end
        self.title = V.TitleCard(BRAND, TITLE_LINES, {
            "building": os.path.join(ROOT, "tools", "assets", "school_building.png"),
            "seal": os.path.join(ROOT, "tools", "assets", "legasci_seal.png")})
        self.total = end + self.title.dur
        self.base = V.make_background()
        self.cue = {c["id"]: c for sc in self.scenes for c in sc["cues"]}
        self.mcs_start = self.cue["4.1"]["start"]
        self.boom_t = self.cue["4.8"]["start"] - 0.25
        eqdir = os.path.join(HERE, "eq")
        os.makedirs(eqdir, exist_ok=True)
        tex = {
            "graph": r"G=(N,E),\quad \tau_e\ \text{min},\quad u_e\ \text{persons/min}",
            "tiers": r"\text{cap}_s=\Big\lfloor \tfrac{F_s}{3.5\,\text{m}^2}\Big\rfloor,\qquad K_s=\Big\lceil \tfrac{y_s}{18}\Big\rceil",
            "lex": r"\max V\ \succ\ \max D\ \succ\ \min Y\ \succ\ \min O\ \succ\ \min \textstyle\sum_e \tau_e x_e",
            "pen": r"M_O = D\,T_{\max}+1,\qquad M_Y = D\,(M_O+T_{\max})+1",
            "tstar": r"T^{*}=\min\{\,T : F(T)=D\,\},\qquad T^{*}\ \ge\ \tau_{\min}-1+\Big\lceil \tfrac{D}{c}\Big\rceil",
            "greedy": r"f(S_g)\ \ge\ \Big(1-\tfrac{1}{e}\Big)\,f(S^{*})\ \approx\ 0.632\,f(S^{*})",
        }
        self.eq = {k: V.latex_png(v, os.path.join(eqdir, k + ".png")) for k, v in tex.items()}
        self.eqs = {k: V.scaled(im, height=None, width=None) if False else im for k, im in self.eq.items()}
        # network geometry for E1
        self.pos = E1["pos"]
        self.arcs = [(a[0], a[1], a[4]) for a in E1["arcs"]]
        self.snode = {"EC1": "TE", "EC2": "TSE", "EC3": "TSW", "SCH1": "TS", "SCH2": "TSE", "SCH3": "TNE"}

    # helpers ---------------------------------------------------------------
    def eqimg(self, key, height, maxw=780):
        im = V.scaled(self.eq[key], height=height)
        if im.size[0] > maxw:
            im = V.scaled(self.eq[key], width=maxw)
        return im

    def net_xy(self, node, box):
        x0, y0, x1, y1 = box
        x, y = self.pos[node]
        s = min(x1 - x0, y1 - y0) / 27.0
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        return cx + x * s, cy - y * s

    def draw_net(self, cv, box, a, reveal=1.0, closed=(), show_labels=True):
        seen = set()
        n = len(self.arcs)
        for i, (u, v, tag) in enumerate(self.arcs):
            if (v, u) in seen or i / n > reveal:
                continue
            seen.add((u, v))
            p, q = self.net_xy(u, box), self.net_xy(v, box)
            bridge = tag[:1] in ("A", "B") and len(tag) == 2
            col = (200, 190, 190)
            if bridge:
                col = V.RED if tag in closed else (230, 200, 120)
            cv.line([p, q], col, a * 0.8, 6 if bridge else 4)
            if bridge and tag in closed:
                mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
                cv.line([(mx - 12, my - 12), (mx + 12, my + 12)], V.RED, a, 5)
                cv.line([(mx - 12, my + 12), (mx + 12, my - 12)], V.RED, a, 5)
        sx, sy = self.net_xy("R0", box)
        cx = (sx + self.net_xy("R6", box)[0]) / 2
        cy = self.net_xy("R3", box)[1] + (self.net_xy("R9", box)[1] - self.net_xy("R3", box)[1]) / 2
        r6 = abs(self.net_xy("R0", box)[0] - cx) * 0.75
        cv.circle((cx, cy), r6, (255, 90, 60), a * 0.10)
        cv.poly([(cx - 18, cy + 14), (cx, cy - 18), (cx + 18, cy + 14)], (90, 60, 60), a)
        for o in E1["origins"]:
            x, y = self.net_xy(o["id"], box)
            cv.circle((x, y), 11, V.RED, a)
            if show_labels:
                cv.text((x + 14, y - 30), o["id"], 22, V.WHITE, a, "SemiBold")
        for sid, node in self.snode.items():
            x, y = self.net_xy(node, box)
            off = 0 if sid != "SCH2" else 22
            col = V.BLUE if sid.startswith("EC") else V.GOLD
            cv.rect((x - 11 + off, y - 11, x + 11 + off, y + 11), col, a, 4)
            if show_labels:
                cv.text((x + 16 + off, y - 8), sid, 20, V.WHITE, a * 0.9, "SemiBold")

    def flows(self, cv, box, a, t):
        for k, r in enumerate(AL3["assignment"]):
            p = self.net_xy(r["origin"], box)
            q = self.net_xy(self.snode[r["shelter"]], box)
            col = V.GOLD if r["space"] == "classroom" else (V.GREEN if r["space"] == "non-school" else V.BLUE)
            cv.line([p, q], col, a * 0.35, 3)
            nd = max(2, int(r["persons"] / 60))
            for j in range(nd):
                ph = (t * 0.35 + j / nd + k * 0.13) % 1.0
                cv.circle((p[0] + (q[0] - p[0]) * ph, p[1] + (q[1] - p[1]) * ph), 6, col, a * 0.95)

    # scenes ----------------------------------------------------------------
    def draw(self, cv, t, sc, lt):
        name = sc["name"]
        c = self.cue
        if name == "Family":
            P.volcano(cv, 1450, 760, 150, 1.0, t, glow=V.prog(t, c["1.1"]["start"], 1.0))
            cv.rect((0, 760, V.W, 1080), (40, 18, 18), 0.9)
            P.house(cv, 330, 760, 80)
            fam = [(470, 760, 34, False), (520, 760, 30, False), (565, 760, 22, False), (615, 760, 30, True)]
            for (x, y, s, cane) in fam:
                P.person(cv, x, y, s, V.CREAM, 1.0, cane)
            a = V.prog(t, c["1.1"]["start"], 0.5)
            cv.text((120, 110), "JANUARY 2026", 40, V.GOLD_LT, a, "Bold")
            P.badge(cv, 330, 210, "ALERT LEVEL 3", 54, (230, 130, 20), a * (1 - V.prog(t, sc["end"] - 0.2, 0.2)))
            a2 = V.prog(t, c["1.2"]["start"], 0.5)
            cv.rect((660, 715, 712, 760), (160, 110, 60), a2, 8)
            cv.rect((672, 702, 700, 718), (120, 80, 40), a2, 4)
            pl = V.prog(t, c["1.2"]["start"] + 0.6, 2.5)
            for k in range(int(28 * pl)):
                cv.circle((740 + k * 22, 800 + 14 * math.sin(k * 0.4)), 4, V.WHITE, 0.8)
            a3 = V.prog(t, c["1.3"]["start"], 0.4)
            cv.card((420, 470, 860, 560), a3, V.CREAM)
            cv.text((450, 492), "Where do we go?", 40, V.INK, a3, "Bold")
            cv.poly([(560, 560), (600, 560), (540, 610)], V.CREAM, a3 * 0.96)
            a4 = V.prog(t, c["1.3"]["start"] + 2.0, 0.4)
            cv.card((560, 600, 900, 680), a4, (255, 236, 200))
            cv.text((585, 618), "Room for Lola?", 36, V.CRIMSON, a4, "Bold")
            a5 = V.prog(t, c["1.4"]["start"], 0.5)
            P.school(cv, 1150, 760, 70, a5, V.prog(t, c["1.4"]["start"] + 0.3, 1.6), None)
            if a5 > 0:
                cv.text((1150, 776), "Nearest shelter: a school", 30, V.WHITE, a5, "SemiBold", anchor="ma")
            P.stamp(cv, 1150, 640, "FULL", V.prog(t, c["1.4"]["start"] + 2.2, 0.3))
        elif name == "Community":
            import random
            rnd = random.Random(5)
            a = V.prog(t, c["2.1"]["start"], 0.8)
            cx, cy = 520, 450
            for i in range(720):
                ang = rnd.random() * 2 * math.pi
                rr = math.sqrt(rnd.random())
                x = cx + math.cos(ang) * rr * 330 * (1 + 0.25 * math.sin(ang * 3))
                y = cy + math.sin(ang) * rr * 260
                if i / 720 <= a:
                    cv.circle((x, y), 3.2, V.CREAM, 0.75)
            cv.circle((cx + 40, cy - 40), 90, (255, 90, 60), 0.18 * a)
            cv.poly([(cx + 22, cy - 30), (cx + 40, cy - 62), (cx + 58, cy - 30)], (90, 60, 60), a)
            cv.ctext(cx, 752, "ALBAY · 18 towns · 720 barangays · 1,374,768 residents", 30, V.WHITE, a, "SemiBold")
            cv.ctext(cx, 796, "PSA 2020 census", 22, V.GREY, a)
            a2 = V.prog(t, c["2.2"]["start"], 0.5) * (1 - V.prog(t, c["2.4"]["start"] - 0.3, 0.3))
            cv.card((980, 190, 1800, 420), a2, (28, 10, 14))
            cv.text((1020, 220), "JANUARY 2026", 28, V.GOLD, a2, "Bold")
            cv.text((1020, 262), "4 schools became evacuation centers", 40, V.WHITE, a2, "SemiBold")
            cv.text((1020, 318), counter_s(3424, V.prog(t, c["2.2"]["start"] + 0.5, 2.5)) + " learners affected", 52, V.GOLD_LT, a2, "Black")
            cv.text((1020, 388), "Philippine Daily Inquirer, 2026", 20, V.GREY, a2)
            a3 = V.prog(t, c["2.3"]["start"], 0.5) * (1 - V.prog(t, c["2.4"]["start"] - 0.3, 0.3))
            cv.card((980, 450, 1800, 760), a3, (28, 10, 14))
            cv.text((1020, 476), "MAY 2026 · CAMALIG", 28, V.GOLD, a3, "Bold")
            fill = V.prog(t, c["2.3"]["start"] + 0.4, 2.5)
            for k in range(34):
                col = k % 12
                row = k // 12
                x = 1020 + col * 62
                y = 524 + row * 52
                on = k < fill * 34
                cv.rect((x, y, x + 52, y + 42), (240, 170, 60) if on else (90, 70, 70), a3, 6)
            cv.text((1020, 690), "34 classrooms · 488 families · about 1,315 people", 32, V.WHITE, a3, "SemiBold")
            cv.text((1020, 732), "Daily Tribune, 2026", 20, V.GREY, a3)
            a4 = V.prog(t, c["2.4"]["start"], 0.5)
            mv = V.prog(t, c["2.5"]["start"], 1.2)
            x1 = 1000 + (680 - 1000) * mv
            x2 = 1000 + (680 - 1000) * mv
            P.chip(cv, x1, 260 - 30 * mv, "SDG 4.a", "safe places to learn", a4, V.GOLD, 600)
            P.chip(cv, x2, 420 - 70 * mv, "SDG 11.5", "protect people from disasters", V.prog(t, c["2.4"]["start"] + 2.6, 0.5), V.BLUE, 600)
            a5 = V.prog(t, c["2.5"]["start"] + 1.0, 0.6)
            P.school(cv, 1560, 470, 56, a5, 0.0)
            cv.rect((672, 508, 1545, 600), (20, 6, 10), 0.85 * a5, 14)
            cv.text((690, 520), "RA 10821: schools are evacuation centers only as a last resort", 28, V.GOLD_LT, a5, "SemiBold")
            cv.text((690, 562), "DepEd: open spaces before classrooms", 24, V.WHITE, a5)
        elif name == "Stakes":
            box = (1000, 150, 1800, 820)
            a = V.prog(t, c["3.1"]["start"], 0.5)
            P.badge(cv, 330, 180, "ALERT LEVEL 4", 54, (220, 60, 30), a)
            mins = int(53 * V.prog(t, c["3.1"]["start"] + 0.4, 6.0))
            cv.circle((330, 420), 120, (28, 10, 14), a, outline=V.GOLD, width=6)
            ang = -math.pi / 2 + 2 * math.pi * (mins / 60)
            cv.line([(330, 420), (330 + 90 * math.cos(ang), 420 + 90 * math.sin(ang))], V.GOLD, a, 8)
            cv.ctext(330, 560, "T + %02d min" % mins, 46, V.WHITE, a, "Bold")
            a2 = V.prog(t, c["3.2"]["start"], 0.6)
            self.draw_net(cv, box, max(a, 0.0) * 0.95, 1.0,
                          closed=[x for x in ("A1", "A2", "A3", "A4", "B1", "B2", "B3")
                                  if t > c["3.2"]["start"] + 1.0 + 0.3 * ("A1 A2 A3 A4 B1 B2 B3".split().index(x))],
                          show_labels=False)
            if a2 > 0:
                cv.text((1010, 96), "lahar channels A and B · bridges closed", 26, (230, 160, 120), a2, "SemiBold")
            a3 = V.prog(t, c["3.3"]["start"], 0.5)
            if a3 > 0:
                nearest = {o["id"]: o["nearest"] for o in E1["origins"]}
                for oid, sid in nearest.items():
                    p = self.net_xy(oid, box)
                    q = self.net_xy(self.snode[sid], box)
                    cv.line([p, q], V.WHITE, a3 * 0.8, 4)
                    cv.circle(q, 18, V.RED, a3 * 0.6)
                cv.card((120, 640, 900, 820), a3, (28, 10, 14))
                cv.text((150, 662), "Nearest-site rule", 32, V.GOLD, a3, "Bold")
                cv.text((150, 712), counter_s(AL3["nearest_overflow"], V.prog(t, c["3.3"]["start"] + 0.4, 2.0))
                        + " arrive at full shelters", 46, V.WHITE, a3, "Black")
                cv.text((150, 776), "test network E1 (synthetic), Alert Level 3", 22, V.GREY, a3)
            a4 = V.prog(t, c["3.4"]["start"], 0.4)
            if a4 > 0:
                cv.rect((0, 0, V.W, V.H), (0, 0, 0), 0.82 * a4)
                for i, (s, col) in enumerate((("Everyone sheltered", V.WHITE), ("Vulnerable first", V.GOLD_LT),
                                              ("Classrooms last", V.GOLD))):
                    cv.ctext(V.W / 2, 250 + i * 120, s, 78, col, V.prog(t, c["3.4"]["start"] + 0.5 + 0.9 * i, 0.4), "Black")
                cv.ctext(V.W / 2, 610, "?", 120, V.WHITE, V.prog(t, c["3.4"]["start"] + 3.2, 0.4), "Black")
        else:
            self.draw_mcs(cv, t, lt)

    def draw_mcs(self, cv, t, lt):
        c = self.cue
        s41, s42, s43, s44, s45, s46, s47, s48 = (c[k]["start"] for k in ("4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7", "4.8"))
        if t < s42 - 0.2:
            P.mcs_reveal(cv, t - s41 + 0.2)
            return
        if t >= s48 - 0.5:
            cv.rect((0, 0, V.W, V.H), (0, 0, 0), 0.5)
            P.closing(cv, t, s48, c["4.9"]["start"], c["4.10"]["start"] + 0.8,
                      "LIGTA-S will not build one more shelter.",
                      "But when the alert rises, it will tell every family where to go, and keep the most classrooms open.",
                      "Distance tells you where the shelter is.", "A plan tells you if there is room, in time.",
                      self.title_start)
            return
        lit = 0.0
        for k, st in enumerate((s42, s42 + 1.2, s44, s44 + 1.5, s45, s47)):
            lit += V.prog(t, st, 0.5)
        P.chain(cv, CHAIN, lit, 40)
        a_mcs = 1 - V.prog(t, s42, 0.4)
        if a_mcs > 0:
            P.mcs_reveal(cv, t - s41 + 0.2, alpha=a_mcs)
        box = (90, 150, 920, 860)
        if t < s46 - 0.3:
            a = V.prog(t, s42, 0.6) * (1 - V.prog(t, s46 - 0.6, 0.3))
            P.panel(cv, box, "TEST NETWORK E1 (SYNTHETIC)", a)
            netbox = (130, 200, 890, 850)
            self.draw_net(cv, netbox, a, V.prog(t, s42 + 0.3, 2.5))
            if t > s43:
                self.flows(cv, netbox, a * V.prog(t, s43 + 0.5, 0.5), t)
            if t > s45:
                pa = V.prog(t, s45 + 1.5, 0.5)
                x, y = self.net_xy("TS", netbox)
                cv.circle((x, y), 34, V.GREEN, pa * 0.5, outline=V.GREEN, width=4)
                cv.text((x - 160, y + 30), "new center: 400 of 450 reached", 24, V.GREEN, pa, "Bold")
            right = (980, 150, 1830, 860)
            if t < s44 - 0.2:
                a1 = V.prog(t, s42, 0.6) * (1 - V.prog(t, s44 - 0.5, 0.3))
                P.panel(cv, right, "MATHEMATICS", a1)
                cv.paste(self.eqimg("graph", 46), (1020, 236), V.prog(t, s42 + 1.0, 0.5) * a1)
                cv.paste(self.eqimg("tiers", 74), (1020, 306), V.prog(t, s42 + 2.6, 0.5) * a1)
                tiers = [("Tier 0", "non-school space", V.BLUE), ("Tier 1", "school open space", V.GREEN),
                         ("Tier 2", "classrooms · 18 per room", V.GOLD)]
                for i, (a_, b_, col) in enumerate(tiers):
                    ai = V.prog(t, s42 + 3.0 + 0.4 * i, 0.4) * a1
                    cv.rect((1020, 410 + i * 56, 1048, 438 + i * 56), col, ai, 6)
                    cv.text((1064, 406 + i * 56), a_ + "  ·  " + b_, 30, V.WHITE, ai, "SemiBold")
                a3 = V.prog(t, s43, 0.5) * a1
                cv.text((1020, 590), "Lexicographic order", 30, V.GOLD_LT, a3, "Bold")
                cv.paste(self.eqimg("lex", 50), (1020, 634), a3)
                cv.paste(self.eqimg("pen", 46), (1020, 710), V.prog(t, s43 + 2.0, 0.5) * a1)
                cv.text((1020, 790), "integral plans · exact · no rounding", 26, V.WHITE, V.prog(t, s43 + 3.5, 0.5) * a1)
            elif t < s45 - 0.2:
                a1 = V.prog(t, s44 - 0.2, 0.5) * (1 - V.prog(t, s45 - 0.5, 0.3))
                P.panel(cv, right, "COMPUTING", a1)
                cv.text((1020, 240), "Time-expanded network: one copy of the roads per minute", 28, V.WHITE, a1, "SemiBold")
                for col in range(9):
                    for row in range(5):
                        x = 1040 + col * 82
                        y = 290 + row * 34
                        on = V.prog(t, s44 + 0.3 + col * 0.12, 0.3)
                        cv.circle((x, y), 7, V.CREAM, a1 * on)
                        if col < 8 and row < 4:
                            cv.line([(x + 8, y + 2), (x + 74, y + 32)], V.GREY, a1 * on * 0.6, 2)
                cv.paste(self.eqimg("tstar", 50), (1020, 446), V.prog(t, s44 + 1.5, 0.5) * a1)
                curve = E1["curves"]["AL3"]
                gx0, gy0, gx1, gy1 = 1040, 560, 1780, 830
                cv.line([(gx0, gy1), (gx1, gy1)], V.GREY, a1, 2)
                cv.line([(gx0, gy0), (gx0, gy1)], V.GREY, a1, 2)
                pc = V.prog(t, s44 + 1.8, 3.0)
                pts = []
                for i, v in enumerate(curve):
                    if i / len(curve) > pc:
                        break
                    pts.append((gx0 + (gx1 - gx0) * i / (len(curve) - 1), gy1 - (gy1 - gy0) * v / 1600))
                if len(pts) > 1:
                    cv.line(pts, V.GOLD, a1, 5)
                ae = V.prog(t, s44 + 4.2, 0.4) * a1
                cv.text((gx0 + 20, gy0 - 4), "F(T): evacuees sheltered by minute T", 22, V.WHITE, a1 * 0.9)
                cv.text((1480, 690), "T* = 53 min", 40, V.GOLD, ae, "Black")
                cv.text((1480, 742), "lower bound 34 min", 24, V.WHITE, ae)
            else:
                a1 = V.prog(t, s45 - 0.2, 0.5)
                P.panel(cv, right, "OPTIMISATION", a1)
                cv.text((1020, 240), "Where to build Ligtas Pinoy Centers (RA 12076)", 28, V.WHITE, a1, "SemiBold")
                cv.paste(self.eqimg("greedy", 64), (1020, 300), V.prog(t, s45 + 0.6, 0.5) * a1)
                cv.text((1020, 400), "coverage is submodular, so the greedy choice", 28, V.WHITE, V.prog(t, s45 + 1.2, 0.5) * a1)
                cv.text((1020, 440), "always reaches at least 63.2% of the best", 28, V.WHITE, V.prog(t, s45 + 1.2, 0.5) * a1)
                rows = E1["siting"]["rows"]
                for i, r in enumerate(rows):
                    ai = V.prog(t, s45 + 2.0 + 0.6 * i, 0.4) * a1
                    y = 490 + i * 95
                    cv.rect((1020, y, 1790, y + 82), (40, 16, 20), ai, 14)
                    cv.text((1044, y + 14), "k = %d · %s" % (r["k"], ", ".join(r["sites"])), 30, V.GOLD_LT, ai, "Bold")
                    cv.text((1044, y + 48), "sheltered outside classrooms +%s · equals the best set" % "{:,}".format(r["gain"]),
                            24, V.WHITE, ai)
        else:
            # numbers and proof
            a = V.prog(t, s46 - 0.3, 0.5)
            lex, blind = AL3["lex"], AL3["blind"]
            cards = [("Classrooms closed", blind["rooms_closed_total"], lex["rooms_closed_total"], 0),
                     ("Learners displaced", blind["learners_displaced"], lex["learners_displaced"], 0)]
            if t < s47 - 0.2:
                for i, (lab, b, l, d) in enumerate(cards):
                    x0 = 140 + i * 840
                    ai = V.prog(t, s46 + 0.4 * i, 0.5) * a
                    cv.card((x0, 200, x0 + 780, 620), ai, (28, 10, 14))
                    cv.text((x0 + 40, 230), lab.upper(), 34, V.GOLD, ai, "Bold")
                    cv.text((x0 + 40, 300), "time-only plan", 28, V.GREY, ai)
                    cv.text((x0 + 40, 336), "{:,}".format(b), 90, V.WHITE, ai, "Black")
                    cv.text((x0 + 420, 300), "school-preserving", 28, V.GOLD_LT, ai)
                    cv.text((x0 + 420, 336), counter_s(l, V.prog(t, s46 + 0.8 + 0.4 * i, 1.6)), 90, V.GOLD, ai, "Black")
                    cv.text((x0 + 40, 480), "↓ %s fewer" % "{:,}".format(b - l), 44, V.GREEN, V.prog(t, s46 + 2.6, 0.5) * ai, "Bold")
                am = V.prog(t, s46 + 3.2, 0.5) * a
                cv.ctext(V.W / 2, 690, "+%.2f min mean trip" % (lex["mean_time"] - blind["mean_time"]), 60, V.WHITE, am, "Black")
                cv.ctext(V.W / 2, 780, "test network E1 (synthetic) · Alert Level 3 · 1,560 evacuees", 28, V.GREY, am)
            else:
                ap = V.prog(t, s47 - 0.2, 0.5)
                cv.ctext(V.W / 2, 190, "10 results, proven, then verified", 70, V.WHITE, ap, "Black")
                P.proof_marks(cv, 10, V.W / 2 - 9 * 34, 330, t, s47 + 0.3, 0.18, 46)
                stats = [("%s / %s" % (VER["V1"]["agree"], VER["V1"]["instances"]), "plans matched five linear programs"),
                         ("%s / %s" % ("{:,}".format(VER["V3"]["agree"]), "{:,}".format(VER["V3"]["pairs"])), "networks matched Ford–Fulkerson"),
                         ("{:,}".format(VER["V6"]["checks_total"]), "submodularity checks, 0 violations")]
                for i, (big, small) in enumerate(stats):
                    ai = V.prog(t, s47 + 1.8 + 0.4 * i, 0.4)
                    x0 = 170 + i * 540
                    cv.card((x0, 450, x0 + 500, 640), ai, (28, 10, 14))
                    cv.text((x0 + 30, 476), big, 64, V.GOLD, ai, "Black")
                    cv.text((x0 + 30, 570), small, 26, V.WHITE, ai, "SemiBold")


def counter_s(v, p):
    return "{:,}".format(int(round(v * V.ease(p))))


def main():
    spec = Spec()
    data = V.save_timeline(spec, os.path.join(HERE, "timeline.json"))
    print("length %.1f s, title at %.1f s, boom %.1f s" % (spec.total, spec.title_start, spec.boom_t))
    if "--preview" in sys.argv:
        pdir = os.path.join(OUT, "_preview")
        os.makedirs(pdir, exist_ok=True)
        times = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1:]] if len(sys.argv) > 2 else []
        if not times:
            for sc in spec.scenes:
                for cu in sc["cues"]:
                    times.append(cu["start"] + 1.5)
            times += [spec.title_start + 6]
        V.render(spec, pdir, "x.mp4", only=[int(x * V.FPS) for x in times])
        return
    out = V.render(spec, OUT, NAME)
    # title frame stills
    img, _ = spec.title.draw(7.0)
    img.save(os.path.join(OUT, "LIGTA-S_Title_Page_1920x1080.png"))
    img.resize((3840, 2160), Image.LANCZOS).save(os.path.join(OUT, "LIGTA-S_Title_Page_3840x2160.png"))
    print(out)


if __name__ == "__main__":
    main()

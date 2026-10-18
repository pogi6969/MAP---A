"""BANTA-Y rationale video (version without narration) and its timeline.

Run:  python3 make_video.py            -> ../BANTA-Y_Rationale_Video_v1_MCS_No_Narration.mp4
      python3 make_video.py --preview t1 t2 ...  -> still frames for checking
"""

import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(PROJ, ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import rationale_parts as P  # noqa: E402
import rationale_video as V  # noqa: E402
from PIL import Image  # noqa: E402

BRAND = "BANTA-Y"
OUT = os.path.join(PROJ, "video")
NAME = "BANTA-Y_Rationale_Video_v1_MCS_No_Narration.mp4"
RES = json.load(open(os.path.join(PROJ, "code", "results.json")))
D1 = RES["d1"]
VER = RES["verification"]
POS = [(0.0, 0.0), (1.5, 0.5), (3.0, -1.0), (6.0, 4.0), (-4.0, -3.0), (2.0, -5.0)]
IDS = ["B1", "B2", "B3", "B4", "B5", "B6"]
LABEL = ["B1 school + market", "B2 residential", "B3 peri-urban", "B4 upland", "B5 lowland", "B6 coast"]

SCENES = [
    {"name": "Pupil", "bar": "Health", "cues": [
        {"id": "1.1", "text": "September 2026. A Grade 5 pupil in Legazpi wakes up with a high fever.",
         "onscreen": "\"SEPTEMBER 2026\"; a house at dawn; a pupil with a thermometer; the badge \"DENGUE\" fades in."},
        {"id": "1.2", "text": "The clinic writes down one thing first: her home address.",
         "onscreen": "A case-report card slides in: \"Case report · Address: home barangay\"; a pin drops on the house."},
        {"id": "1.3", "text": "But the mosquito that bit her was not at home. It was at school, in the middle of the day.",
         "onscreen": "The sun rises; a dotted path runs from the house to the school; an Aedes mosquito circles the school; the house pin greys out."},
    ]},
    {"name": "Province", "bar": "Province", "cues": [
        {"id": "2.1", "text": "Zoom out to Albay.",
         "onscreen": "Albay as a field of 720 barangay dots in 18 towns."},
        {"id": "2.2", "text": "By mid-September, the province had 2,179 cases and 14 deaths, 84 percent more than the year before.",
         "onscreen": "Counters: 2,179 cases · 14 deaths · +84% vs the same period of 2025 (Jan 1 to Sept 12, 2026); source Daily Tribune, 2026."},
        {"id": "2.3", "text": "The province declared a state of calamity, and schools closed for a week of cleanup.",
         "onscreen": "Badge \"STATE OF CALAMITY\"; a school with the sign \"Closed Sept 14 to 18 · cleanup and fogging\"."},
        {"id": "2.4", "text": "Sustainable Development Goal 3 asks us to end epidemics like dengue.",
         "onscreen": "Chips: \"SDG 3.3 · end the epidemics of neglected tropical diseases\" and \"SDG 3.d · early warning\"."},
    ]},
    {"name": "Place", "bar": "Place", "cues": [
        {"id": "3.1", "text": "Every case is filed by home address, so the brigades go to the homes.",
         "onscreen": "Test network D1 (synthetic): bars of cases by residence; B2 has the most; brigade markers move to B2."},
        {"id": "3.2", "text": "But Aedes aegypti bites by day, where people gather: classrooms, markets, terminals.",
         "onscreen": "Daytime arrows flow from every barangay into B1, the poblacion with the central school and public market; B1 glows."},
        {"id": "3.3", "text": "Spray where cases live, and you may spray the wrong barangay.",
         "onscreen": "Spray cloud over B2 while B1 stays red; stamp \"WRONG PLACE?\"."},
        {"id": "3.4", "text": "So where is dengue really spreading, and how much control is enough?",
         "onscreen": "Three lines build: \"Where does it spread? · How much is enough? · When do we warn?\""},
    ]},
    {"name": "How MCS comes into play", "bar": "MCS", "cues": [
        {"id": "4.1", "text": "This is where MCS comes into play.",
         "onscreen": "The letters M, C and S drop in, then unfold into Mathematical, Computational, Sciences."},
        {"id": "4.2", "text": "Mathematics writes each barangay's day as a matrix: who spends how many hours, and where.",
         "onscreen": "Chain lights \"Open data → Graph\"; panel MATHEMATICS: the 6 × 6 residence-time matrix P of test network D1 fills in as a heat map; p_ii = 1 − ω_i, p_ij ∝ A_j e^(−βT_ij)."},
        {"id": "4.3", "text": "Its largest eigenvalue gives the reproduction number, and dengue fades when it falls below one.",
         "onscreen": "M = κ D_N P W Pᵀ, R0² = λ_max(S); dial shows R0 = 1.214 with the threshold line at 1."},
        {"id": "4.4", "text": "Computing splits that number into shares by place, and ranks the true hotspots.",
         "onscreen": "Chain lights \"Algorithm → Numbers\"; panel COMPUTING: paired bars, cases by residence vs transmission by place; B1 rises to 42.6%."},
        {"id": "4.5", "text": "Optimisation finds the cheapest brigade plan that brings the number below one, with a certificate that nothing cheaper exists.",
         "onscreen": "Chain lights \"Optimisation\"; panel OPTIMISATION: min Σ c_j u_j subject to R0(u) ≤ 0.95; cost bars for five strategies, least cost 22.60 team-days with its certified lower bound."},
        {"id": "4.6", "text": "On the test network, cases pointed to a residential barangay, but forty-three percent of transmission was at the school and market.",
         "onscreen": "Two cards: \"Most cases by home: B2, 28.5%\" and \"Most transmission by place: B1, 42.6%\" (test network D1, synthetic)."},
        {"id": "4.7", "text": "The least-cost plan needed forty percent fewer team-days than spraying everywhere.",
         "onscreen": "Counter: 37.47 → 22.60 team-days, −40%; versus spraying where cases live 38.88 (−42%)."},
        {"id": "4.8", "text": "And a CUSUM alarm warned more than a week and a half sooner than a single-week threshold.",
         "onscreen": "CUSUM curve S_t climbs past h = 12.75; bars of mean delay: CUSUM 4.84 weeks vs single-week rule 6.52 weeks at the same 5% false-alarm rate (5,000 simulated years)."},
        {"id": "4.9", "text": "Twelve results, proven, then verified against independent code.",
         "onscreen": "Chain lights \"Proof\"; twelve proof squares turn into green checks; 300/300 reproduction numbers, 120/120 control plans, 10,000 alarm sequences."},
        {"id": "4.10", "text": "BANTA-Y will not kill one mosquito.", "pause": 0.6,
         "onscreen": "Boom. Screen darkens; the line appears in white."},
        {"id": "4.11", "text": "But it will tell the brigades where the bites really happen, and how much is enough.",
         "onscreen": "The line appears in gold."},
        {"id": "4.12", "text": "[pause] Homes tell you where dengue is reported. Places tell you where it spreads.",
         "pause": 0.8, "hold": 1.0,
         "onscreen": "Two lines: \"Homes tell you where dengue is reported.\" (white), then \"Places tell you where it spreads.\" (gold)."},
    ]},
]

TITLE_LINES = ["Where People Go, Dengue Goes: A Verified Mobility-Coupled Network Model",
               "for Ranking Dengue Hotspots, Issuing Early Warnings, and Allocating",
               "Vector Control at Least Cost in Albay"]

CHAIN = ["Open data", "Graph", "Algorithm", "Numbers", "Optimisation", "Proof"]


def counter_s(v, p, dec=0):
    x = v * V.ease(p)
    return ("{:,.%df}" % dec).format(x) if dec else "{:,}".format(int(round(x)))


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
        self.boom_t = self.cue["4.10"]["start"] - 0.25
        eqdir = os.path.join(HERE, "eq")
        os.makedirs(eqdir, exist_ok=True)
        tex = {
            "P": r"p_{ii}=1-\omega_i,\qquad p_{ij}\ \propto\ A_j\,e^{-\beta T_{ij}},\qquad \tilde N_j=\textstyle\sum_k p_{kj}N_k",
            "M": r"M=\kappa\,D_N\,P\,W\,P^{\top},\qquad \mathcal{R}_0^2=\lambda_{\max}(S)",
            "share": r"s_j=\frac{\kappa\,w_j\,(q_j^{\top}v)^2}{\lambda},\qquad \textstyle\sum_j s_j=1",
            "opt": r"\min_u\ \textstyle\sum_j c_j u_j\quad \text{s.t.}\quad \mathcal{R}_0(u)\le 0.95,\ \ 0\le u_j\le 0.8",
            "cusum": r"S_t=\max\{0,\ S_{t-1}+x_t-k_t\},\qquad \text{alarm when } S_t\ge h",
        }
        self.eq = {k: V.latex_png(v, os.path.join(eqdir, k + ".png")) for k, v in tex.items()}

    def eqimg(self, key, height, maxw=780):
        im = V.scaled(self.eq[key], height=height)
        if im.size[0] > maxw:
            im = V.scaled(self.eq[key], width=maxw)
        return im

    def xy(self, i, box):
        x0, y0, x1, y1 = box
        s = min(x1 - x0, y1 - y0) / 13.5
        cx, cy = (x0 + x1) / 2 - 1.0 * s, (y0 + y1) / 2
        x, y = POS[i]
        return cx + x * s, cy - y * s

    def draw_net(self, cv, box, a, labels=True, heat=None):
        N = [r["residents"] for r in D1["rows"]]
        Pm = D1["P"]
        for i in range(6):
            for j in range(6):
                if i != j and Pm[i][j] * N[i] > 120:
                    p, q = self.xy(i, box), self.xy(j, box)
                    cv.line([p, q], (200, 190, 190), a * 0.35, 2)
        for i in range(6):
            x, y = self.xy(i, box)
            r = 16 + 18 * math.sqrt(N[i] / 6000)
            m = D1["m"][i]
            heatv = (m - 1.6) / 1.4 if heat is None else heat[i]
            col = (int(250 - 40 * (1 - heatv)), int(200 - 150 * heatv), int(120 - 90 * heatv))
            cv.circle((x, y), r, col, a, outline=(40, 20, 20), width=2)
            if labels:
                cv.text((x, y + r + 6), IDS[i], 24, V.WHITE, a, "Bold", anchor="ma")

    def draw(self, cv, t, sc, lt):
        name = sc["name"]
        c = self.cue
        if name == "Pupil":
            sun = V.prog(t, c["1.3"]["start"], 1.5)
            cv.rect((0, 760, V.W, 1080), (40, 18, 18), 0.9)
            cv.circle((1500, 300 - 120 * sun), 70, (255, 200, 80), 0.25 + 0.6 * sun)
            P.house(cv, 360, 760, 90)
            P.person(cv, 520, 760, 26, V.CREAM)
            a = V.prog(t, c["1.1"]["start"], 0.5)
            cv.text((120, 110), "SEPTEMBER 2026", 40, V.GOLD_LT, a, "Bold")
            P.badge(cv, 290, 210, "DENGUE", 54, (200, 40, 40), a)
            cv.rect((556, 650, 568, 720), V.WHITE, a, 6)
            cv.circle((562, 724), 12, V.RED, a)
            a2 = V.prog(t, c["1.2"]["start"], 0.5)
            cv.card((640, 380, 1180, 560), a2, V.CREAM)
            cv.text((670, 404), "CASE REPORT", 30, V.CRIMSON, a2, "Black")
            cv.text((670, 452), "Address: home barangay", 34, V.INK, a2, "SemiBold")
            cv.text((670, 500), "Diagnosis: dengue", 28, V.INK, a2)
            grey = V.prog(t, c["1.3"]["start"] + 2.5, 0.6)
            pin_col = tuple(int(V.RED[k] * (1 - grey) + 120 * grey) for k in range(3))
            pa = V.prog(t, c["1.2"]["start"] + 1.0, 0.4)
            py = 560 - 60 * (1 - P.back_out(V.clamp((t - c["1.2"]["start"] - 1.0) / 0.4)))
            cv.circle((360, py), 26, pin_col, pa)
            cv.poly([(340, py + 14), (380, py + 14), (360, py + 50)], pin_col, pa)
            a3 = V.prog(t, c["1.3"]["start"], 0.6)
            P.school(cv, 1450, 760, 70, a3, 0.4)
            pl = V.prog(t, c["1.3"]["start"] + 0.5, 2.0)
            for k in range(int(36 * pl)):
                cv.circle((560 + k * 22, 800 + 10 * math.sin(k * 0.5)), 4, V.WHITE, 0.8)
            if a3 > 0:
                ang = t * 2.2
                P.mosquito(cv, 1450 + 230 * math.cos(ang), 560 + 70 * math.sin(ang * 1.3), 22, a3, t)
                cv.text((1450, 776), "School, 10:00 a.m.", 30, V.WHITE, a3, "SemiBold", anchor="ma")
        elif name == "Province":
            rnd = random.Random(9)
            a = V.prog(t, c["2.1"]["start"], 0.8)
            cx, cy = 520, 450
            for i in range(720):
                ang = rnd.random() * 2 * math.pi
                rr = math.sqrt(rnd.random())
                x = cx + math.cos(ang) * rr * 330 * (1 + 0.25 * math.sin(ang * 3))
                y = cy + math.sin(ang) * rr * 260
                if i / 720 <= a:
                    hot = rnd.random() < 0.08 * V.prog(t, c["2.2"]["start"], 2.0)
                    cv.circle((x, y), 3.4 if hot else 3.0, V.RED if hot else V.CREAM, 0.85)
            cv.ctext(cx, 752, "ALBAY · 18 towns · 720 barangays", 30, V.WHITE, a, "SemiBold")
            a2 = V.prog(t, c["2.2"]["start"], 0.5) * (1 - V.prog(t, c["2.4"]["start"] - 0.3, 0.3))
            cv.card((980, 170, 1800, 470), a2, (28, 10, 14))
            cv.text((1020, 196), "JANUARY 1 TO SEPTEMBER 12, 2026", 28, V.GOLD, a2, "Bold")
            p2 = V.prog(t, c["2.2"]["start"] + 0.4, 2.2)
            cv.text((1020, 246), counter_s(2179, p2), 96, V.WHITE, a2, "Black")
            cv.text((1300, 290), "cases", 40, V.WHITE, a2, "SemiBold")
            cv.text((1500, 246), counter_s(14, p2), 96, V.RED, a2, "Black")
            cv.text((1650, 290), "deaths", 40, V.WHITE, a2, "SemiBold")
            cv.text((1020, 370), "+84% vs the same months of 2025", 40, V.GOLD_LT, V.prog(t, c["2.2"]["start"] + 2.6, 0.5) * a2, "Bold")
            cv.text((1020, 432), "Daily Tribune, 2026", 20, V.GREY, a2)
            a3 = V.prog(t, c["2.3"]["start"], 0.5) * (1 - V.prog(t, c["2.4"]["start"] - 0.3, 0.3))
            if a3 > 0:
                P.badge(cv, 1390, 540, "STATE OF CALAMITY", 46, (200, 40, 40), a3)
                P.school(cv, 1250, 820, 60, a3, 0.0)
                cv.card((1430, 690, 1800, 800), a3, V.CREAM)
                cv.text((1450, 706), "CLOSED", 34, V.CRIMSON, a3, "Black")
                cv.text((1450, 752), "Sept 14–18 · cleanup", 26, V.INK, a3, "SemiBold")
            a4 = V.prog(t, c["2.4"]["start"], 0.5)
            P.chip(cv, 1000, 300, "SDG 3.3", "end the epidemics of neglected tropical diseases", a4, V.GOLD, 780)
            P.chip(cv, 1000, 450, "SDG 3.d", "early warning and health-risk management", V.prog(t, c["2.4"]["start"] + 1.4, 0.5), V.BLUE, 780)
        elif name == "Place":
            box = (980, 130, 1820, 820)
            a = V.prog(t, c["3.1"]["start"], 0.6)
            self.draw_net(cv, box, a)
            cv.text((1000, 96), "test network D1 (synthetic)", 26, V.GREY, a, "SemiBold")
            # cases by residence bars
            for i in range(6):
                ai = V.prog(t, c["3.1"]["start"] + 0.3 + 0.15 * i, 0.4)
                h = 300 * D1["case_share"][i] / 0.3
                x0 = 140 + i * 120
                cv.rect((x0, 620 - h * ai, x0 + 80, 620), (230, 150, 150), ai * a, 6)
                cv.text((x0 + 40, 630), IDS[i], 26, V.WHITE, ai * a, "Bold", anchor="ma")
            cv.text((140, 220), "Cases by home address", 40, V.WHITE, a, "Bold")
            cv.text((140, 270), "the brigades follow the addresses", 28, V.GREY, a)
            bx = V.prog(t, c["3.1"]["start"] + 2.0, 1.5)
            if bx > 0:
                p = self.xy(1, box)
                for k in range(3):
                    sx = 980 + (p[0] - 980) * bx + k * 18
                    sy = 900 + (p[1] - 900) * bx - k * 10
                    cv.rect((sx - 10, sy - 10, sx + 10, sy + 10), V.BLUE, 0.9, 4)
            a2 = V.prog(t, c["3.2"]["start"], 0.6)
            if a2 > 0:
                b1 = self.xy(0, box)
                for i in range(1, 6):
                    p = self.xy(i, box)
                    for j in range(4):
                        ph = (t * 0.45 + j / 4 + i * 0.1) % 1
                        cv.circle((p[0] + (b1[0] - p[0]) * ph, p[1] + (b1[1] - p[1]) * ph), 6, V.GOLD, a2)
                    cv.line([p, b1], V.GOLD, a2 * 0.35, 3)
                cv.circle(b1, 70 + 6 * math.sin(t * 5), V.RED, a2 * 0.30)
                cv.text((b1[0] - 140, b1[1] - 120), "school + market, by day", 26, V.GOLD_LT, a2, "Bold")
            a3 = V.prog(t, c["3.3"]["start"], 0.5)
            if a3 > 0:
                p = self.xy(1, box)
                for k in range(14):
                    ang = k * 0.9 + t
                    cv.circle((p[0] + 40 * math.cos(ang), p[1] - 50 + 30 * math.sin(ang)), 22, (220, 230, 240), a3 * 0.35)
                P.stamp(cv, 1400, 760, "WRONG PLACE?", V.prog(t, c["3.3"]["start"] + 1.5, 0.3), 46)
            a4 = V.prog(t, c["3.4"]["start"], 0.4)
            if a4 > 0:
                cv.rect((0, 0, V.W, V.H), (0, 0, 0), 0.82 * a4)
                for i, (s, col) in enumerate((("Where does it spread?", V.WHITE), ("How much is enough?", V.GOLD_LT),
                                              ("When do we warn?", V.GOLD))):
                    cv.ctext(V.W / 2, 250 + i * 120, s, 78, col, V.prog(t, c["3.4"]["start"] + 0.5 + 0.9 * i, 0.4), "Black")
        else:
            self.draw_mcs(cv, t)

    def draw_mcs(self, cv, t):
        c = self.cue
        s = {k: c[k]["start"] for k in c if k.startswith("4.")}
        if t < s["4.2"] - 0.2:
            P.mcs_reveal(cv, t - s["4.1"] + 0.2)
            return
        if t >= s["4.10"] - 0.5:
            cv.rect((0, 0, V.W, V.H), (0, 0, 0), 0.5)
            P.closing(cv, t, s["4.10"], s["4.11"], s["4.12"] + 0.8,
                      "BANTA-Y will not kill one mosquito.",
                      "But it will tell the brigades where the bites really happen, and how much is enough.",
                      "Homes tell you where dengue is reported.", "Places tell you where it spreads.",
                      self.title_start)
            return
        lit = 0.0
        for st in (s["4.2"], s["4.2"] + 1.2, s["4.4"], s["4.4"] + 1.5, s["4.5"], s["4.9"]):
            lit += V.prog(t, st, 0.5)
        P.chain(cv, CHAIN, lit, 40)
        a_mcs = 1 - V.prog(t, s["4.2"], 0.4)
        if a_mcs > 0:
            P.mcs_reveal(cv, t - s["4.1"] + 0.2, alpha=a_mcs)
        left = (90, 150, 920, 860)
        right = (980, 150, 1830, 860)
        if t < s["4.6"] - 0.3:
            a = V.prog(t, s["4.2"], 0.6) * (1 - V.prog(t, s["4.6"] - 0.6, 0.3))
            if t < s["4.4"] - 0.2:
                # left: matrix heat map
                P.panel(cv, left, "MATRIX P · TEST NETWORK D1", a)
                Pm = D1["P"]
                x0, y0, cs = 250, 270, 84
                for i in range(6):
                    cv.text((x0 - 20, y0 + i * cs + 28), IDS[i], 26, V.WHITE, a, "Bold", anchor="ra")
                    cv.text((x0 + i * cs + cs / 2, y0 - 40), IDS[i], 26, V.WHITE, a, "Bold", anchor="ma")
                    for j in range(6):
                        k = i * 6 + j
                        ak = V.prog(t, s["4.2"] + 0.5 + k * 0.05, 0.3) * a
                        v = Pm[i][j]
                        inten = min(1.0, v / 0.8) ** 0.5
                        col = (int(60 + 190 * inten), int(30 + 140 * inten), int(40 + 20 * inten))
                        cv.rect((x0 + j * cs + 3, y0 + i * cs + 3, x0 + (j + 1) * cs - 3, y0 + (i + 1) * cs - 3), col, ak, 8)
                        cv.text((x0 + j * cs + cs / 2, y0 + i * cs + 28), "%.2f" % v, 22,
                                V.INK if inten > 0.6 else V.WHITE, ak, "SemiBold", anchor="ma")
                cv.text((130, 790), "share of biting hours residents of each row spend in each column", 22, V.GREY, a)
                a1 = V.prog(t, s["4.2"], 0.6) * (1 - V.prog(t, s["4.4"] - 0.5, 0.3))
                P.panel(cv, right, "MATHEMATICS", a1)
                cv.paste(self.eqimg("P", 56), (1020, 250), V.prog(t, s["4.2"] + 1.0, 0.5) * a1)
                cv.text((1020, 330), "ω = share of the day away from home; A = pull of schools, markets, jobs", 24, V.WHITE, V.prog(t, s["4.2"] + 2.0, 0.5) * a1)
                a3 = V.prog(t, s["4.3"], 0.5) * a1
                cv.paste(self.eqimg("M", 60), (1020, 400), a3)
                # dial
                r0 = D1["r0"]
                cx, cy, R = 1400, 720, 120
                cv.d.arc((cx - R, cy - R, cx + R, cy + R), 180, 360, fill=V.rgba(V.GREY, a3), width=14)
                frac_one = 1 / 2.0
                ang1 = math.pi + math.pi * frac_one
                cv.line([(cx + (R - 30) * math.cos(ang1), cy + (R - 30) * math.sin(ang1)),
                         (cx + (R + 20) * math.cos(ang1), cy + (R + 20) * math.sin(ang1))], V.WHITE, a3, 5)
                cv.text((cx + (R + 34) * math.cos(ang1), cy + (R + 50) * math.sin(ang1)), "1", 28, V.WHITE, a3, "Bold", anchor="ma")
                pv = V.prog(t, s["4.3"] + 1.2, 1.6)
                val = r0 * pv
                angv = math.pi + math.pi * min(val, 2.0) / 2.0
                cv.line([(cx, cy), (cx + (R - 10) * math.cos(angv), cy + (R - 10) * math.sin(angv))], V.GOLD, a3, 8)
                cv.circle((cx, cy), 12, V.GOLD, a3)
                cv.text((cx, cy + 30), "R₀ = %.3f" % val, 48, V.GOLD, a3, "Black", anchor="ma")
                cv.text((cx, cy + 92), "above 1: dengue can spread", 26, V.WHITE, V.prog(t, s["4.3"] + 2.8, 0.5) * a3, "SemiBold", anchor="ma")
            else:
                P.panel(cv, left, "TEST NETWORK D1 (SYNTHETIC)", a)
                heat = [min(1, sh / 0.43) for sh in D1["shares"]]
                hp = V.prog(t, s["4.4"] + 1.5, 1.5)
                hh = [h * hp + ((D1["m"][i] - 1.6) / 1.4) * (1 - hp) for i, h in enumerate(heat)]
                self.draw_net(cv, (130, 220, 890, 840), a, True, hh)
                if t < s["4.5"] - 0.2:
                    a1 = V.prog(t, s["4.4"] - 0.2, 0.5) * (1 - V.prog(t, s["4.5"] - 0.5, 0.3))
                    P.panel(cv, right, "COMPUTING", a1)
                    cv.paste(self.eqimg("share", 70), (1020, 240), V.prog(t, s["4.4"] + 0.4, 0.5) * a1)
                    pb = V.prog(t, s["4.4"] + 1.0, 1.8)
                    for i in range(6):
                        y = 380 + i * 72
                        cv.text((1020, y + 10), IDS[i], 28, V.WHITE, a1, "Bold")
                        w1 = 600 * D1["case_share"][i] / 0.45 * pb
                        w2 = 600 * D1["shares"][i] / 0.45 * pb
                        cv.rect((1080, y, 1080 + w1, y + 26), (230, 150, 150), a1 * 0.9, 6)
                        cv.rect((1080, y + 30, 1080 + w2, y + 56), V.GOLD, a1, 6)
                        cv.text((1090 + w2, y + 28), "%.1f%%" % (100 * D1["shares"][i] * pb), 24, V.GOLD_LT, a1 * pb, "Bold")
                    cv.rect((1020, 820, 1046, 840), (230, 150, 150), a1, 4)
                    cv.text((1056, 814), "cases by residence", 22, V.WHITE, a1)
                    cv.rect((1290, 820, 1316, 840), V.GOLD, a1, 4)
                    cv.text((1326, 814), "transmission by place", 22, V.WHITE, a1)
                else:
                    a1 = V.prog(t, s["4.5"] - 0.2, 0.5)
                    P.panel(cv, right, "OPTIMISATION", a1)
                    cv.paste(self.eqimg("opt", 56), (1020, 240), V.prog(t, s["4.5"] + 0.4, 0.5) * a1)
                    st = D1["strategies"]
                    rows = [("Spray where cases live", st["case_residence"]["cost"], (230, 150, 150)),
                            ("Spray everywhere equally", st["uniform"]["cost"], V.GREY),
                            ("Place-share heuristic", st["place_share"]["cost"], V.BLUE),
                            ("Quick certificate (LP)", st["certificate"]["cost"], V.GREEN),
                            ("Least cost, certified", st["exact"]["cost"], V.GOLD)]
                    for i, (lab, cost, col) in enumerate(rows):
                        ai = V.prog(t, s["4.5"] + 1.2 + 0.5 * i, 0.4) * a1
                        y = 350 + i * 92
                        cv.text((1020, y), lab, 26, V.WHITE, ai, "SemiBold")
                        w = 560 * cost / 40.0 * V.ease(V.clamp((t - s["4.5"] - 1.2 - 0.5 * i) / 0.8))
                        cv.rect((1020, y + 36, 1020 + w, y + 72), col, ai, 8)
                        cv.text((1030 + w, y + 36), "%.2f" % cost, 30, col, ai, "Black")
                    cv.text((1020, 820), "team-days to bring R₀ to 0.95 · lower bound 22.5965", 22, V.GREY,
                            V.prog(t, s["4.5"] + 4.0, 0.5) * a1)
        else:
            a = V.prog(t, s["4.6"] - 0.3, 0.5)
            if t < s["4.8"] - 0.2:
                if t < s["4.7"] - 0.2:
                    for i, (lab, big, sub, col) in enumerate((
                            ("MOST CASES BY HOME", "B2 · %.1f%%" % (100 * D1["case_share"][1]), "residential barangay", (230, 150, 150)),
                            ("MOST TRANSMISSION BY PLACE", "B1 · %.1f%%" % (100 * D1["shares"][0]), "poblacion: central school + public market", V.GOLD))):
                        x0 = 140 + i * 840
                        ai = V.prog(t, s["4.6"] + 0.6 * i, 0.5) * a
                        cv.card((x0, 220, x0 + 780, 600), ai, (28, 10, 14))
                        cv.text((x0 + 40, 250), lab, 34, col, ai, "Bold")
                        cv.text((x0 + 40, 320), big, 110, V.WHITE if i == 0 else V.GOLD, ai, "Black")
                        cv.text((x0 + 40, 480), sub, 30, V.WHITE, ai, "SemiBold")
                    cv.ctext(V.W / 2, 680, "test network D1 (synthetic)", 28, V.GREY, a)
                else:
                    a2 = V.prog(t, s["4.7"] - 0.2, 0.5)
                    st = D1["strategies"]
                    cv.card((240, 200, 1680, 640), a2, (28, 10, 14))
                    cv.text((300, 240), "TEAM-DAYS TO REACH R₀ ≤ 0.95", 36, V.GOLD, a2, "Bold")
                    cv.text((300, 310), "spray everywhere", 30, V.GREY, a2)
                    cv.text((300, 350), "%.2f" % st["uniform"]["cost"], 120, V.WHITE, a2, "Black")
                    cv.text((900, 310), "least-cost plan", 30, V.GOLD_LT, a2)
                    pv = V.prog(t, s["4.7"] + 0.6, 1.5)
                    val = st["uniform"]["cost"] + (st["exact"]["cost"] - st["uniform"]["cost"]) * pv
                    cv.text((900, 350), "%.2f" % val, 120, V.GOLD, a2, "Black")
                    cv.text((300, 520), "−40%% team-days · −42%% vs spraying where cases live", 40, V.GREEN,
                            V.prog(t, s["4.7"] + 2.0, 0.5) * a2, "Bold")
            elif t < s["4.9"] - 0.2:
                a3 = V.prog(t, s["4.8"] - 0.2, 0.5)
                cv.paste(self.eqimg("cusum", 56, 1200), (V.W / 2, 150), a3, anchor="ma")
                cu = D1["cusum"]
                gx0, gy0, gx1, gy1 = 160, 280, 1100, 780
                cv.line([(gx0, gy1), (gx1, gy1)], V.GREY, a3, 2)
                cv.line([(gx0, gy0), (gx0, gy1)], V.GREY, a3, 2)
                Ssc = 60.0
                hy = gy1 - (gy1 - gy0) * cu["h"] / Ssc
                cv.line([(gx0, hy), (gx1, hy)], V.RED, a3, 3)
                cv.text((gx0 + 8, hy - 34), "h = %.2f" % cu["h"], 24, V.RED, a3, "Bold")
                pc = V.prog(t, s["4.8"] + 0.3, 3.0)
                pts = []
                n = len(cu["S"])
                for i, v in enumerate(cu["S"][:36]):
                    if i / 35 > pc:
                        break
                    pts.append((gx0 + (gx1 - gx0) * i / 35, gy1 - (gy1 - gy0) * min(v, Ssc) / Ssc))
                if len(pts) > 1:
                    cv.line(pts, V.GOLD, a3, 5)
                cv.text((gx0, gy1 + 14), "weeks of a simulated outbreak year (test network D1)", 22, V.GREY, a3)
                ab = V.prog(t, s["4.8"] + 2.5, 0.5) * a3
                cv.card((1180, 280, 1800, 780), ab, (28, 10, 14))
                cv.text((1220, 304), "MEAN WEEKS TO ALARM", 30, V.GOLD, ab, "Bold")
                cv.text((1220, 344), "same 5% false-alarm rate · 5,000 years", 22, V.GREY, ab)
                for i, (lab, v, col) in enumerate((("CUSUM", D1["cusum"]["delay_cusum_mean"], V.GOLD),
                                                   ("single-week rule", D1["cusum"]["delay_threshold_mean"], V.GREY))):
                    y = 420 + i * 150
                    cv.text((1220, y), lab, 30, V.WHITE, ab, "SemiBold")
                    w = 480 * v / 7.0 * V.prog(t, s["4.8"] + 2.8 + 0.4 * i, 0.8)
                    cv.rect((1220, y + 44, 1220 + w, y + 96), col, ab, 10)
                    cv.text((1230 + w, y + 48), "%.2f" % v, 40, col, ab, "Black")
            else:
                ap = V.prog(t, s["4.9"] - 0.2, 0.5)
                cv.ctext(V.W / 2, 190, "12 results, proven, then verified", 70, V.WHITE, ap, "Black")
                P.proof_marks(cv, 12, V.W / 2 - 11 * 34, 330, t, s["4.9"] + 0.2, 0.15, 46)
                stats = [("%s / %s" % (VER["V1"]["instances"], VER["V1"]["instances"]), "reproduction numbers match to 5 × 10⁻¹⁵"),
                         ("%d / %d" % (VER["V6"]["grid_ok"] + VER["V6"]["slsqp_ok"], VER["V6"]["grid_cases"] + VER["V6"]["slsqp_cases"]), "least-cost plans confirmed"),
                         ("{:,}".format(VER["V8"]["delay_checks"]), "alarm sequences, 0 violations")]
                for i, (big, small) in enumerate(stats):
                    ai = V.prog(t, s["4.9"] + 1.6 + 0.4 * i, 0.4)
                    x0 = 170 + i * 540
                    cv.card((x0, 450, x0 + 500, 640), ai, (28, 10, 14))
                    cv.text((x0 + 30, 476), big, 64, V.GOLD, ai, "Black")
                    cv.text((x0 + 30, 570), small, 24, V.WHITE, ai, "SemiBold")


def main():
    spec = Spec()
    V.save_timeline(spec, os.path.join(HERE, "timeline.json"))
    print("length %.1f s, title at %.1f s, boom %.1f s" % (spec.total, spec.title_start, spec.boom_t))
    if "--preview" in sys.argv:
        pdir = os.path.join(OUT, "_preview")
        os.makedirs(pdir, exist_ok=True)
        times = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1:]]
        if not times:
            times = [cu["start"] + 1.5 for sc in spec.scenes for cu in sc["cues"]] + [spec.title_start + 6]
        V.render(spec, pdir, "x.mp4", only=[int(x * V.FPS) for x in times])
        return
    out = V.render(spec, OUT, NAME)
    img, _ = spec.title.draw(7.0)
    img.save(os.path.join(OUT, "BANTA-Y_Title_Page_1920x1080.png"))
    img.resize((3840, 2160), Image.LANCZOS).save(os.path.join(OUT, "BANTA-Y_Title_Page_3840x2160.png"))
    print(out)


if __name__ == "__main__":
    main()

"""MAP-A rationale video v6: the four objectives of the paper, its verified results, and
the app. The timing follows the spoken narration, so the picture, the subtitles and the
voice move together with no dead air.

Run:  python3 make_video.py            -> ../MAP-A_Rationale_Video_v6_MCS_No_Narration.mp4
                                          ../MAP-A_Rationale_Video_v6_MCS_Narrated.mp4
      python3 make_video.py --preview  -> still frames for checking
"""

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
import voiced  # noqa: E402
from PIL import Image  # noqa: E402

BRAND = "MAP-A"
OUT = os.path.join(PROJ, "video")
NAME = "MAP-A_Rationale_Video_v6_MCS_No_Narration.mp4"
NAME_VO = "MAP-A_Rationale_Video_v6_MCS_Narrated.mp4"
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "kokoro", "clips")
TITLE = ("A Landmark-Anchored Timetable-Graph Model of Public Transport: Verified Computation of "
         "Accessibility, Its Inequality, and the Fare Matrix from Open Data, with Agent-Reported "
         "Hospital Bed Capacity for Ambulance and Patient Routing")

SCENES = [
    {"name": "Trip", "bar": "Mobility", "cues": [
        {"id": "1.1", "text": "Start with one trip, from Legazpi Grand Central Terminal to Tabaco City.",
         "onscreen": "A road from a terminal (A) in Legazpi to Tabaco City (B); a jeepney waits at A."},
        {"id": "1.2", "text": "Which jeepney do you ride, when do you arrive, and what do you pay?",
         "onscreen": "Three chips: \"Which jeepney?\", \"When do I arrive?\", \"How much?\"."},
        {"id": "1.3", "text": "In Albay, jeepneys, tricycles, buses, and UV Express vans publish no machine-readable routes, stops, or fares.",
         "onscreen": "Four vehicle cards; a red stamp \"NO ROUTE DATA\"."},
        {"id": "1.4", "text": "Many leave only when full, and since September 28, the base jeepney fare is 14 pesos for the first four kilometers.",
         "onscreen": "Fare card \"₱14.00 for the first 4 km · ₱2.00 per km after · 20% discount for students, seniors, PWD\". Source: Daguno-Bersamina, 2026 (LTFRB)."},
    ]},
    {"name": "Community", "bar": "Access", "cues": [
        {"id": "2.1", "text": "Zoom out to the whole province.",
         "onscreen": "Albay as a field of 720 barangay dots."},
        {"id": "2.2", "text": "Albay has 720 barangays and nearly 1.4 million people in 18 cities and municipalities.",
         "onscreen": "\"ALBAY · 18 cities and municipalities · 720 barangays · 1,379,398 residents\" (2024 Census, Proclamation No. 973, s. 2025)."},
        {"id": "2.3", "text": "Bicol is one of six regions where fewer than 80 percent of people live within two hours of a public hospital that can do essential surgery.",
         "onscreen": "Card \"Bicol: fewer than 80% within 2 hours of essential surgery\". Source: Lim et al., 2023."},
        {"id": "2.4", "text": "Target 11.2 asks for transport accessible to all, and Target 3.8 for health care people can use without hardship.",
         "onscreen": "Chips \"SDG 11.2 · accessible transport\" and \"SDG 3.8 · health care without hardship\"; \"SDG 10.2 · inclusion\"."},
        {"id": "2.5", "text": "In Albay, there was nothing to measure them against.",
         "onscreen": "The chips meet over an empty chart: \"no baseline data\"."},
    ]},
    {"name": "Patient", "bar": "Health", "cues": [
        {"id": "3.1", "text": "Now, an emergency.",
         "onscreen": "An ambulance with flashing light."},
        {"id": "3.2", "text": "The nearest hospital may be full, may lack the right level of care, or may cost more than the family can pay.",
         "onscreen": "Three hospitals: \"FULL\", \"Level 1 only\", \"₱₱₱\"."},
        {"id": "3.3", "text": "The Department of Health publishes where hospitals are and how many beds they have, but not which beds are free.",
         "onscreen": "Card \"Published: location, bed capacity · Not published: free beds\". Source: DOH Freedom of Information Unit, personal communication, September 22, 2026."},
        {"id": "3.4", "text": "So how does a crew know, in minutes, which hospital can take the patient?",
         "onscreen": "\"Right care · Free bed · Fair price · In minutes\" with a question mark."},
    ]},
    {"name": "How MCS comes into play", "bar": "MCS", "cues": [
        {"id": "4.1", "text": "This is where MCS comes into play.",
         "onscreen": "The letters M, C and S drop in and unfold into Mathematical, Computational, Sciences."},
        {"id": "4.2", "text": "Objective one: a timetable graph from open data that routes by arrival, fare, and transfers, within vehicle road limits.",
         "onscreen": "Panel OBJECTIVE 1 · TIMETABLE GRAPH; a time-expanded graph with ride, wait and transfer arcs; ten vehicle classes."},
        {"id": "4.3", "text": "Dijkstra's search gives the exact earliest arrival, and the regulated fare is proven monotone and subadditive.",
         "onscreen": "The earliest-arrival path lights gold; equations for the mean travel time and the regulated fare f(ℓ₁+ℓ₂) ≤ f(ℓ₁)+f(ℓ₂)."},
        {"id": "4.4", "text": "Objective two: measure who is left behind, with the Gini, Theil, and Palma measures, and split inequality within and between towns.",
         "onscreen": "Panel OBJECTIVE 2 · INEQUALITY; a Lorenz curve; cumulative accessibility and the exact Theil split; S1: 86.0% between municipalities."},
        {"id": "4.5", "text": "Objective three: e-mail agents gather bed reports, and an early-stopping search finds the nearest hospital that can take the patient.",
         "onscreen": "Panel OBJECTIVE 3 · HOSPITAL MODE; agents exchange tokened e-mails; the route skips the full hospital; suitability rule and nearest suitable hospital."},
        {"id": "4.6", "text": "In an emergency, payment never delays the route.",
         "onscreen": "Badge \"Acuity 1–2: payment filter off · payment gap = 0\" (RA 10932)."},
        {"id": "4.7", "text": "Objective four: MAP-A, one app that puts all of this on a phone, even without a signal.",
         "onscreen": "Panel OBJECTIVE 4 · THE APP; a phone with the MAP-A trip planner and hospital mode; \"offline\"."},
        {"id": "4.8", "text": "Twelve propositions, proven, then checked: 618 of 618 trips, 5,200 of 5,200 hospital queries, and all 200 forged replies rejected.",
         "onscreen": "Twelve green checks; cards 618/618 earliest-arrival queries, 5,200/5,200 hospital queries, 200/200 forged replies rejected."},
        {"id": "4.9", "text": "Fifteen of the sixteen app features work, and it runs with no connection at all.",
         "onscreen": "Cards 11,620 vehicle-class pairs, 0 violations · 15 of 16 checklist features working · runs offline."},
        {"id": "4.10", "text": "MAP-A will not add one bed to Albay.", "pause": 0.3,
         "onscreen": "Boom. Screen darkens; the line appears in white."},
        {"id": "4.11", "text": "But it will tell a rider what to ride and what to pay, and tell a crew which hospital can take the patient now.",
         "onscreen": "The line appears in gold."},
        {"id": "4.12", "text": "Distance tells you where the hospital is.",
         "onscreen": "\"Distance tells you where the hospital is.\" in white."},
        {"id": "4.13", "text": "Access tells you whether it can help in time.", "hold": 0.6,
         "onscreen": "\"Access tells you whether it can help in time.\" in gold."},
    ]},
]

CHAIN = ["Open data", "Timetable graph", "Dijkstra", "Inequality", "Hospital mode", "MAP-A"]
PRONOUNCE = ["MCS: \"M-C-S\", letter by letter", "MAP-A: \"Map A\"", "Dijkstra's: DIKE-struhz",
             "Theil: like \"tile\"", "Gini: JEE-nee", "Tabaco: tah-BAH-ko", "Albay: al-BYE", "jeepney: JEEP-nee",
             "Bicol: BEE-kol", "e-mail: EE-mail", "\"test instance\", never \"Albay\", for the S1 numbers",
             "₱ fares, sources and table values are shown on screen only."]


def wrap_title(text, size=46, maxw=1700):
    f = V.font(size, "SerifBold")
    lines, cur = [], ""
    for w in text.split():
        nxt = (cur + " " + w).strip()
        if f.getlength(nxt) > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = nxt
    return lines + [cur]


def jeepney(cv, x, y, s, a, col=(230, 60, 50)):
    """Side view of a jeepney, x,y = rear wheel contact point, s = length/4."""
    cv.rect((x - 0.4 * s, y - 1.25 * s, x + 3.6 * s, y - 0.35 * s), col, a, 10)
    cv.rect((x - 0.3 * s, y - 1.55 * s, x + 3.3 * s, y - 1.2 * s), (240, 240, 235), a, 8)
    for k in range(6):
        cv.rect((x - 0.1 * s + k * 0.5 * s, y - 1.12 * s, x + 0.3 * s + k * 0.5 * s, y - 0.78 * s), (60, 90, 120), a, 4)
    cv.rect((x - 0.4 * s, y - 0.7 * s, x + 3.6 * s, y - 0.58 * s), V.GOLD, a, 2)
    for wx in (x + 0.3 * s, x + 2.9 * s):
        cv.circle((wx, y - 0.3 * s), 0.32 * s, (30, 30, 30), a)
        cv.circle((wx, y - 0.3 * s), 0.14 * s, (180, 180, 180), a)


def hospital(cv, x, y, s, a, tag=None, tag_col=V.RED):
    cv.rect((x - s, y - s, x + s, y + s), V.CREAM, a, 14)
    cv.rect((x - 0.18 * s, y - 0.62 * s, x + 0.18 * s, y + 0.62 * s), V.RED, a, 3)
    cv.rect((x - 0.62 * s, y - 0.18 * s, x + 0.62 * s, y + 0.18 * s), V.RED, a, 3)
    if tag:
        w = V.font(26, "Bold").getlength(tag) + 28
        cv.rect((x - w / 2, y + s + 14, x + w / 2, y + s + 58), tag_col, a, 10)
        cv.ctext(x, y + s + 20, tag, 26, V.WHITE, a, "Bold")


def ambulance(cv, x, y, s, a, t=0.0):
    cv.rect((x, y - s, x + 2.4 * s, y), V.WHITE, a, 10)
    cv.rect((x + 2.4 * s, y - 0.7 * s, x + 3.1 * s, y), V.WHITE, a, 8)
    cv.rect((x + 2.5 * s, y - 0.62 * s, x + 2.95 * s, y - 0.32 * s), (60, 90, 120), a, 4)
    cv.rect((x + 0.95 * s, y - 0.8 * s, x + 1.35 * s, y - 0.2 * s), V.RED, a, 2)
    cv.rect((x + 0.85 * s, y - 0.7 * s, x + 1.45 * s, y - 0.3 * s), V.RED, a, 2)
    blink = 0.5 + 0.5 * math.sin(t * 12)
    cv.circle((x + 0.4 * s, y - 1.12 * s), 0.16 * s, (60, 120, 255), a * blink)
    for wx in (x + 0.55 * s, x + 2.45 * s):
        cv.circle((wx, y), 0.3 * s, (30, 30, 30), a)


def phone(cv, x0, y0, w, h, a, t):
    cv.rect((x0, y0, x0 + w, y0 + h), (20, 20, 24), a, 40)
    cv.rect((x0 + 14, y0 + 40, x0 + w - 14, y0 + h - 30), (236, 232, 222), a, 18)
    cv.rect((x0 + 14, y0 + 40, x0 + w - 14, y0 + 96), V.CRIMSON, a, 18)
    cv.text((x0 + 34, y0 + 52), "MAP-A", 30, V.WHITE, a, "Black")
    cv.text((x0 + w - 120, y0 + 58), "offline ✓", 20, V.GOLD_LT, a, "Bold")
    rnd = random.Random(3)
    pts = [(x0 + 40 + rnd.random() * (w - 80), y0 + 120 + rnd.random() * (h - 330)) for _ in range(9)]
    for p, q in zip(pts, pts[1:]):
        cv.line([p, q], (150, 140, 130), a, 4)
    route = pts[1:6]
    pr = V.clamp((t % 4.0) / 2.5)
    k = max(2, int(len(route) * pr) + 1)
    cv.line(route[:k], V.GOLD, a, 7)
    for p in pts:
        cv.circle(p, 7, V.CRIMSON, a)
    cv.rect((x0 + 30, y0 + h - 200, x0 + w - 30, y0 + h - 50), V.WHITE, a, 14)
    cv.text((x0 + 50, y0 + h - 188), "Terminal → Tabaco City", 22, V.INK, a, "Bold")
    cv.text((x0 + 50, y0 + h - 152), "jeepney · 1 transfer", 20, V.INK, a)
    cv.text((x0 + 50, y0 + h - 120), "fare and arrival time", 20, V.CRIMSON, a, "SemiBold")


class Spec:
    def __init__(self):
        self.scenes, end, self.clips = voiced.lay_out(SCENES, CACHE)
        self.title_start = end
        self.title = V.TitleCard(BRAND, wrap_title(TITLE), {
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
            "time": r"T(o,d,t)=\mathrm{EA}(o,d,t)-t,\qquad \bar T(o,d)=\frac{1}{|\Theta|}\sum_{t\in\Theta}T(o,d,t)",
            "fare": r"f(\ell)=b+r\,\max\{0,\lceil \ell-\ell_0\rceil\},\qquad f(\ell_1+\ell_2)\le f(\ell_1)+f(\ell_2)",
            "acc": r"A_a^{k}(\theta)=\sum_{d\in D_k} w_d\,\mathbf{1}\big[\bar T(a,d)\le\theta\big]",
            "theil": r"T=\underbrace{\textstyle\sum_g s_g T_g}_{\text{within}}+\underbrace{\textstyle\sum_g s_g\ln\frac{\bar x_g}{\bar x}}_{\text{between}}",
            "suit": r"h^{*}(o,p,t)=\arg\min_{h\in H_t(p)}\ \tau(o,h,t)",
            "hset": r"h\in H_t(p)\iff \ell_h\ge\lambda(a),\ \text{bed free},\ c_h\le\pi\ \text{or}\ a\in E",
        }
        self.eq = {k: V.latex_png(v, os.path.join(eqdir, k + ".png")) for k, v in tex.items()}

    def eqimg(self, key, height, maxw=780):
        im = V.scaled(self.eq[key], height=height)
        if im.size[0] > maxw:
            im = V.scaled(self.eq[key], width=maxw)
        return im

    def frac(self, cid, f):
        c = self.cue[cid]
        return c["start"] + f * (c["end"] - c["start"])

    def draw(self, cv, t, sc, lt):
        name = sc["name"]
        if name == "Trip":
            self.draw_trip(cv, t)
        elif name == "Community":
            self.draw_community(cv, t)
        elif name == "Patient":
            self.draw_patient(cv, t)
        else:
            self.draw_mcs(cv, t)

    def draw_trip(self, cv, t):
        c = self.cue
        s11, s12, s13, s14 = (c[k]["start"] for k in ("1.1", "1.2", "1.3", "1.4"))
        a = V.prog(t, s11 - 0.3, 0.6) * (1 - V.prog(t, s13 - 0.3, 0.3))
        if a > 0:
            road = [(220, 560), (520, 470), (820, 520), (1120, 400), (1420, 430), (1700, 300)]
            cv.line(road, (200, 190, 180), a, 14)
            cv.line(road, (90, 80, 80), a, 4)
            cv.circle(road[0], 30, V.GOLD, a)
            cv.ctext(road[0][0], road[0][1] - 18, "A", 32, V.INK, a, "Black")
            cv.circle(road[-1], 30, V.GOLD, a)
            cv.ctext(road[-1][0], road[-1][1] - 18, "B", 32, V.INK, a, "Black")
            cv.text((150, 700), "Legazpi Grand Central Terminal", 28, V.WHITE, a, "SemiBold")
            cv.text((1480, 230), "Tabaco City", 30, V.WHITE, a, "SemiBold")
            jeepney(cv, 260, 680, 46, a)
            a2 = V.prog(t, s12 - 0.1, 0.4)
            for i, q in enumerate(("Which jeepney?", "When do I arrive?", "How much?")):
                ai = V.prog(t, self.frac("1.2", 0.05 + 0.3 * i), 0.4) * a * (1 if a2 > 0 else 0)
                x0 = 560 + i * 420
                cv.card((x0, 640, x0 + 390, 730), ai, V.CREAM)
                cv.ctext(x0 + 195, 662, q, 34, V.CRIMSON, ai, "Bold")
        a3 = V.prog(t, s13 - 0.2, 0.5)
        if a3 > 0:
            for i, (nm, col) in enumerate((("Jeepney", (230, 60, 50)), ("Tricycle", (60, 140, 220)),
                                            ("Provincial bus", (240, 170, 40)), ("UV Express", (220, 220, 220)))):
                ai = V.prog(t, s13 + 0.25 * i, 0.4) * (1 - V.prog(t, s14 - 0.3, 0.3))
                x0 = 140 + i * 420
                cv.card((x0, 200, x0 + 380, 470), ai, (28, 10, 14))
                jeepney(cv, x0 + 100, 380, 44 if i != 1 else 32, ai, col)
                cv.ctext(x0 + 190, 400, nm, 32, V.WHITE, ai, "Bold")
            P.stamp(cv, 960, 560, "NO ROUTE DATA", V.prog(t, self.frac("1.3", 0.55), 0.3) * (1 - V.prog(t, s14 - 0.3, 0.3)), 60)
        a4 = V.prog(t, s14 - 0.2, 0.5)
        if a4 > 0:
            cv.card((360, 170, 1560, 780), a4, (28, 10, 14))
            cv.text((410, 205), "REGULATED FARE · FROM SEPTEMBER 28, 2026", 30, V.GOLD, a4, "Bold")
            cv.text((410, 270), "Traditional jeepney", 36, V.WHITE, a4, "SemiBold")
            cv.text((410, 330), "₱14.00", 120, V.GOLD_LT, V.prog(t, self.frac("1.4", 0.5), 0.4) * a4, "Black")
            cv.text((910, 380), "for the first 4 km", 40, V.WHITE, V.prog(t, self.frac("1.4", 0.6), 0.4) * a4, "SemiBold")
            cv.text((410, 500), "+ ₱2.00 for each kilometer after", 36, V.WHITE, V.prog(t, self.frac("1.4", 0.75), 0.4) * a4)
            cv.text((410, 560), "20% discount: students, senior citizens, persons with disabilities", 28, V.CREAM,
                    V.prog(t, self.frac("1.4", 0.85), 0.4) * a4)
            cv.text((410, 640), "Many vehicles leave the terminal only when full: no timetable.", 30, V.GOLD_LT,
                    V.prog(t, s14, 0.4) * a4, "SemiBold")
            cv.text((410, 720), "LTFRB, as reported by Daguno-Bersamina (2026), Philstar.com", 22, V.GREY, a4)

    def draw_community(self, cv, t):
        c = self.cue
        rnd = random.Random(5)
        a = V.prog(t, c["2.1"]["start"] - 0.2, 0.8)
        cx, cy = 520, 430
        for i in range(720):
            ang = rnd.random() * 2 * math.pi
            rr = math.sqrt(rnd.random())
            x = cx + math.cos(ang) * rr * 330 * (1 + 0.25 * math.sin(ang * 3))
            y = cy + math.sin(ang) * rr * 260
            if i / 720 <= a:
                cv.circle((x, y), 3.2, V.CREAM, 0.75)
        for k in range(14):
            p = (cx - 300 + k * 44, cy + 90 * math.sin(k * 0.7))
            q = (cx - 300 + (k + 1) * 44, cy + 90 * math.sin((k + 1) * 0.7))
            cv.line([p, q], V.GOLD, a * 0.7, 4)
        a2 = V.prog(t, c["2.2"]["start"] - 0.1, 0.5)
        cv.ctext(cx, 720, "ALBAY · 18 cities and municipalities · 720 barangays", 30, V.WHITE, a2, "SemiBold")
        cv.ctext(cx, 762, counter_s(1379398, V.prog(t, c["2.2"]["start"] + 0.3, 2.0)) + " residents", 40, V.GOLD_LT, a2, "Black")
        cv.ctext(cx, 812, "2024 Census of Population (Proclamation No. 973, s. 2025)", 20, V.GREY, a2)
        s24 = c["2.4"]["start"]
        a3 = V.prog(t, c["2.3"]["start"] - 0.1, 0.5) * (1 - V.prog(t, s24 - 0.3, 0.3))
        if a3 > 0:
            cv.card((980, 170, 1820, 640), a3, (28, 10, 14))
            cv.text((1015, 200), "BICOL REGION", 30, V.GOLD, a3, "Bold")
            cv.text((1015, 250), "fewer than", 34, V.WHITE, a3, "SemiBold")
            cv.text((1015, 300), "80%", 130, V.GOLD_LT, a3, "Black")
            cv.para((1015, 450), "live within a 2-hour drive of a public hospital that can perform essential surgery",
                    32, 760, V.WHITE, a3, "SemiBold", 1.2)
            cv.text((1015, 590), "Lim et al., 2023, BMJ Open", 20, V.GREY, a3)
        a4 = V.prog(t, s24 - 0.1, 0.5)
        if a4 > 0:
            for i, (g, sub, col) in enumerate((("SDG 11.2", "transport accessible to all", V.BLUE),
                                               ("SDG 3.8", "health care without hardship", V.GREEN),
                                               ("SDG 10.2", "inclusion of all", V.GOLD))):
                P.chip(cv, 1000, 170 + i * 150, g, sub, V.prog(t, s24 + 0.35 * i, 0.4), col, 640)
            a5 = V.prog(t, c["2.5"]["start"] - 0.1, 0.5)
            cv.rect((1000, 640, 1640, 800), (20, 6, 10), 0.85 * a5, 14)
            cv.line([(1040, 770), (1600, 770)], V.GREY, a5, 3)
            cv.line([(1040, 670), (1040, 770)], V.GREY, a5, 3)
            cv.ctext(1320, 690, "no baseline data for Albay", 34, V.GOLD_LT, a5, "Bold")

    def draw_patient(self, cv, t):
        c = self.cue
        s31, s32, s33, s34 = (c[k]["start"] for k in ("3.1", "3.2", "3.3", "3.4"))
        a = V.prog(t, s31 - 0.2, 0.5) * (1 - V.prog(t, s33 - 0.3, 0.3))
        if a > 0:
            mv = V.prog(t, s31, s33 - s31)
            ambulance(cv, 150 + 260 * mv, 700, 70, a, t)
            cv.line([(140, 712), (1800, 712)], (120, 110, 110), a, 4)
            tags = [("FULL", V.RED), ("Level 1 only", (200, 120, 40)), ("₱₱₱", (150, 80, 160))]
            for i, (tag, col) in enumerate(tags):
                ai = V.prog(t, self.frac("3.2", 0.1 + 0.28 * i), 0.4) * a
                hospital(cv, 760 + i * 380, 420, 90, ai, tag, col)
        a3 = V.prog(t, s33 - 0.2, 0.5) * (1 - V.prog(t, s34 - 0.3, 0.3))
        if a3 > 0:
            cv.card((260, 160, 1660, 790), a3, (28, 10, 14))
            cv.text((310, 196), "WHAT THE DEPARTMENT OF HEALTH PUBLISHES", 30, V.GOLD, a3, "Bold")
            rows = [("Location of every facility", True), ("Authorized or average bed capacity", True),
                    ("Licensed service level", True), ("Which beds are free right now", False)]
            for i, (txt, ok) in enumerate(rows):
                ai = V.prog(t, self.frac("3.3", 0.1 + 0.2 * i), 0.4) * a3
                y = 270 + i * 100
                col = V.GREEN if ok else V.RED
                cv.circle((340, y + 26), 26, col, ai)
                cv.ctext(340, y + 4, "✓" if ok else "✕", 36, V.WHITE, ai, "Black")
                cv.text((390, y + 4), txt, 40, V.WHITE if ok else V.GOLD_LT, ai, "SemiBold")
            cv.text((310, 720), "DOH Freedom of Information Unit, personal communication, September 22, 2026", 22, V.GREY, a3)
        a4 = V.prog(t, s34 - 0.1, 0.4)
        if a4 > 0:
            cv.rect((0, 0, V.W, V.H), (0, 0, 0), 0.82 * a4)
            for i, (s, col) in enumerate((("Right care", V.WHITE), ("Free bed", V.GOLD_LT),
                                          ("Fair price", V.GOLD), ("In minutes", V.WHITE))):
                cv.ctext(V.W / 2, 160 + i * 120, s, 76, col, V.prog(t, self.frac("3.4", 0.1 + 0.2 * i), 0.4), "Black")
            cv.ctext(V.W / 2, 650, "?", 110, V.WHITE, V.prog(t, self.frac("3.4", 0.9), 0.4), "Black")

    def draw_mcs(self, cv, t):
        c = self.cue
        s = {k: c[k]["start"] for k in c if k.startswith("4.")}
        if t < s["4.2"] - 0.2:
            P.mcs_reveal(cv, t - s["4.1"] + 0.2)
            return
        if t >= s["4.10"] - 0.4:
            self.closing(cv, t, s)
            return
        lit = sum(V.prog(t, st, 0.5) for st in (s["4.2"] - 0.2, s["4.2"] + 1.0, s["4.3"], s["4.4"], s["4.5"], s["4.7"]))
        P.chain(cv, CHAIN, lit, 40)
        a_mcs = 1 - V.prog(t, s["4.2"], 0.4)
        if a_mcs > 0:
            P.mcs_reveal(cv, t - s["4.1"] + 0.2, alpha=a_mcs)
        left, right = (90, 150, 920, 840), (980, 150, 1830, 840)
        blocks = [("4.2", "4.4", self.obj1), ("4.4", "4.5", self.obj2), ("4.5", "4.7", self.obj3),
                  ("4.7", "4.8", self.obj4), ("4.8", "4.10", self.proof)]
        for k0, k1, fn in blocks:
            if s[k0] - 0.2 <= t < s[k1] - 0.2:
                a1 = V.prog(t, s[k0] - 0.2, 0.5) * (1 - V.prog(t, s[k1] - 0.5, 0.3))
                fn(cv, t, a1, s, left, right)

    def head(self, cv, box, n, title, a1):
        P.panel(cv, box, "OBJECTIVE %d" % n, a1)
        cv.text((box[0] + 40, 226), title, 40, V.GOLD_LT, a1, "Black")

    def obj1(self, cv, t, a1, s, left, right):
        P.panel(cv, left, "TIME-EXPANDED GRAPH", a1)
        cols = [200, 380, 560, 740]
        names = ["Stop 1", "Stop 2", "Stop 3", "Stop 4"]
        for i, x in enumerate(cols):
            cv.ctext(x, 220, names[i], 24, V.WHITE, a1, "SemiBold")
            cv.line([(x, 260), (x, 800)], V.GREY, a1 * 0.6, 3)
            for k in range(7):
                cv.circle((x, 280 + k * 80), 8, V.CREAM, a1)
        rides = [((0, 0), (1, 1)), ((1, 1), (2, 2)), ((2, 2), (3, 3)), ((0, 2), (1, 3)), ((1, 3), (2, 4)),
                 ((2, 4), (3, 5)), ((0, 4), (1, 5)), ((1, 5), (2, 6)), ((2, 1), (3, 2))]
        rv = V.prog(t, s["4.2"] + 0.5, 2.0)
        for i, ((c0, r0), (c1, r1)) in enumerate(rides):
            if i / len(rides) <= rv:
                cv.line([(cols[c0], 280 + r0 * 80), (cols[c1], 280 + r1 * 80)], (230, 200, 120), a1 * 0.8, 4)
        ag = V.prog(t, self.frac("4.3", 0.1), 0.8) * a1
        best = [(cols[0], 280), (cols[1], 360), (cols[2], 440), (cols[3], 520)]
        cv.line(best, V.GOLD, ag, 9)
        cv.text((560, 760), "earliest arrival", 26, V.GOLD, ag, "Bold")
        self.head(cv, right, 1, "Timetable graph from open data", a1)
        rows = ["departures from estimated headways", "road limits for 10 vehicle classes",
                "routes by arrival, fare and transfers", "2026 regulated fares, 20% discount"]
        for i, txt in enumerate(rows):
            ai = V.prog(t, self.frac("4.2", 0.2 + 0.15 * i), 0.4) * a1 * (1 - V.prog(t, s["4.3"] - 0.3, 0.3))
            cv.circle((1040, 330 + i * 70), 10, V.GOLD, ai)
            cv.text((1066, 312 + i * 70), txt, 32, V.WHITE, ai, "SemiBold")
        ae = V.prog(t, s["4.3"] - 0.1, 0.5) * a1
        cv.text((1020, 310), "Dijkstra: exact earliest arrival", 32, V.GOLD_LT, ae, "Bold")
        cv.paste(self.eqimg("time", 70), (1020, 370), ae)
        cv.text((1020, 520), "regulated fare: monotone and subadditive", 32, V.GOLD_LT, V.prog(t, self.frac("4.3", 0.5), 0.5) * a1, "Bold")
        cv.paste(self.eqimg("fare", 50), (1020, 580), V.prog(t, self.frac("4.3", 0.55), 0.5) * a1)

    def obj2(self, cv, t, a1, s, left, right):
        P.panel(cv, left, "LORENZ CURVE · TEST INSTANCE S1", a1)
        gx0, gy0, gx1, gy1 = 180, 240, 820, 780
        cv.line([(gx0, gy1), (gx1, gy1)], V.GREY, a1, 3)
        cv.line([(gx0, gy0), (gx0, gy1)], V.GREY, a1, 3)
        cv.line([(gx0, gy1), (gx1, gy0)], V.WHITE, a1 * 0.5, 2)
        pc = V.prog(t, s["4.4"] + 0.4, 2.0)
        pts = []
        for k in range(41):
            u = k / 40
            if u > pc:
                break
            pts.append((gx0 + (gx1 - gx0) * u, gy1 - (gy1 - gy0) * u ** 2.2))
        if len(pts) > 1:
            cv.line(pts, V.GOLD, a1, 6)
        cv.text((gx0 + 20, gy0 - 10), "share of reachable beds", 22, V.WHITE, a1)
        cv.text((gx1 - 300, gy1 + 10), "share of anchor weight", 22, V.WHITE, a1)
        self.head(cv, right, 2, "Who is left behind", a1)
        cv.paste(self.eqimg("acc", 54), (1020, 300), V.prog(t, s["4.4"] + 0.4, 0.5) * a1)
        for i, (k, v) in enumerate((("Gini", "how unequal"), ("Theil", "splits exactly"), ("Palma", "top 10% vs bottom 40%"))):
            ai = V.prog(t, self.frac("4.4", 0.3 + 0.1 * i), 0.4) * a1
            x0 = 1020 + i * 265
            cv.rect((x0, 400, x0 + 245, 490), (40, 16, 20), ai, 14)
            cv.text((x0 + 18, 408), k, 34, V.GOLD_LT, ai, "Black")
            cv.text((x0 + 18, 452), v, 20, V.WHITE, ai)
        cv.paste(self.eqimg("theil", 80), (1020, 520), V.prog(t, self.frac("4.4", 0.65), 0.5) * a1)
        cv.text((1020, 700), "S1: 86.0% of the inequality lies between municipalities", 26, V.WHITE,
                V.prog(t, self.frac("4.4", 0.8), 0.5) * a1, "SemiBold")

    def obj3(self, cv, t, a1, s, left, right):
        P.panel(cv, left, "HOSPITAL MODE · TEST INSTANCE S1", a1)
        hs = [(300, 330, "S3", "FULL", V.RED), (700, 340, "S7", "Level 2 · private", (150, 80, 160)),
              (520, 650, "S4", "Level 3 · 8 free", V.GREEN)]
        for x, y, nm, tag, col in hs:
            hospital(cv, x, y, 50, a1, tag, col)
            cv.ctext(x, y - 92, nm, 26, V.WHITE, a1, "Bold")
        ax, ay = 170, 560
        ambulance(cv, ax - 60, ay + 30, 34, a1, t)
        pr = V.prog(t, self.frac("4.5", 0.55), 1.5)
        cv.line([(ax, ay), (ax + (470 - ax) * pr, ay + (650 - ay) * pr)], V.GOLD, a1, 8)
        cv.line([(ax, ay), (300, 390)], V.GREY, a1 * 0.6, 3)
        ae = V.prog(t, self.frac("4.5", 0.1), 0.6) * a1
        for k in range(5):
            ph = (t * 0.6 + k * 0.2) % 1.0
            cv.rect((560 + 120 * ph, 470, 590 + 120 * ph, 490), V.CREAM, ae * (1 - abs(ph - 0.5) * 2), 3)
        cv.text((540, 500), "tokened e-mail reports", 22, V.CREAM, ae)
        self.head(cv, right, 3, "Nearest suitable hospital", a1)
        cv.paste(self.eqimg("suit", 56), (1020, 300), V.prog(t, s["4.5"] + 0.3, 0.5) * a1)
        cv.paste(self.eqimg("hset", 40), (1020, 390), V.prog(t, self.frac("4.5", 0.45), 0.5) * a1)
        rows = ["agents: at most 2 e-mails per shift, opt-outs honored", "early stopping: exact, settles 5.2% of",
                "vertices on a 16,000-vertex graph"]
        for i, txt in enumerate(rows):
            ai = V.prog(t, self.frac("4.5", 0.6 + 0.1 * i), 0.4) * a1
            cv.text((1020, 470 + i * 46), txt, 28, V.WHITE, ai, "SemiBold")
        a6 = V.prog(t, s["4.6"] - 0.1, 0.4) * a1
        if a6 > 0:
            cv.rect((1020, 640, 1800, 800), V.CRIMSON, a6, 16)
            cv.text((1046, 656), "EMERGENCY · acuity 1–2", 34, V.GOLD_LT, a6, "Black")
            cv.text((1046, 708), "payment filter off · payment gap = 0", 30, V.WHITE, a6, "SemiBold")
            cv.text((1046, 752), "Anti-Hospital Deposit Law (RA 10932)", 22, V.CREAM, a6)

    def obj4(self, cv, t, a1, s, left, right):
        P.panel(cv, left, "MAP-A", a1)
        phone(cv, 330, 190, 360, 640, a1, t)
        self.head(cv, right, 4, "One app, even offline", a1)
        rows = ["trip planner: fastest, fewest transfers, cheapest", "fare for regular, student, senior, PWD",
                "landmark accessibility with a time slider", "hospital mode with a 911 button",
                "all 18 cities and municipalities", "opens with no connection"]
        for i, txt in enumerate(rows):
            ai = V.prog(t, self.frac("4.7", 0.15 + 0.12 * i), 0.4) * a1
            cv.circle((1040, 330 + i * 70), 10, V.GOLD, ai)
            cv.text((1066, 312 + i * 70), txt, 30, V.WHITE, ai, "SemiBold")

    def proof(self, cv, t, a1, s, left, right):
        cv.ctext(V.W / 2, 170, "12 propositions, proven, then verified", 64, V.WHITE, a1, "Black")
        P.proof_marks(cv, 12, V.W / 2 - 11 * 34, 290, t, s["4.8"] + 0.2, 0.12, 46)
        stats = [("4.8", "618 / 618", "earliest-arrival queries matched enumeration"),
                 ("4.8", "5,200 / 5,200", "hospital queries matched the references"),
                 ("4.8", "200 / 200", "forged e-mail replies rejected"),
                 ("4.9", "11,620", "vehicle-class pairs, 0 violations"),
                 ("4.9", "1,000 / 1,000", "fare splits subadditive"),
                 ("4.9", "15 of 16", "app features working; runs offline")]
        for i, (cid, big, small) in enumerate(stats):
            ai = V.prog(t, self.frac(cid, 0.25 + 0.2 * (i % 3)), 0.4) * a1
            x0 = 130 + (i % 3) * 570
            y0 = 380 + (i // 3) * 220
            cv.card((x0, y0, x0 + 530, y0 + 190), ai, (28, 10, 14))
            cv.text((x0 + 30, y0 + 24), big, 60, V.GOLD, ai, "Black")
            cv.para((x0 + 30, y0 + 108), small, 26, 470, V.WHITE, ai, "SemiBold", 1.15)
        cv.ctext(V.W / 2, 830, "synthetic instances and a simulated mail server · no real hospital or patient", 22, V.GREY, a1)

    def closing(self, cv, t, s):
        cv.rect((0, 0, V.W, V.H), (0, 0, 0), 0.5)
        a1 = V.prog(t, s["4.10"] - 0.2, 0.4) * (1 - V.prog(t, s["4.11"] - 0.4, 0.3))
        cv.para((V.W / 2, 380), "MAP-A will not add one bed to Albay.", 74, 1500, V.WHITE, a1, "Bold", 1.2, "center")
        a2 = V.prog(t, s["4.11"] - 0.2, 0.4) * (1 - V.prog(t, s["4.12"] - 0.4, 0.3))
        cv.para((V.W / 2, 300), "But it will tell a rider what to ride and what to pay, and tell a crew which hospital can take the patient now.",
                60, 1500, V.GOLD, a2, "Bold", 1.25, "center")
        a3 = V.prog(t, s["4.12"] - 0.2, 0.4)
        a4 = V.prog(t, s["4.13"] - 0.2, 0.4)
        cv.para((V.W / 2, 300), "Distance tells you where the hospital is.", 64, 1600, V.WHITE, a3, "Bold", 1.2, "center")
        cv.para((V.W / 2, 470), "Access tells you whether it can help in time.", 64, 1600, V.GOLD, a4, "Bold", 1.2, "center")


def counter_s(v, p):
    return "{:,}".format(int(round(v * V.ease(p))))


def main():
    spec = Spec()
    V.save_timeline(spec, os.path.join(HERE, "timeline.json"))
    print("length %.1f s, title at %.1f s, boom %.1f s" % (spec.total, spec.title_start, spec.boom_t))
    os.makedirs(OUT, exist_ok=True)
    if "--preview" in sys.argv:
        pdir = os.path.join(OUT, "_preview")
        os.makedirs(pdir, exist_ok=True)
        times = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1:]]
        if not times:
            for sc in spec.scenes:
                for cu in sc["cues"]:
                    times.append(cu["start"] + 0.8 * (cu["end"] - cu["start"]))
            times += [spec.title_start + 6]
        V.render(spec, pdir, "x.mp4", only=[int(x * V.FPS) for x in times])
        return
    out = V.render(spec, OUT, NAME)
    voiced.narrated(spec, spec.clips, out, os.path.join(OUT, NAME_VO), BRAND)
    img, _ = spec.title.draw(7.0)
    img.save(os.path.join(OUT, "MAP-A_Title_Page_1920x1080.png"))
    img.resize((3840, 2160), Image.LANCZOS).save(os.path.join(OUT, "MAP-A_Title_Page_3840x2160.png"))
    print(out)


if __name__ == "__main__":
    main()

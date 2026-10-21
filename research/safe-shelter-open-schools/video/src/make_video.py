"""LIGTA-S rationale video v2: typhoons by wind signal and forecast track, the revised
objectives, and the model's results. The timing follows the spoken narration, so the
picture, the subtitles and the voice move together with no dead air.

Run:  python3 make_video.py            -> ../LIGTA-S_Rationale_Video_v2_MCS_No_Narration.mp4
                                          ../LIGTA-S_Rationale_Video_v2_MCS_Narrated.mp4
      python3 make_video.py --preview  -> still frames for checking
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
import voiced  # noqa: E402
from PIL import Image  # noqa: E402

BRAND = "LIGTA-S"
OUT = os.path.join(PROJ, "video")
NAME = "LIGTA-S_Rationale_Video_v2_MCS_No_Narration.mp4"
NAME_VO = "LIGTA-S_Rationale_Video_v2_MCS_Narrated.mp4"
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "kokoro", "clips")
RES = json.load(open(os.path.join(PROJ, "code", "results.json")))
E1 = RES["e1"]
VER = RES["verification"]
AL3 = E1["scenarios"]["AL3"]
AL4L = E1["scenarios"]["AL4+L"]
CHAN = E1["channel_closures"]
SIT = E1["siting"]["rows"]

# PAGASA Tropical Cyclone Wind Signals (2022): wind range (km/h) and lead time (h)
TCWS = [(1, "39–61 km/h", "36 h", (240, 200, 60)), (2, "62–88 km/h", "24 h", (240, 150, 40)),
        (3, "89–117 km/h", "18 h", (230, 95, 40)), (4, "118–184 km/h", "12 h", (205, 40, 40)),
        (5, "185 km/h or more", "12 h", (150, 20, 95))]

SCENES = [
    {"name": "Storm", "bar": "Warning", "cues": [
        {"id": "1.1", "text": "A typhoon is coming, and PAGASA draws its forecast track toward Albay.",
         "onscreen": "Map of Bicol at sea level; a typhoon spiral moves in from the Pacific along a dotted forecast track with a widening cone; forecast points +12 h, +24 h, +36 h."},
        {"id": "1.2", "text": "Along the track, PAGASA raises wind signals, from Signal No. 1 up to Signal No. 5.",
         "onscreen": "Signal rings 1 to 5 open around the forecast landfall; the ladder of the five Tropical Cyclone Wind Signals builds on the right (wind range per signal)."},
        {"id": "1.3", "text": "Each signal comes with a lead time: thirty-six hours at Signal No. 1, but only twelve at Signal No. 4 or 5.",
         "onscreen": "The lead-time column lights up: 36 h, 24 h, 18 h, 12 h, 12 h. Source: PAGASA Tropical Cyclone Wind Signals (2022)."},
        {"id": "1.4", "text": "Families must leave before the winds arrive. But where do they go, and is there room for Lola?",
         "onscreen": "A family of four by their house; bubbles \"Where do we go?\" and \"Room for Lola?\"."},
    ]},
    {"name": "Community", "bar": "Learning", "cues": [
        {"id": "2.1", "text": "Albay has lived through this before.",
         "onscreen": "Albay as a field of 720 barangay dots; Mayon at the centre. PSA 2020 census."},
        {"id": "2.2", "text": "In 2006, Typhoon Reming sent lahar down Mayon, and about 1,200 people were dead or missing.",
         "onscreen": "Card: \"November 2006 · Typhoon Reming (Durian) · lahar from Mayon's old deposits · about 1,200 dead and missing\". Source: Philippine Daily Inquirer, 2016."},
        {"id": "2.3", "text": "In 2020, Super Typhoon Rolly made landfall in Albay under Signal No. 5.",
         "onscreen": "Card: \"November 2020 · Super Typhoon Rolly (Goni) · landfall in Tiwi, Albay · Signal No. 5\". Source: PAGASA, 2020."},
        {"id": "2.4", "text": "And when Mayon rose to Alert Level 3 in January 2026, four schools became evacuation centers, and 3,424 learners were affected.",
         "onscreen": "Card: \"January 2026 · 4 schools became evacuation centers · 3,424 learners affected\". Source: Philippine Daily Inquirer, 2026."},
        {"id": "2.5", "text": "The law makes schools a last resort. Goals 4, 11, and 13 meet in the same classroom.",
         "onscreen": "Chips SDG 4.a, SDG 11.5 and SDG 13.1 meet over one classroom; \"RA 10821: schools are evacuation centers only as a last resort\"."},
    ]},
    {"name": "Stakes", "bar": "Time", "cues": [
        {"id": "3.1", "text": "As the track shifts, the plan must shift too: which zones leave, and which roads close.",
         "onscreen": "Badge \"SIGNAL NO. 4\"; a lead-time clock counts down from 12 h; test network E1 with its hazard zones."},
        {"id": "3.2", "text": "Heavy rain sends lahar down the river channels and closes the bridges.",
         "onscreen": "Lahar channels A and B cut across the road ring; bridges A1 to A4 and B1 to B3 turn red with a cross."},
        {"id": "3.3", "text": "Send everyone to the nearest site, and families arrive at shelters that are already full.",
         "onscreen": "Arrows to the nearest shelters; counter \"898 arrive at full shelters\" (test network E1, Alert Level 4 with typhoon lahar)."},
        {"id": "3.4", "text": "So how do we shelter everyone before the lead time runs out, the vulnerable first, and classrooms last?",
         "onscreen": "\"Everyone sheltered · Vulnerable first · Classrooms last · Before the lead time ends\" with a question mark."},
    ]},
    {"name": "How MCS comes into play", "bar": "MCS", "cues": [
        {"id": "4.1", "text": "This is where MCS comes into play.",
         "onscreen": "The letters M, C and S drop in and unfold into Mathematical, Computational, Sciences."},
        {"id": "4.2", "text": "Objective one: turn the signal and the forecast track into a hazard scenario, the zones that must leave and the roads that close.",
         "onscreen": "Panel OBJECTIVE 1 · SCENARIO: σ = (Z_σ, X_σ); signal + track → zones (lahar, flood, storm surge) and closed roads; test network E1 with closed bridges."},
        {"id": "4.3", "text": "Objective two: write the law's order as one lexicographic minimum-cost flow: vulnerable first, everyone next, classrooms last.",
         "onscreen": "Panel OBJECTIVE 2 · SHELTER PLAN: three shelter tiers, the lexicographic objective and its penalties; evacuee flows animate."},
        {"id": "4.4", "text": "Objective three: compute the exact clearance time on a time-expanded network, and check it against the signal's lead time.",
         "onscreen": "Panel OBJECTIVE 3 · CLEARANCE TIME: T* = min{T : F(T) = D}; T* ≤ lead time; arrival curve F(T)."},
        {"id": "4.5", "text": "Objective four: find the bridges to protect before landfall, and site new Ligtas Pinoy Centers with a proven guarantee.",
         "onscreen": "Panel OBJECTIVE 4 · BRIDGES AND CENTERS: Δ_B = T*(σ + B) − T*(σ) ≥ 0; f(S_g) ≥ (1 − 1/e) f(S*); the new center lights up."},
        {"id": "4.6", "text": "Objective five: prove every result, then verify it against independent code.",
         "onscreen": "Panel OBJECTIVE 5 · PROOF: ten proof marks turn into checks."},
        {"id": "4.7", "text": "On the test network, losing one lahar channel's bridges stretches the clearance time from 53 to 95 minutes.",
         "onscreen": "Card 1: \"Clearance time 53 → 95 min · lahar channel A closed · protect it first\" (test network E1, synthetic)."},
        {"id": "4.8", "text": "With typhoon rain on an eruption, 450 people are cut off, and one new center reaches 400 of them.",
         "onscreen": "Card 2: \"450 cut off → one new Ligtas Pinoy Center reaches 400\"."},
        {"id": "4.9", "text": "At Alert Level 3, the plan closes fourteen classrooms instead of forty.",
         "onscreen": "Card 3: \"Classrooms closed 40 → 14 · learners displaced 1,702 → 532\"."},
        {"id": "4.10", "text": "Ten results, proven, then verified against independent code.",
         "onscreen": "Ten green checks; 300/300 plans, 660/660 networks, 4,796 checks, 0 violations."},
        {"id": "4.11", "text": "LIGTA-S will not stop a typhoon.", "pause": 0.3,
         "onscreen": "Boom. Screen darkens; the line appears in white."},
        {"id": "4.12", "text": "But before landfall, it will tell every family where to go, in time, and keep the most classrooms open.",
         "onscreen": "The line appears in gold."},
        {"id": "4.13", "text": "A signal tells you the storm is coming.",
         "onscreen": "\"A signal tells you the storm is coming.\" in white."},
        {"id": "4.14", "text": "A plan tells you if there is room, in time.", "hold": 0.6,
         "onscreen": "\"A plan tells you if there is room, in time.\" in gold."},
    ]},
]

TITLE_LINES = ["Safe Shelter, Open Schools: A Verified Network-Flow Model",
               "for Planning Evacuations in Albay by Hazard Zone, Shelter Capacity,",
               "and Vulnerability While Keeping Classrooms Open"]

CHAIN = ["Signal + track", "Scenario", "Flow", "Clearance", "Siting", "Proof"]
PRONOUNCE = ["MCS: \"M-C-S\", letter by letter", "LIGTA-S: \"LIG-tas\", like the Filipino word for safe",
             "PAGASA: pag-A-sa", "Signal No. 4: \"Signal Number Four\"", "Reming: REH-ming", "Mayon: mah-YON",
             "Albay: al-BYE", "lahar: LAH-har", "Lola: LOH-lah",
             "\"test network\", never \"Albay\", for the E1 numbers", "Wind ranges, sources and table values are shown on screen only."]

# Bicol map (screen coordinates inside the map panel)
LAND = [(120, 250), (260, 228), (380, 296), (500, 352), (640, 410), (760, 492), (860, 594), (900, 694),
        (842, 762), (720, 722), (600, 646), (470, 592), (330, 520), (200, 430), (120, 350)]
ALBAY = [(505, 438), (640, 426), (762, 506), (782, 600), (664, 642), (540, 602), (478, 520)]
CATAN = [(905, 370), (972, 352), (996, 420), (958, 474), (912, 446)]
TRACK = [(1160, 190), (1040, 290), (950, 400), (800, 500), (640, 548), (430, 612), (200, 668)]


def track_at(s):
    """Point at fraction s (0..1) of the polyline TRACK."""
    segs = list(zip(TRACK[:-1], TRACK[1:]))
    lens = [math.dist(a, b) for a, b in segs]
    d = s * sum(lens)
    for (a, b), L in zip(segs, lens):
        if d <= L:
            f = d / L
            return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        d -= L
    return TRACK[-1]


def typhoon(cv, x, y, r, t, alpha):
    """Spiral cloud bands around an eye, turning counterclockwise."""
    if alpha <= 0:
        return
    cv.circle((x, y), r * 1.05, (235, 240, 250), alpha * 0.10)
    for arm in range(3):
        pts = []
        for k in range(34):
            ang = -t * 2.2 + arm * 2 * math.pi / 3 + k * 0.17
            rr = r * (0.18 + 0.82 * k / 33)
            pts.append((x + rr * math.cos(ang), y - rr * math.sin(ang)))
        cv.line(pts, (240, 244, 252), alpha * 0.85, 9)
    cv.circle((x, y), r * 0.16, (30, 40, 60), alpha, outline=(240, 244, 252), width=3)


class Spec:
    def __init__(self):
        self.scenes, end, self.clips = voiced.lay_out(SCENES, CACHE)
        self.title_start = end
        self.title = V.TitleCard(BRAND, TITLE_LINES, {
            "building": os.path.join(ROOT, "tools", "assets", "school_building.png"),
            "seal": os.path.join(ROOT, "tools", "assets", "legasci_seal.png")})
        self.total = end + self.title.dur
        self.base = V.make_background()
        self.cue = {c["id"]: c for sc in self.scenes for c in sc["cues"]}
        self.mcs_start = self.cue["4.1"]["start"]
        self.boom_t = self.cue["4.11"]["start"] - 0.25
        eqdir = os.path.join(HERE, "eq")
        os.makedirs(eqdir, exist_ok=True)
        tex = {
            "scen": r"\sigma=(Z_\sigma,\,X_\sigma)\qquad \text{signal}+\text{track}\ \longmapsto\ \sigma",
            "tiers": r"\text{cap}_s=\Big\lfloor \tfrac{F_s}{3.5\,\text{m}^2}\Big\rfloor,\qquad K_s=\Big\lceil \tfrac{y_s}{18}\Big\rceil",
            "lex": r"\max V\ \succ\ \max D\ \succ\ \min Y\ \succ\ \min O\ \succ\ \min \textstyle\sum_e \tau_e x_e",
            "pen": r"M_O = D\,T_{\max}+1,\qquad M_Y = D\,(M_O+T_{\max})+1",
            "tstar": r"T^{*}=\min\{\,T : F(T)=D\,\}",
            "lead": r"T^{*}(\sigma)\ \le\ L_{\text{signal}}",
            "delta": r"\Delta_B=T^{*}(\sigma+B)-T^{*}(\sigma)\ \ge\ 0",
            "greedy": r"f(S_g)\ \ge\ \Big(1-\tfrac{1}{e}\Big)\,f(S^{*})\ \approx\ 0.632\,f(S^{*})",
        }
        self.eq = {k: V.latex_png(v, os.path.join(eqdir, k + ".png")) for k, v in tex.items()}
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
        return (x0 + x1) / 2 + x * s, (y0 + y1) / 2 - y * s

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
        cx = (self.net_xy("R0", box)[0] + self.net_xy("R6", box)[0]) / 2
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

    def frac(self, cid, f):
        """Time at fraction f of a cue's spoken line."""
        c = self.cue[cid]
        return c["start"] + f * (c["end"] - c["start"])

    # scenes ----------------------------------------------------------------
    def draw(self, cv, t, sc, lt):
        name = sc["name"]
        if name == "Storm":
            self.draw_storm(cv, t, sc)
        elif name == "Community":
            self.draw_community(cv, t)
        elif name == "Stakes":
            self.draw_stakes(cv, t)
        else:
            self.draw_mcs(cv, t)

    def draw_storm(self, cv, t, sc):
        c = self.cue
        s11, s12, s13, s14 = (c[k]["start"] for k in ("1.1", "1.2", "1.3", "1.4"))
        am = V.prog(t, s11 - 0.3, 0.6) * (1 - V.prog(t, s14 - 0.3, 0.4))
        if am > 0:
            cv.rect((90, 110, 1190, 840), (14, 30, 52), am, 24)
            cv.text((120, 130), "PACIFIC OCEAN", 22, (150, 180, 210), am * 0.8, "SemiBold")
            cv.poly(LAND, (70, 96, 70), am)
            cv.poly(CATAN, (70, 96, 70), am)
            cv.text((880, 486), "Catanduanes", 20, (210, 220, 210), am * 0.8)
            cv.poly(ALBAY, (110, 130, 80), am, outline=V.GOLD, width=4)
            cv.text((560, 652), "ALBAY", 30, V.GOLD_LT, am, "Bold")
            cv.text((170, 300), "BICOL", 26, (210, 220, 210), am * 0.8, "Bold")
            P.volcano(cv, 625, 540, 26, am, t)
            # forecast track, cone and forecast points
            pos = 0.05 + 0.30 * V.prog(t, s11, s14 - s11)
            pts = [track_at(pos + (1 - pos) * k / 40) for k in range(41)]
            left, right = [], []
            for k in range(40):
                (x0, y0), (x1, y1) = pts[k], pts[k + 1]
                L = math.hypot(x1 - x0, y1 - y0) or 1
                nx, ny = -(y1 - y0) / L, (x1 - x0) / L
                w = 14 + 150 * k / 40
                left.append((x0 + nx * w, y0 + ny * w))
                right.append((x0 - nx * w, y0 - ny * w))
            ac = V.prog(t, s11 + 0.8, 0.8) * am
            cv.poly(left + right[::-1], (220, 230, 250), ac * 0.13)
            for k in range(0, 40, 2):
                cv.line([pts[k], pts[k + 1]], V.WHITE, ac * 0.9, 3)
            for f, lab in ((0.52, "+12 h"), (0.68, "+24 h"), (0.84, "+36 h")):
                x, y = track_at(f)
                cv.circle((x, y), 8, V.WHITE, ac)
                cv.text((x + 12, y - 40), lab, 22, V.WHITE, ac, "SemiBold")
            # wind-signal rings around the forecast landfall
            lx, ly = track_at(0.68)
            for i, (n, wind, lead, col) in enumerate(TCWS):
                ai = V.prog(t, s12 + 0.5 + 0.35 * i, 0.4) * am
                cv.circle((lx, ly), 250 - 45 * i, col, ai * 0.22, outline=col, width=3)
            x, y = track_at(pos)
            typhoon(cv, x, y, 70, t, am)
            cv.text((110, 790), "Forecast track and cone (illustration) · PAGASA issues the official track", 20, V.GREY, am)
        # signal ladder
        al = V.prog(t, s12, 0.5) * (1 - V.prog(t, s14 - 0.3, 0.4))
        if al > 0:
            cv.card((1230, 110, 1830, 840), al, (28, 10, 14))
            cv.text((1260, 134), "TROPICAL CYCLONE WIND SIGNALS", 26, V.GOLD, al, "Bold")
            cv.text((1260, 176), "signal  ·  winds  ·  lead time", 22, V.GREY, al)
            hl = V.prog(t, s13 + 0.4, 0.5)
            for i, (n, wind, lead, col) in enumerate(TCWS):
                ai = V.prog(t, s12 + 0.5 + 0.35 * i, 0.4) * al
                y = 220 + i * 112
                cv.rect((1260, y, 1350, y + 90), col, ai, 14)
                cv.ctext(1305, y + 12, str(n), 56, V.WHITE, ai, "Black")
                cv.text((1372, y + 6), "Signal No. %d" % n, 32, V.WHITE, ai, "Bold")
                cv.text((1372, y + 50), wind, 26, V.CREAM, ai)
                cv.rect((1650, y + 14, 1806, y + 76), V.GOLD, ai * hl, 12)
                cv.ctext(1728, y + 22, lead, 36, V.INK if hl > 0.5 else V.WHITE, ai, "Black")
            cv.text((1260, 790), "PAGASA Tropical Cyclone Wind Signals (2022)", 20, V.GREY, al)
        # family
        af = V.prog(t, s14 - 0.1, 0.5)
        if af > 0:
            cv.rect((0, 700, V.W, 860), (40, 18, 18), 0.9 * af)
            P.house(cv, 430, 760, 80, af)
            for (x, y, s, cane) in [(570, 760, 34, False), (620, 760, 30, False), (665, 760, 22, False), (715, 760, 30, True)]:
                P.person(cv, x, y, s, V.CREAM, af, cane)
            typhoon(cv, 1450, 330, 150, t, af * 0.9)
            for k in range(40):
                rx = (k * 97 + t * 900) % 1900
                ry = (k * 53 + t * 1400) % 640 + 100
                cv.line([(rx, ry), (rx - 10, ry + 34)], (200, 215, 235), af * 0.5, 2)
            a3 = V.prog(t, self.frac("1.4", 0.45), 0.4)
            cv.card((520, 470, 960, 560), a3, V.CREAM)
            cv.text((550, 492), "Where do we go?", 40, V.INK, a3, "Bold")
            cv.poly([(660, 560), (700, 560), (640, 610)], V.CREAM, a3 * 0.96)
            a4 = V.prog(t, self.frac("1.4", 0.75), 0.4)
            cv.card((660, 590, 1000, 670), a4, (255, 236, 200))
            cv.text((685, 608), "Room for Lola?", 36, V.CRIMSON, a4, "Bold")

    def draw_community(self, cv, t):
        c = self.cue
        rnd = random.Random(5)
        a = V.prog(t, c["2.1"]["start"] - 0.2, 0.8)
        cx, cy = 520, 440
        for i in range(720):
            ang = rnd.random() * 2 * math.pi
            rr = math.sqrt(rnd.random())
            x = cx + math.cos(ang) * rr * 330 * (1 + 0.25 * math.sin(ang * 3))
            y = cy + math.sin(ang) * rr * 260
            if i / 720 <= a:
                cv.circle((x, y), 3.2, V.CREAM, 0.75)
        cv.circle((cx + 40, cy - 40), 90, (255, 90, 60), 0.18 * a)
        cv.poly([(cx + 22, cy - 30), (cx + 40, cy - 62), (cx + 58, cy - 30)], (90, 60, 60), a)
        cv.ctext(cx, 742, "ALBAY · 18 towns · 720 barangays · 1,374,768 residents", 30, V.WHITE, a, "SemiBold")
        cv.ctext(cx, 786, "PSA 2020 census", 22, V.GREY, a)
        s25 = c["2.5"]["start"]
        cards = [("2.2", "NOVEMBER 2006 · TYPHOON REMING (DURIAN)", "Lahar from Mayon's old deposits",
                  "about 1,200 dead and missing", "Philippine Daily Inquirer, 2016"),
                 ("2.3", "NOVEMBER 2020 · SUPER TYPHOON ROLLY (GONI)", "Landfall in Tiwi, Albay",
                  "Signal No. 5", "PAGASA, 2020"),
                 ("2.4", "JANUARY 2026 · MAYON ALERT LEVEL 3", "4 schools became evacuation centers",
                  "%s learners affected", "Philippine Daily Inquirer, 2026")]
        for i, (cid, head, line1, big, src) in enumerate(cards):
            ai = V.prog(t, c[cid]["start"] - 0.1, 0.5) * (1 - V.prog(t, s25 - 0.3, 0.3))
            if ai <= 0:
                continue
            y0 = 120 + i * 240
            cv.card((980, y0, 1820, y0 + 220), ai, (28, 10, 14))
            cv.text((1015, y0 + 22), head, 26, V.GOLD, ai, "Bold")
            cv.text((1015, y0 + 64), line1, 34, V.WHITE, ai, "SemiBold")
            if "%s" in big:
                big = big % counter_s(3424, V.prog(t, c[cid]["start"] + 0.4, 2.0))
            cv.text((1015, y0 + 110), big, 46, V.GOLD_LT, ai, "Black")
            cv.text((1015, y0 + 178), src, 20, V.GREY, ai)
        a4 = V.prog(t, s25 - 0.1, 0.5)
        if a4 > 0:
            for i, (g, sub, col) in enumerate((("SDG 4.a", "safe places to learn", V.GOLD),
                                               ("SDG 11.5", "protect people from disasters", V.BLUE),
                                               ("SDG 13.1", "resilience to climate hazards", V.GREEN))):
                P.chip(cv, 1000, 150 + i * 150, g, sub, V.prog(t, s25 + 0.3 * i, 0.4), col, 640)
            a5 = V.prog(t, self.frac("2.5", 0.2), 0.5)
            P.school(cv, 1700, 690, 56, a5, 0.0)
            cv.rect((980, 600, 1600, 760), (20, 6, 10), 0.85 * a5, 14)
            cv.text((1000, 616), "RA 10821: schools are evacuation", 28, V.GOLD_LT, a5, "SemiBold")
            cv.text((1000, 656), "centers only as a last resort", 28, V.GOLD_LT, a5, "SemiBold")
            cv.text((1000, 704), "DepEd: open spaces before classrooms", 24, V.WHITE, a5)

    def draw_stakes(self, cv, t):
        c = self.cue
        box = (1000, 150, 1800, 820)
        s31, s32, s33, s34 = (c[k]["start"] for k in ("3.1", "3.2", "3.3", "3.4"))
        a = V.prog(t, s31 - 0.2, 0.5)
        P.badge(cv, 330, 180, "SIGNAL NO. 4", 54, (205, 40, 40), a)
        left = 12 * (1 - V.prog(t, s31 + 0.3, s34 - s31))
        cv.circle((330, 420), 120, (28, 10, 14), a, outline=V.GOLD, width=6)
        ang = -math.pi / 2 + 2 * math.pi * (left / 12)
        cv.line([(330, 420), (330 + 90 * math.cos(ang), 420 + 90 * math.sin(ang))], V.GOLD, a, 8)
        cv.ctext(330, 560, "lead time %.1f h" % left, 46, V.WHITE, a, "Bold")
        self.draw_net(cv, box, a * 0.95, 1.0,
                      closed=[x for i, x in enumerate(("A1", "A2", "A3", "A4", "B1", "B2", "B3"))
                              if t > s32 + 0.8 + 0.25 * i], show_labels=False)
        a2 = V.prog(t, s32, 0.5)
        if a2 > 0:
            cv.text((1010, 96), "lahar channels A and B · bridges closed", 26, (230, 160, 120), a2, "SemiBold")
        a3 = V.prog(t, s33 - 0.1, 0.5)
        if a3 > 0:
            for o in E1["origins"]:
                p = self.net_xy(o["id"], box)
                q = self.net_xy(self.snode[o["nearest"]], box)
                cv.line([p, q], V.WHITE, a3 * 0.8, 4)
                cv.circle(q, 18, V.RED, a3 * 0.6)
            cv.card((120, 640, 900, 830), a3, (28, 10, 14))
            cv.text((150, 662), "Nearest-site rule", 32, V.GOLD, a3, "Bold")
            cv.text((150, 712), counter_s(AL4L["nearest_overflow"], V.prog(t, s33 + 0.3, 1.8))
                    + " arrive at full shelters", 46, V.WHITE, a3, "Black")
            cv.text((150, 780), "test network E1 (synthetic) · Alert Level 4 + typhoon lahar", 22, V.GREY, a3)
        a4 = V.prog(t, s34 - 0.1, 0.4)
        if a4 > 0:
            cv.rect((0, 0, V.W, V.H), (0, 0, 0), 0.82 * a4)
            lines = (("Everyone sheltered", V.WHITE), ("Vulnerable first", V.GOLD_LT),
                     ("Classrooms last", V.GOLD), ("Before the lead time ends", V.WHITE))
            for i, (s, col) in enumerate(lines):
                cv.ctext(V.W / 2, 170 + i * 120, s, 74, col, V.prog(t, self.frac("3.4", 0.12 + 0.2 * i), 0.4), "Black")
            cv.ctext(V.W / 2, 650, "?", 110, V.WHITE, V.prog(t, self.frac("3.4", 0.9), 0.4), "Black")

    def draw_mcs(self, cv, t):
        c = self.cue
        s = {k: c[k]["start"] for k in c if k.startswith("4.")}
        if t < s["4.2"] - 0.2:
            P.mcs_reveal(cv, t - s["4.1"] + 0.2)
            return
        if t >= s["4.11"] - 0.4:
            self.closing(cv, t, s)
            return
        lit = sum(V.prog(t, st, 0.5) for st in (s["4.2"] - 0.2, s["4.2"] + 0.8, s["4.3"], s["4.4"], s["4.5"], s["4.6"]))
        P.chain(cv, CHAIN, lit, 40)
        a_mcs = 1 - V.prog(t, s["4.2"], 0.4)
        if a_mcs > 0:
            P.mcs_reveal(cv, t - s["4.1"] + 0.2, alpha=a_mcs)
        if t < s["4.7"] - 0.3:
            self.objectives(cv, t, s)
        elif t < s["4.10"] - 0.3:
            self.results(cv, t, s)
        else:
            self.proof(cv, t, s)

    def objectives(self, cv, t, s):
        box = (90, 150, 920, 840)
        a = V.prog(t, s["4.2"], 0.6) * (1 - V.prog(t, s["4.7"] - 0.6, 0.3))
        P.panel(cv, box, "TEST NETWORK E1 (SYNTHETIC)", a)
        netbox = (130, 200, 890, 830)
        closed = ("A1", "A2", "A3", "A4", "B1", "B2", "B3") if t > s["4.2"] + 1.5 and t < s["4.3"] - 0.2 else ()
        self.draw_net(cv, netbox, a, V.prog(t, s["4.2"] + 0.3, 2.0), closed=closed)
        if s["4.3"] < t < s["4.4"]:
            self.flows(cv, netbox, a * V.prog(t, s["4.3"] + 0.5, 0.5), t)
        if t > s["4.5"]:
            pa = V.prog(t, self.frac("4.5", 0.6), 0.5) * a
            x, y = self.net_xy("TS", netbox)
            cv.circle((x, y), 34, V.GREEN, pa * 0.5, outline=V.GREEN, width=4)
            cv.text((x - 150, y + 30), "new Ligtas Pinoy Center", 24, V.GREEN, pa, "Bold")
        right = (980, 150, 1830, 840)
        keys = ["4.2", "4.3", "4.4", "4.5", "4.6", "4.7"]
        for i, k in enumerate(keys[:-1]):
            if s[k] - 0.2 <= t < s[keys[i + 1]] - 0.2:
                a1 = V.prog(t, s[k] - 0.2, 0.5) * (1 - V.prog(t, s[keys[i + 1]] - 0.5, 0.3))
                getattr(self, "obj%d" % (i + 1))(cv, t, a1, s[k], right)

    def obj_head(self, cv, right, n, title, a1):
        P.panel(cv, right, "OBJECTIVE %d" % n, a1)
        cv.text((1020, 226), title, 40, V.GOLD_LT, a1, "Black")

    def obj1(self, cv, t, a1, st, right):
        self.obj_head(cv, right, 1, "Signal and track → scenario", a1)
        cv.paste(self.eqimg("scen", 54), (1020, 300), V.prog(t, st + 0.6, 0.5) * a1)
        rows = [("Z", "zones that must leave: lahar, flood, storm surge", (230, 160, 120)),
                ("X", "roads that close: bridges over lahar channels", V.RED),
                ("L", "lead time from the wind signal", V.GOLD)]
        for i, (k, txt, col) in enumerate(rows):
            ai = V.prog(t, self.frac("4.2", 0.35 + 0.18 * i), 0.4) * a1
            y = 420 + i * 110
            cv.rect((1020, y, 1090, y + 76), col, ai, 12)
            cv.ctext(1055, y + 12, k, 44, V.WHITE, ai, "Black")
            cv.para((1110, y + 8), txt, 30, 680, V.WHITE, ai, "SemiBold", 1.2)

    def obj2(self, cv, t, a1, st, right):
        self.obj_head(cv, right, 2, "One lexicographic flow", a1)
        tiers = [("Tier 0", "non-school space", V.BLUE), ("Tier 1", "school open space", V.GREEN),
                 ("Tier 2", "classrooms · 18 per room", V.GOLD)]
        for i, (a_, b_, col) in enumerate(tiers):
            ai = V.prog(t, st + 0.4 + 0.3 * i, 0.4) * a1
            cv.rect((1020, 300 + i * 56, 1048, 328 + i * 56), col, ai, 6)
            cv.text((1064, 296 + i * 56), a_ + "  ·  " + b_, 30, V.WHITE, ai, "SemiBold")
        a3 = V.prog(t, self.frac("4.3", 0.35), 0.5) * a1
        cv.text((1020, 490), "Vulnerable ≻ everyone ≻ classrooms last", 30, V.GOLD_LT, a3, "Bold")
        cv.paste(self.eqimg("lex", 50), (1020, 540), a3)
        cv.paste(self.eqimg("pen", 46), (1020, 620), V.prog(t, self.frac("4.3", 0.6), 0.5) * a1)
        cv.text((1020, 720), "integral plans · exact · no rounding", 26, V.WHITE, V.prog(t, self.frac("4.3", 0.8), 0.5) * a1)

    def obj3(self, cv, t, a1, st, right):
        self.obj_head(cv, right, 3, "Exact clearance time", a1)
        cv.paste(self.eqimg("tstar", 50), (1020, 296), V.prog(t, st + 0.5, 0.5) * a1)
        cv.paste(self.eqimg("lead", 50), (1020, 362), V.prog(t, self.frac("4.4", 0.7), 0.5) * a1)
        gx0, gy0, gx1, gy1 = 1040, 470, 1780, 810
        cv.line([(gx0, gy1), (gx1, gy1)], V.GREY, a1, 2)
        cv.line([(gx0, gy0), (gx0, gy1)], V.GREY, a1, 2)
        pc = V.prog(t, st + 0.8, 3.0)
        for key, col in (("AL3", V.GOLD), ("AL4+L", (230, 120, 90))):
            curve = E1["curves"][key]
            pts = []
            for i, v in enumerate(curve):
                if i / len(curve) > pc:
                    break
                pts.append((gx0 + (gx1 - gx0) * i / 45, gy1 - (gy1 - gy0) * v / 2500))
            if len(pts) > 1:
                cv.line(pts, col, a1, 5)
        cv.text((gx0 + 20, gy0 - 4), "F(T): evacuees sheltered by minute T", 22, V.WHITE, a1 * 0.9)
        ae = V.prog(t, self.frac("4.4", 0.55), 0.4) * a1
        cv.text((1420, 610), "Alert Level 3: T* = %d min" % AL3["clearance_lex"], 28, V.GOLD, ae, "Bold")
        cv.text((1420, 652), "with typhoon lahar: %d min" % AL4L["clearance_lex"], 28, (230, 120, 90), ae, "Bold")
        cv.text((1420, 700), "well inside a 12-h lead time", 24, V.WHITE, ae)

    def obj4(self, cv, t, a1, st, right):
        self.obj_head(cv, right, 4, "Bridges to protect, centers to build", a1)
        cv.paste(self.eqimg("delta", 52), (1020, 300), V.prog(t, st + 0.5, 0.5) * a1)
        ab = V.prog(t, self.frac("4.5", 0.3), 0.5) * a1
        cv.text((1020, 380), "lahar channel A closed: %d → %d min" % (CHAN["none"]["clearance_fixed_plan"],
                                                                   CHAN["A"]["clearance_fixed_plan"]), 30, V.WHITE, ab, "SemiBold")
        cv.text((1020, 424), "lahar channel B closed: %d → %d min" % (CHAN["none"]["clearance_fixed_plan"],
                                                                   CHAN["B"]["clearance_fixed_plan"]), 30, V.WHITE, ab, "SemiBold")
        cv.paste(self.eqimg("greedy", 60), (1020, 500), V.prog(t, self.frac("4.5", 0.55), 0.5) * a1)
        ag = V.prog(t, self.frac("4.5", 0.7), 0.5) * a1
        cv.text((1020, 590), "coverage is submodular, so the greedy choice", 28, V.WHITE, ag)
        cv.text((1020, 630), "always reaches at least 63.2% of the best", 28, V.WHITE, ag)
        cv.text((1020, 690), "Ligtas Pinoy Centers (RA 12076)", 26, V.GREEN, ag, "Bold")

    def obj5(self, cv, t, a1, st, right):
        self.obj_head(cv, right, 5, "Prove, then verify", a1)
        P.proof_marks(cv, 10, 1040, 360, t, st + 0.3, 0.15, 46)
        cv.text((1020, 470), "Every proposition is checked against", 30, V.WHITE, V.prog(t, st + 1.0, 0.5) * a1, "SemiBold")
        cv.text((1020, 512), "reference code written independently", 30, V.WHITE, V.prog(t, st + 1.0, 0.5) * a1, "SemiBold")

    def results(self, cv, t, s):
        cards = [("4.7", "CLEARANCE TIME", "%d → %d min" % (CHAN["none"]["clearance_fixed_plan"], CHAN["A"]["clearance_fixed_plan"]),
                  "lahar channel A closed", "protect these bridges first"),
                 ("4.8", "TYPHOON RAIN ON AN ERUPTION", "%d cut off" % AL4L["lex"]["unplaced"],
                  "one new Ligtas Pinoy Center", "reaches %d of them" % SIT[0]["gain"]),
                 ("4.9", "CLASSROOMS CLOSED", "%d → %d" % (AL3["blind"]["rooms_closed_total"], AL3["lex"]["rooms_closed_total"]),
                  "learners displaced %s → %s" % ("{:,}".format(AL3["blind"]["learners_displaced"]),
                                                  "{:,}".format(AL3["lex"]["learners_displaced"])), "Alert Level 3")]
        a = 1 - V.prog(t, s["4.10"] - 0.6, 0.3)
        for i, (cid, head, big, l1, l2) in enumerate(cards):
            ai = V.prog(t, s[cid] - 0.2, 0.5) * a
            x0 = 110 + i * 580
            cv.card((x0, 170, x0 + 540, 700), ai, (28, 10, 14))
            cv.text((x0 + 34, 200), head, 28, V.GOLD, ai, "Bold")
            cv.text((x0 + 34, 270), big, 78, V.WHITE, ai, "Black")
            cv.para((x0 + 34, 400), l1, 32, 470, V.GOLD_LT, ai, "SemiBold", 1.2)
            cv.para((x0 + 34, 500), l2, 30, 470, V.GREEN, ai, "Bold", 1.2)
        cv.ctext(V.W / 2, 750, "test network E1 (synthetic) · model outputs, not Albay data", 26, V.GREY, a)

    def proof(self, cv, t, s):
        ap = V.prog(t, s["4.10"] - 0.2, 0.5)
        cv.ctext(V.W / 2, 190, "10 results, proven, then verified", 70, V.WHITE, ap, "Black")
        P.proof_marks(cv, 10, V.W / 2 - 9 * 34, 330, t, s["4.10"] + 0.2, 0.12, 46)
        stats = [("%s / %s" % (VER["V1"]["agree"], VER["V1"]["instances"]), "plans matched five linear programs"),
                 ("%s / %s" % (VER["V3"]["agree"], VER["V3"]["pairs"]), "networks matched Ford–Fulkerson"),
                 ("{:,}".format(VER["V6"]["checks_total"]), "submodularity checks, 0 violations")]
        for i, (big, small) in enumerate(stats):
            ai = V.prog(t, s["4.10"] + 0.8 + 0.3 * i, 0.4)
            x0 = 170 + i * 540
            cv.card((x0, 450, x0 + 500, 640), ai, (28, 10, 14))
            cv.text((x0 + 30, 476), big, 64, V.GOLD, ai, "Black")
            cv.text((x0 + 30, 570), small, 26, V.WHITE, ai, "SemiBold")

    def closing(self, cv, t, s):
        cv.rect((0, 0, V.W, V.H), (0, 0, 0), 0.5)
        a1 = V.prog(t, s["4.11"] - 0.2, 0.4) * (1 - V.prog(t, s["4.12"] - 0.4, 0.3))
        cv.para((V.W / 2, 380), "LIGTA-S will not stop a typhoon.", 74, 1500, V.WHITE, a1, "Bold", 1.2, "center")
        a2 = V.prog(t, s["4.12"] - 0.2, 0.4) * (1 - V.prog(t, s["4.13"] - 0.4, 0.3))
        cv.para((V.W / 2, 300), "But before landfall, it will tell every family where to go, in time, and keep the most classrooms open.",
                62, 1500, V.GOLD, a2, "Bold", 1.25, "center")
        a3 = V.prog(t, s["4.13"] - 0.2, 0.4)
        a4 = V.prog(t, s["4.14"] - 0.2, 0.4)
        cv.para((V.W / 2, 300), "A signal tells you the storm is coming.", 64, 1600, V.WHITE, a3, "Bold", 1.2, "center")
        cv.para((V.W / 2, 470), "A plan tells you if there is room, in time.", 64, 1600, V.GOLD, a4, "Bold", 1.2, "center")


def counter_s(v, p):
    return "{:,}".format(int(round(v * V.ease(p))))


def main():
    spec = Spec()
    V.save_timeline(spec, os.path.join(HERE, "timeline.json"))
    print("length %.1f s, title at %.1f s, boom %.1f s" % (spec.total, spec.title_start, spec.boom_t))
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
    img.save(os.path.join(OUT, "LIGTA-S_Title_Page_1920x1080.png"))
    img.resize((3840, 2160), Image.LANCZOS).save(os.path.join(OUT, "LIGTA-S_Title_Page_3840x2160.png"))
    print(out)


if __name__ == "__main__":
    main()

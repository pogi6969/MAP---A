"""Build timeline.json: the single source of truth for the LIGTA-S rationale video.

Every narration line gets a start, a "finish by" and a read time; every visual
cue tied to a word gets an exact time.  render.js draws the video from this
file, make_audio.py places the sound effects from it, and make_script.py
prints the narration script from it, so the three always agree.

Run:  python3 build_timeline.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
WPS = 2.9          # words per second while speaking (reference read)
PUNCT_PAUSE = 0.2   # extra seconds for each comma, colon or mid-line question mark
TAIL = 0.3         # subtitle stays this long after the reference read ends
TITLE_LEN = 10.0

# Each scene: id, name, stakes-bar label, lead-in (s), lines, hold after last line (s).
# Each line: text, pre (gap before it, s), cues {id: word}, screen (on-screen description).
SCENES = [
    {
        "id": "s1", "name": "Alert", "bar": "Safety", "lead": 0.8, "hold": 0.8,
        "lines": [
            {"text": "Mayon rumbles, and the alert goes up.", "pre": 0.0,
             "cues": {"alert": "alert"},
             "screen": "Night sky; the cone of Mayon draws in with a thin ash plume and a glowing summit. "
                       "On “alert” a badge “ALERT LEVEL 3” flashes, with the chip “January 6, 2026 · "
                       "PHIVOLCS raises Mayon to Alert Level 3” (source: Interaksyon/Philstar, Jan 6, 2026)."},
            {"text": "A family in the six-kilometer danger zone must leave.", "pre": 0.4,
             "cues": {"zone": "six-kilometer", "family": "family", "leave": "leave"},
             "screen": "The 6-km Permanent Danger Zone ring draws around the base. A house inside it; "
                       "a mother, Lolo with a cane and a schoolgirl with a backpack step out and start walking. "
                       "Label “preemptive evacuation”."},
            {"text": "Which shelter has room? Can Lolo get in? How far is it?", "pre": 0.4,
             "cues": {"q1": "Which", "q2": "Can", "q3": "How"},
             "screen": "Three tags pop in, one per question: “Which shelter has room?” · "
                       "“Can Lolo get in?” (wheelchair-ramp icon) · “How far is it?” (clock)."},
            {"text": "And if it is a classroom, whose class stops?", "pre": 0.4,
             "cues": {"room": "classroom", "stops": "stops"},
             "screen": "A fourth tag in gold: “Whose class stops?” A classroom (board and desks) appears; "
                       "on “stops” a red stamp “CLASS SUSPENDED” lands on the board."},
            {"text": "Our shelter model answers all of it.", "pre": 0.4,
             "cues": {"model": "model", "all": "all"},
             "screen": "The LIGTA-S badge appears; on “all” the four tags turn gold with check marks. "
                       "Under the badge: “where to go · is there room · can they get in · how long · "
                       "which classrooms”."},
        ],
    },
    {
        "id": "s2", "name": "Community", "bar": "Learning", "lead": 0.6, "hold": 0.7,
        "lines": [
            {"text": "Zoom out.", "pre": 0.0, "cues": {},
             "screen": "The family scene shrinks away. Albay card: 18 cities and municipalities · 720 barangays "
                       "· 1,374,768 residents (PSA 2020 census); a field of 720 dots, one per barangay."},
            {"text": "In January, four schools became shelters, and thousands of learners were affected.",
             "pre": 0.4, "cues": {"four": "four", "learners": "thousands"},
             "screen": "Four school icons turn into evacuation centers. Counters: “3,424 learners affected” "
                       "and “608 learners displaced from the danger zone”; “some schools shifted to "
                       "modular or blended learning” (Philippine Daily Inquirer, 2026)."},
            {"text": "In May, Camalig classrooms were sheltering families.", "pre": 0.4,
             "cues": {"camalig": "Camalig"},
             "screen": "34 classroom tiles fill one by one: “34 classrooms in three Camalig schools · 488 "
                       "families, about 1,315 people” (Daily Tribune, May 4, 2026); chip “ashfall reached up to "
                       "132 schools” (Philippine Star, May 6, 2026)."},
            {"text": "The law says classrooms should come last.", "pre": 0.4,
             "cues": {"law": "law", "last": "last"},
             "screen": "Card “RA 10821 (2016): schools only when no other suitable space exists”; a three-step "
                       "ladder: non-school space → school gym or open space → classrooms (last resort, at most "
                       "15 days unless the LGU documents the need); chip “RA 12076 (2024): a Ligtas Pinoy Center in "
                       "every city and municipality”."},
            {"text": "SDGs 4, 11, and 13 ask for safe schools and safer towns.", "pre": 0.4,
             "cues": {"sdg": "SDGs", "safe": "safe"},
             "screen": "Three goal chips: SDG 4.a safe learning environments · SDG 11.5 fewer people affected "
                       "by disasters · SDG 13.1 resilience to climate hazards."},
            {"text": "Yet no tool told a town how many classrooms it truly needs.", "pre": 0.4,
             "cues": {"how": "how"},
             "screen": "A row of classrooms with question marks; the notation “classrooms needed = ?” "
                       "in gold."},
        ],
    },
    {
        "id": "s3", "name": "Evacuation", "bar": "Lives", "lead": 0.6, "hold": 0.8,
        "lines": [
            {"text": "Now, the evacuation.", "pre": 0.0, "cues": {},
             "screen": "The synthetic test network E1 draws in: summit, ring road, five towns, six barangay clusters, "
                       "shelters. Label “TEST NETWORK E1 · synthetic volcano, not Albay data”."},
            {"text": "On our test network, three barangays must leave.", "pre": 0.4,
             "cues": {"three": "three"},
             "screen": "O1, O2 and O3 inside the 6-km zone pulse red. Card “Alert Level 3 · 1,560 evacuees "
                       "· 342 vulnerable”."},
            {"text": "Send everyone to the nearest shelter, and nearly three hundred find it full.", "pre": 0.4,
             "cues": {"send": "Send", "full": "full"},
             "screen": "Dots stream from each barangay to its nearest shelter site; the northeast and east sites "
                       "overflow and flash FULL; counter “298 arrive at full shelters”."},
            {"text": "A plan that counts only minutes fills the nearest classrooms.", "pre": 0.4,
             "cues": {"minutes": "minutes", "fills": "fills"},
             "screen": "“Time-only plan”: classroom grids of the three schools (20, 30 and 14 rooms) fill in red: "
                       "40 classrooms closed · 1,702 learners displaced · mean trip 29.48 min."},
            {"text": "If a lahar takes the bridges, four hundred fifty are cut off.", "pre": 0.4,
             "cues": {"lahar": "lahar", "bridges": "bridges", "cut": "cut"},
             "screen": "Alert Level 4 with lahar: channels A and B flow down the south flank; the seven bridges "
                       "A1–A4 and B1–B3 get a red X; the southern pocket (O3, O4 and one school, SCH1) "
                       "is shaded: “450 residents cannot be sheltered”."},
            {"text": "Room, time, and school all pull against each other.", "pre": 0.4,
             "cues": {"room": "Room", "time": "time", "school": "school"},
             "screen": "Three chips ROOM · TIME · SCHOOL appear on a triangle, joined by straining lines."},
        ],
    },
    {
        "id": "s4", "name": "How MCS comes into play", "bar": "MCS", "lead": 0.7, "hold": 1.4,
        "lines": [
            {"text": "So, where does MCS come in?", "pre": 0.0, "cues": {"mcs": "MCS"},
             "screen": "Faint math symbols drift behind. On “MCS” the gold letters M, C, S drop in one by one, "
                       "then unfold into Mathematical · Computational · Sciences. The stakes bar reaches its "
                       "top rung, “MCS”."},
            {"text": "Mathematics turns open data on roads and shelters into a graph.", "pre": 1.3,
             "cues": {"math": "Mathematics", "data": "open", "graph": "graph"},
             "screen": "The title shrinks into an MCS badge and a chain appears across the top: Open data → Graph "
                       "→ Algorithm → Numbers → Optimisation → Proof (“Open data” and “Graph” light up). "
                       "Panel MATHEMATICS: G = (N, E) with travel time τ_e and capacity u_e; σ = (active hazard "
                       "zones, closed bridges); D_a, V_a. The test network builds road by road."},
            {"text": "At Sphere's three and a half square meters, a classroom holds eighteen.", "pre": 0.4,
             "cues": {"sphere": "Sphere's", "room": "classroom", "e18": "eighteen"},
             "screen": "c_s = ⌊A_s / 3.5 m²⌋; q = ⌊(7 m × 9 m) / 3.5 m²⌋ = 18; a 7 × 9 m classroom fills with "
                       "18 figures; three shelter tiers: tier 0 non-school space, tier 1 school open space, tier 2 "
                       "classrooms; K_s = ⌈y_s / 18⌉."},
            {"text": "Computing places everyone with one minimum-cost flow, in whole numbers.", "pre": 0.4,
             "cues": {"comp": "Computing", "flow": "minimum-cost", "whole": "whole"},
             "screen": "“Algorithm” lights. Panel COMPUTING: Algorithm 1 steps highlight in turn; cost(a, s, ι) = "
                       "T_σ(a, s) + M_O·1[ι = 1] + M_Y·1[ι = 2]; x ∈ ℤ≥0 (“no evacuee is split between "
                       "shelters”). On the test network the Alert Level 3 plan streams along the roads."},
            {"text": "A copy of the roads per minute gives the exact clearance time.", "pre": 0.4,
             "cues": {"copy": "copy", "exact": "exact"},
             "screen": "“Numbers” lights. A small time-expanded network (one layer per minute); T*_σ = min{T ≥ 0 : "
                       "F_σ(T) = D′}; bisection probes 8, 16, 32, 64, then 31, 47, 55, 51, 53, 52; the arrival curve "
                       "F(T) climbs to 1,560 at T* = 53 min, with the lower bound 34 min dashed (test network)."},
            {"text": "Optimisation follows the law: vulnerable first, then everyone, classrooms last.", "pre": 0.4,
             "cues": {"opt": "Optimisation", "vul": "vulnerable", "everyone": "everyone", "last": "classrooms"},
             "screen": "“Optimisation” lights. Panel OPTIMISATION: max F_V ≻ max F ≻ min Y ≻ min O ≻ min Θ, each "
                       "level glowing on its word; M_O = D·T_max + 1, M_Y = D·(M_O + T_max) + 1."},
            {"text": "On the test network: fourteen classrooms closed, not forty, for under two minutes more travel.",
             "pre": 0.4, "cues": {"fourteen": "fourteen", "forty": "forty", "two": "two"},
             "screen": "Classroom grids drop from 40 red rooms to 14; bars: time-only 40 rooms · 1,702 learners · "
                       "29.48 min against school-preserving 14 rooms · 532 learners · 31.18 min (+1.70 min)."},
            {"text": "When a lahar cuts off a pocket, a greedy rule picks the next Ligtas Pinoy Center.", "pre": 0.4,
             "cues": {"pocket": "pocket", "greedy": "greedy", "center": "Ligtas"},
             "screen": "Both lahar channels close their bridges; the southern pocket shades. f(S) = Φ_θ(E ∪ S) − "
                       "Φ_θ(E) is monotone submodular, so f(S_g) ≥ (1 − 1/e) f(S*) ≈ 0.632 f(S*). A gold star lands "
                       "on the south town: “400 of the 450 sheltered”; second site, northeast town: “persons in "
                       "classrooms 920 → 570”; “greedy = exhaustive best for k = 1 to 3” (test network)."},
            {"text": "Ten results, proven, then verified.", "pre": 0.4,
             "cues": {"ten": "Ten", "proven": "proven", "verified": "verified"},
             "screen": "“Proof” lights. Ten tiles, Propositions 1 to 10, get a proof mark ∎ on “proven” and a "
                       "check on “verified”, with the checks: 300/300 plans · 150/150 bound · 660/660 · 79/79 "
                       "· 0 of 4,796 · greedy worst 0.890. Footer: “Each proven on paper, then checked against "
                       "independent code on synthetic instances · no field data”."},
            {"text": "LIGTA-S cannot build a single new shelter.", "pre": 1.2, "cues": {"single": "single"},
             "boom": True,
             "screen": "Conclusion. A boom just before the line clears the screen to a plain background. The line "
                       "appears large, with “single new shelter” in gold. The large text is its subtitle."},
            {"text": "But once towns list their shelters, it shows each family where to go, and keeps more "
                     "classrooms open.", "pre": 0.4, "cues": {"where": "where", "open": "open"},
             "screen": "Appears under it in two rows, with “where to go” and “more classrooms open” in gold. "
                       "Both lines then fade out."},
            {"text": "The nearest shelter is not always the right one.", "pre": 1.6, "pause": True, "cues": {},
             "screen": "[pause] The screen is empty for a moment. Then the line appears, with the LIGTA-S badge and "
                       "the paper title below."},
            {"text": "The right plan keeps families safe and schools open.", "pre": 0.6, "hit": True,
             "cues": {"safe": "safe", "open2": "open"},
             "screen": "Lands in large gold type with a final hit; “safe” and “open” are underlined. "
                       "Hold silence."},
        ],
    },
]


def words(text):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", text))


def read_time(text):
    w = words(text)
    inner = text.rstrip(".?!")
    pauses = len(re.findall(r"[,:;?]", inner))
    extra = 0.35 if "SDGs" in text else 0.0
    return round(w / WPS + PUNCT_PAUSE * pauses + extra, 1)


def word_time(text, start, read, word):
    """Time a cue word is spoken: proportional to the characters before it."""
    m = re.search(r"(?<![A-Za-z])" + re.escape(word) + r"(?![A-Za-z])", text)
    if not m:
        raise ValueError("cue word %r not in %r" % (word, text))
    frac = m.start() / max(1, len(text))
    return round(start + read * frac, 2)


def main():
    t = 0.0
    out = {"fps": FPS, "width": 1920, "height": 1080, "scenes": [], "lines": [], "cues": {},
           "sfx": []}
    total_words = 0
    for si, sc in enumerate(SCENES):
        s0 = round(t, 2)
        t = s0 + sc["lead"]
        scene_words = 0
        for li, ln in enumerate(sc["lines"]):
            t += ln["pre"] if li else 0.0
            start = round(t, 1)
            rt = read_time(ln["text"])
            finish = round(start + rt + TAIL, 1)
            lid = "%d.%d" % (si + 1, li + 1)
            cues = {}
            for cid, w in ln["cues"].items():
                cues[cid] = word_time(ln["text"], start, rt, w)
                out["cues"]["%s_%s" % (sc["id"], cid)] = cues[cid]
            nw = words(ln["text"])
            scene_words += nw
            out["lines"].append({"id": lid, "scene": sc["id"], "start": start, "finish": finish,
                                 "read": rt, "text": ln["text"], "words": nw, "cues": cues,
                                 "screen": ln["screen"], "boom": ln.get("boom", False),
                                 "pause": ln.get("pause", False), "hit": ln.get("hit", False)})
            t = finish
        t = round(t + sc["hold"], 1)
        out["scenes"].append({"id": sc["id"], "n": si + 1, "name": sc["name"], "bar": sc["bar"],
                              "start": s0, "end": t, "words": scene_words})
        total_words += scene_words
    title0 = t
    out["scenes"].append({"id": "title", "n": 5, "name": "Title card", "bar": "Researchers",
                          "start": title0, "end": round(title0 + TITLE_LEN, 1), "words": 0})
    out["duration"] = round(title0 + TITLE_LEN, 1)
    out["words"] = total_words
    # title card choreography (seconds after the title card starts)
    letters = ["L", "I", "G", "T", "A", "-", "S"]
    out["title"] = {"start": title0, "letters": letters,
                    "letter_times": [round(title0 + 0.75 + 0.2 * i, 2) for i in range(len(letters))],
                    "shine": round(title0 + 2.25, 2), "title_lines": round(title0 + 2.35, 2),
                    "rules": round(title0 + 3.6, 2), "leader": round(title0 + 4.1, 2),
                    "role": round(title0 + 4.7, 2), "members": round(title0 + 5.3, 2),
                    "leader_shine": round(title0 + 6.1, 2), "fade": round(title0 + 9.2, 2)}
    # sound effects
    for sc in out["scenes"][1:]:
        out["sfx"].append({"kind": "whoosh", "t": round(sc["start"] - 0.35, 2)})
    for ln in out["lines"]:
        if ln["boom"]:
            out["sfx"].append({"kind": "boom", "t": round(ln["start"] - 0.25, 2)})
            out["cues"]["boom"] = round(ln["start"] - 0.25, 2)
        if ln["hit"]:
            out["sfx"].append({"kind": "hit", "t": round(ln["start"] + 0.05, 2)})
    out["cues"]["s4_drop"] = out["cues"]["s4_mcs"]
    for i, lt in enumerate(out["title"]["letter_times"]):
        out["sfx"].append({"kind": "letter", "t": round(lt + 0.22, 2), "i": i})
    out["sfx"].append({"kind": "shine", "t": out["title"]["shine"]})
    out["sfx"].append({"kind": "shine", "t": out["title"]["leader_shine"]})
    with open(os.path.join(HERE, "timeline.json"), "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    for sc in out["scenes"]:
        print("%-6s %-28s %6.1f-%6.1f  %5.1fs  %3d words" % (sc["id"], sc["name"], sc["start"], sc["end"],
                                                            sc["end"] - sc["start"], sc["words"]))
    print("duration %.1f s (%d:%04.1f), %d words, %.2f words/s over the narrated part"
          % (out["duration"], out["duration"] // 60, out["duration"] % 60, total_words,
             total_words / title0))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the single timeline (scenes, narration lines, on-screen cues, sound cues)
for the BANTA-Y rationale video v1.

The renderer (render.html), the audio generator (make_audio.py) and the narration
script (make_script.py) all read the file written here, so the times printed in
the script are exactly the times in the video.

Numbers shown about the test network D1 are read from
../../code/results.json (key "d1"); they are synthetic, never Albay data.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "..", "code", "results.json")

# ---------------------------------------------------------------------------
# Narration. gold = phrases drawn in gold in the subtitle (and on screen).
# gap = silence before the line (s); hold = extra time after the line (s).
# onscreen: production note; {w:N} -> time of word N of this line,
# {t:+x} -> line start + x seconds.
# ---------------------------------------------------------------------------
SCENES = [
    {"id": "s1", "name": "Fever", "bar": "A household"},
    {"id": "s2", "name": "Province", "bar": "A province"},
    {"id": "s3", "name": "Outbreak", "bar": "Lives"},
    {"id": "s4", "name": "How MCS comes into play", "bar": "MCS"},
]

LINES = [
    # ---------------- Scene 1 ----------------
    dict(id="1.1", scene="s1", gap=0.4, text="Start with one child, and one fever.",
         gold=["one fever"],
         onscreen="Night turns to dawn over a small house in a barangay. A child steps out of the door; "
                  "on \u201cfever\u201d a red pulse rings her and a thermometer appears."),
    dict(id="1.2", scene="s1", text="Her dengue case is written down at her home address.",
         gold=["home address"],
         onscreen="A case card drops onto the house: \u201cDengue case \u00b7 recorded at: home address\u201d, "
                  "and a red pin marks the house ({w:9})."),
    dict(id="1.3", scene="s1", text="But the mosquito that carries dengue bites by day, at school, at the market, at work.",
         gold=["by day"],
         onscreen="The sun rises. Her day path draws from home to the school ({w:11}), the market ({w:14}) "
                  "and a workplace ({w:16}); Aedes aegypti mosquitoes buzz at the school and the market, "
                  "not at the house. Chip: \u201cAedes aegypti bites by day and stays close to where it breeds "
                  "(Stoddard et al., 2013, PNAS)\u201d."),
    dict(id="1.4", scene="s1", text="So where was she bitten, and where should the brigade clean?",
         gold=["where was she bitten"], hold=0.6,
         onscreen="Question marks rise over the house and the school; on \u201cbrigade\u201d a dengue-brigade "
                  "worker with a sprayer appears between them and turns from one to the other."),
    # ---------------- Scene 2 ----------------
    dict(id="2.1", scene="s2", gap=0.5, text="Zoom out.",
         onscreen="Whoosh. The town shrinks into one dot among 720 barangay dots in 18 clusters; "
                  "\u201cALBAY \u00b7 18 cities and municipalities \u00b7 720 barangays \u00b7 1,374,768 residents "
                  "(PSA 2020 census)\u201d, marked \u201cschematic, not a map\u201d."),
    dict(id="2.2", scene="s2", text="In September 2026, Albay declared a state of calamity over dengue.",
         gold=["state of calamity"],
         onscreen="A red stamp lands on \u201ccalamity\u201d ({w:9}): \u201cSTATE OF CALAMITY \u00b7 dengue \u00b7 "
                  "Albay Provincial Board \u00b7 Sept 10, 2026\u201d. Dots across the field turn red."),
    dict(id="2.3", scene="s2", text="Cases rose eighty-four percent from the year before, and fourteen people died.",
         gold=["eighty-four percent"],
         onscreen="Bars for Jan 1\u2013Sept 12: 2025 \u00b7 1,183 and 2026 \u00b7 2,179 with \u201c+84%\u201d; "
                  "on \u201cfourteen\u201d the chip \u201c14 deaths\u201d, then \u201c2,888 cases by Sept 21\u201d. "
                  "Source: Daily Tribune, Sept 2026."),
    dict(id="2.4", scene="s2", text="Sustainable Development Goal 3 asks us to end such epidemics, and to warn early.",
         gold=["Goal 3"], hold=0.6,
         onscreen="Lower third: \u201cSDG 3 \u00b7 Good health and well-being\u201d with \u201c3.3 end epidemics of "
                  "neglected tropical diseases, dengue among them\u201d and, on \u201cwarn early\u201d, "
                  "\u201c3.d early warning\u201d."),
    # ---------------- Scene 3 ----------------
    dict(id="3.1", scene="s3", gap=0.5, text="Now, the response.",
         onscreen="Whoosh. A school with a \u201cCLOSED\u201d banner: \u201cPublic schools closed Sept 14\u201318 "
                  "for cleanup and fogging\u201d (Daily Tribune, Sept 2026)."),
    dict(id="3.2", scene="s3", text="Brigades clean and spray where cases live, because that is what the reports show.",
         gold=["where cases live"],
         onscreen="Bars \u201cCases by home address\u201d: Legazpi City 486 \u00b7 Bacacay 296 \u00b7 Daraga 220 "
                  "\u00b7 Tabaco 181 \u00b7 Malilipot 171. Beside them the DOH 4S card: Search and destroy "
                  "\u00b7 Self-protection \u00b7 Seek early consultation \u00b7 Support fogging only in hotspots, "
                  "with \u201conly in hotspots\u201d circled and \u201cWhich places are the hotspots?\u201d"),
    dict(id="3.3", scene="s3", text="But if the mosquitoes breed at a school or a market, the source survives.",
         gold=["the source survives"],
         onscreen="Split view: \u201cwhere cases live\u201d, houses under spray with green checks; "
                  "\u201cwhere mosquitoes breed\u201d, the school and the market still swarming. "
                  "On \u201csurvives\u201d ({w:13}) the label \u201csource survives\u201d."),
    dict(id="3.4", scene="s3", text="And when the wards fill up, the outbreak is already weeks old.",
         gold=["weeks old"], hold=0.6,
         onscreen="A week-by-week strip fills with rising bars (illustration); a hospital icon reads "
                  "\u201cNaga City hospitals full \u00b7 Sept 2026\u201d; the alarm bell rings only at the end, "
                  "labelled \u201crecognised late\u201d."),
    # ---------------- Scene 4 ----------------
    dict(id="4.1", scene="s4", gap=0.6, text="You may be wondering: how does MCS come into play?",
         gold=["MCS"],
         onscreen="Whoosh. \u201cYou may be wondering\u2026\u201d, then \u201cHow does\u201d. On \u201cMCS\u201d "
                  "({w:7}) the gold letters M, C, S drop in and unfold into Mathematical \u00b7 Computational "
                  "\u00b7 Sciences, then \u201ccome into play?\u201d. Faint math symbols drift behind; "
                  "the stakes bar climbs to its top rung, \u201cMCS\u201d."),
    dict(id="4.2", scene="s4", gap=0.7, text="Mathematics turns where people spend the day into a network.",
         gold=["Mathematics"],
         onscreen="The title shrinks into an \u201cMCS\u201d badge and a chain lights up across the top: Open "
                  "data \u2192 Graph \u2192 Algorithm \u2192 Numbers \u2192 Optimisation \u2192 Proof. Panel "
                  "\u201cMATHEMATICS\u201d: the residence-time matrix p\u1d62\u1d62 = 1 \u2212 \u03c9\u1d62, "
                  "p\u1d62\u2c7c \u221d A\u2c7c e^(\u2212\u03b2T\u1d62\u2c7c), people present by day "
                  "\u00d1\u2c7c = \u03a3 p\u2096\u2c7c N\u2096 and m\u2c7c = V\u2c7c/\u00d1\u2c7c. The synthetic "
                  "test network D1 builds: six barangays, flows of people as moving arcs; B1 (school + market) "
                  "swells from 4,000 residents to 7,300 people present by day."),
    dict(id="4.3", scene="s4", text="Dengue's reproduction number becomes the largest eigenvalue of one symmetric matrix.",
         gold=["largest eigenvalue"],
         onscreen="\u03ba = a\u00b2bc\u03bd / (\u03bc\u1d65(\u03bd+\u03bc\u1d65)(\u03b3+\u03bc\u2095)) = 0.584; "
                  "M = \u03ba D_N P W P\u1d40, W = diag(V\u2c7c/\u00d1\u2c7c\u00b2); on \u201ceigenvalue\u201d "
                  "R\u2080\u00b2 = \u03bb_max(S) with S symmetric positive semidefinite, and the bounds "
                  "min R\u1d62 \u2264 R\u2080\u00b2 \u2264 max R\u1d62. Read-out: \u201ctest network: "
                  "R\u2080 = 1.214 > 1 \u00b7 averaged 1.204 hides risk \u00b7 B1 alone 1.759\u201d."),
    dict(id="4.4", scene="s4", gap=0.8, text="Computing traces cases from home addresses back to the places of infection.",
         gold=["places of infection"],
         onscreen="Panel \u201cCOMPUTING\u201d: y = P z, solved by nonnegative least squares (Lawson\u2013Hanson) "
                  "with the error bound \u2016\u1e91 \u2212 z\u2016 \u2264 \u2016\u03b5\u2016 / min(2p\u1d62\u1d62 \u2212 1). "
                  "Four weeks of test-network cases: grey bars by residence (76, 91, 53, 39, 24, 25) flow along "
                  "the arcs and regroup as gold bars by place (151.0, 55.8, 40.0, 32.5, 15.5, 13.2)."),
    dict(id="4.5", scene="s4", text="In the test network, homes point to B2, but the school and market in B1 carry the most transmission.",
         gold=["B1"],
         onscreen="Place shares s\u2c7c = \u03bawj(q\u2c7c\u00b7v)\u00b2/R\u2080\u00b2, \u03a3s\u2c7c = 1. On \u201cB2\u201d "
                  "({w:8}) B2 lights grey: \u201c28.5% of cases by home\u201d; on \u201cB1\u201d ({w:15}) B1 "
                  "turns gold and swells: \u201c42.6% of transmission happens here\u201d."),
    dict(id="4.6", scene="s4", gap=0.8, text="Optimisation finds the cheapest brigade plan that brings R-naught below one, and certifies it.",
         gold=["cheapest brigade plan"], hold=0.6,
         onscreen="Panel \u201cOPTIMISATION\u201d: min \u03a3 c\u2c7cu\u2c7c subject to R\u2080(u) \u2264 0.95, "
                  "0 \u2264 u\u2c7c \u2264 0.8; convex, solved by a barrier interior-point method with a "
                  "certified dual lower bound. Team-days (test network): spray everywhere equally 37.47 \u00b7 "
                  "where cases live 38.88 \u00b7 place shares 29.54 \u00b7 quick LP certificate 26.49 \u00b7 "
                  "exact least cost 22.60 in gold, \u201c40% cheaper than uniform \u00b7 42% cheaper than where "
                  "cases live\u201d. Rings on the network show the plan: B1 80%, B4 38.9%, B5 15.7%, "
                  "B3 10.6%, B2 0, B6 0; the R\u2080 gauge falls from 1.214 to 0.950 and on \u201ccertifies\u201d "
                  "a seal reads \u201cgap < 10\u207b\u2076\u201d."),
    dict(id="4.7", scene="s4", gap=0.7, text="And a CUSUM alarm adds up small weekly rises, so warnings come sooner.",
         gold=["warnings come sooner"],
         onscreen="Panel \u201cCOMPUTING \u00b7 EARLY WARNING\u201d: S\u209c = max(0, S\u209c\u208b\u2081 + x\u209c "
                  "\u2212 k\u209c), alarm when S\u209c \u2265 h, delay \u2264 \u2308h/\u03b4\u2309. One simulated "
                  "season: weekly bars and S\u209c climbing over h. Bars: average alarm delay after onset, "
                  "CUSUM 4.84 weeks vs single-week rule 6.52 weeks (same 5% yearly false-alarm rate, "
                  "5,000 simulated seasons, test network)."),
    dict(id="4.8", scene="s4", gap=0.7, text="Twelve results, proven, then verified.",
         gold=["proven", "verified"], hold=1.4,
         onscreen="\u201c12 results = 12 propositions\u201d: twelve tiles get a proof mark \u220e on \u201cproven\u201d "
                  "and a check \u2713 on \u201cverified\u201d ({w:5}); chips V1\u2013V9 list the checks "
                  "(R\u2080 vs numerical next-generation matrix, 300 instances, error 5.3\u00d710\u207b\u00b9\u2075; "
                  "least cost vs grid and SLSQP, 120/120; CUSUM run length vs Monte Carlo, 6/6). "
                  "\u201cEach proven on paper, then checked against independent code on synthetic instances "
                  "\u00b7 no field data\u201d. The tiles implode into a glowing core."),
    dict(id="4.9", scene="s4", gap=1.0, text="BANTA-Y will not kill a single mosquito.", big=True,
         gold=["a single mosquito"],
         onscreen="Conclusion. A boom at {boom} clears the screen to a plain background. The line appears "
                  "large, with \u201ca single mosquito\u201d in gold. The large text is its subtitle."),
    dict(id="4.10", scene="s4", text="But once cases are reported, it will tell the brigade where to go first, and how much is enough.",
         big=True, gold=["where to go first", "how much is enough"], hold=0.6,
         onscreen="Appears under it in two rows, with \u201cwhere to go first\u201d and \u201chow much is "
                  "enough\u201d in gold. Both lines then fade out."),
    dict(id="4.11", scene="s4", gap=1.9, pause=True, text="An address tells you where the sick live.", big=True,
         gold=[],
         onscreen="[pause] The screen is empty for a moment. Then the line appears, with the BANTA-Y logo and "
                  "name below."),
    dict(id="4.12", scene="s4", gap=0.5, text="Where people go tells you where dengue goes.", big=True,
         gold=["where dengue goes"], hold=1.6,
         onscreen="Lands in large gold type with a final hit; \u201cwhere dengue goes\u201d is underlined. "
                  "Hold silence. At {title} the title card follows."),
]

TITLE_LEN = 10.0
PAPER_TITLE = ("Where People Go, Dengue Goes: A Verified Mobility-Coupled Network Model for "
               "Ranking Dengue Hotspots, Issuing Early Warnings, and Allocating Vector Control "
               "at Least Cost in Albay")


def words(text):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", text))


def read_time(text):
    w = words(text)
    breaks = len(re.findall(r"[,:;]", text))
    return round(0.36 * w + 0.2 * breaks + 0.25, 1)


def fmt(t):
    m = int(t // 60)
    s = t - 60 * m
    return f"{m}:{s:04.1f}"


def build():
    res = json.load(open(RES))
    d1 = res["d1"]
    t = 0.0
    out_lines = []
    scene_bounds = {}
    prev_scene = None
    for L in LINES:
        if L["scene"] != prev_scene:
            if prev_scene is not None:
                scene_bounds[prev_scene][1] = t
            scene_bounds[L["scene"]] = [t, None]
            prev_scene = L["scene"]
        gap = L.get("gap", 0.55)
        start = round(t + gap, 1)
        rt = read_time(L["text"])
        finish = round(start + rt, 1)
        w = words(L["text"])
        toks = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", L["text"])
        # time of each word: linear inside the read time
        wt = [round(start + rt * (i / max(w, 1)) * 0.95, 2) for i in range(w)]
        out_lines.append(dict(id=L["id"], scene=L["scene"], text=L["text"], words=w,
                              start=start, finish=finish, read=rt, word_times=wt, tokens=toks,
                              gold=L.get("gold", []), big=L.get("big", False),
                              pause=L.get("pause", False), onscreen_raw=L["onscreen"]))
        t = finish + L.get("hold", 0.0)
    t = round(t + 0.4, 1)
    scene_bounds[prev_scene][1] = t
    title_start = t
    end = round(title_start + TITLE_LEN, 1)

    scenes = []
    for i, S in enumerate(SCENES):
        a, b = scene_bounds[S["id"]]
        a = 0.0 if i == 0 else a
        sl = [l for l in out_lines if l["scene"] == S["id"]]
        scenes.append(dict(S, start=round(a, 1), end=round(b, 1), words=sum(l["words"] for l in sl)))
    # make scenes contiguous
    for i in range(1, len(scenes)):
        scenes[i]["start"] = scenes[i - 1]["end"]

    L = {l["id"]: l for l in out_lines}
    boom = round(L["4.9"]["start"] - 0.45, 2)

    # title-card sub-timeline (absolute seconds)
    T = title_start
    glyphs = ["B", "A", "N", "T", "A", "-", "Y"]
    letter_land = [round(T + 1.05 + 0.13 * i + 0.32, 3) for i in range(len(glyphs))]
    title = dict(start=T, end=end, glyphs=glyphs, letter_land=letter_land,
                 shine=round(letter_land[-1] + 0.25, 2),
                 lines_in=round(T + 2.3, 2), rules=round(T + 3.6, 2), leader=round(T + 4.1, 2),
                 role=round(T + 4.7, 2), others=round(T + 5.2, 2), name_glow=round(T + 6.1, 2),
                 fade=round(end - 0.8, 2), paper_title=PAPER_TITLE)

    sfx = []
    for s in scenes[1:]:
        sfx.append(dict(kind="whoosh", t=round(s["start"] + 0.25, 2)))
    sfx.append(dict(kind="drop", t=round(L["4.1"]["word_times"][6] - 0.1, 2)))
    sfx.append(dict(kind="boom", t=boom))
    sfx.append(dict(kind="softhit", t=round(L["4.12"]["start"] + 0.05, 2)))
    sfx.append(dict(kind="whoosh_soft", t=round(T + 0.1, 2)))
    for i, x in enumerate(letter_land):
        sfx.append(dict(kind="hit_big" if i == len(letter_land) - 1 else "tick", t=x))
    sfx.append(dict(kind="shine", t=title["shine"]))
    sfx.append(dict(kind="shine_soft", t=title["name_glow"]))

    # fill on-screen placeholders
    def fill(l):
        s = l["onscreen_raw"]
        s = re.sub(r"\{w:(\d+)\}", lambda m: fmt(l["word_times"][int(m.group(1)) - 1]), s)
        s = re.sub(r"\{t:\+([\d.]+)\}", lambda m: fmt(l["start"] + float(m.group(1))), s)
        s = s.replace("{boom}", fmt(boom)).replace("{title}", fmt(T))
        return s
    for l in out_lines:
        l["onscreen"] = fill(l)
        del l["onscreen_raw"]

    total_words = sum(l["words"] for l in out_lines)
    tl = dict(
        title="BANTA-Y rationale video v1",
        video="BANTA-Y_Rationale_Video_v1_MCS_No_Narration.mp4",
        fps=30, width=1920, height=1080, duration=end,
        total_words=total_words, scenes=scenes, lines=out_lines,
        boom=boom, title_card=title, sfx=sfx,
        d1=dict(
            ids=[r["id"] for r in d1["rows"]], desc=[r["desc"] for r in d1["rows"]],
            residents=[r["residents"] for r in d1["rows"]], P=d1["P"], present=d1["present"],
            m=d1["m"], R_local=d1["R_local"], r0=d1["r0"], hom_r0=d1["hom_r0"],
            r0_no_movement=d1["r0_no_movement"], shares=d1["shares"], case_share=d1["case_share"],
            kappa=d1["kappa"], strategies=d1["strategies"], inversion=d1["inversion"],
            cusum=d1["cusum"], pos=[[0.0, 0.0], [1.5, 0.5], [3.0, -1.0], [6.0, 4.0], [-4.0, -3.0], [2.0, -5.0]],
        ),
        verification=res["verification"],
    )
    with open(os.path.join(HERE, "timeline.json"), "w") as f:
        json.dump(tl, f, indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, "timeline.js"), "w") as f:
        f.write("window.TL = " + json.dumps(tl, ensure_ascii=False) + ";\n")
    # SRT of the narration (subtitles), for reference
    with open(os.path.join(HERE, "subtitles.srt"), "w") as f:
        for i, l in enumerate(out_lines, 1):
            def srt(x):
                h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
                return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
            f.write(f"{i}\n{srt(l['start'])} --> {srt(l['finish'] + 0.4)}\n{l['text']}\n\n")
    print(f"duration {fmt(end)} ({end:.1f} s), words {total_words}, title at {fmt(T)}, boom {fmt(boom)}")
    for s in scenes:
        print(f"  {s['id']} {s['name']:<26} {fmt(s['start'])}-{fmt(s['end'])} "
              f"{s['end'] - s['start']:5.1f} s {s['words']:4d} words "
              f"{s['words'] / (s['end'] - s['start']):.2f} w/s")
    for l in out_lines:
        print(f"  {l['id']:<5} {fmt(l['start'])} {fmt(l['finish'])} {l['read']:4.1f}s {l['words']:3d}w  {l['text']}")


if __name__ == "__main__":
    build()

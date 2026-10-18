"""Final defense decks for LIGTA-S and BANTA-Y.

LIGTA-S: the finished content deck gets two more slides (How MCS Comes into Play, and the
Sustainable Development Goals with the official goal icons) and the rationale-video opening.
BANTA-Y: built from the same template design, with the same two slides and the video opening.

Run: python3 finalize_decks.py [ligtas|bantay]
(set REFERENCE_DECK to the MAP-A defense deck if it is not in tools/assets)
"""

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

from pptx import Presentation  # noqa: E402
from pptx.util import Pt  # noqa: E402

import deckkit as K  # noqa: E402

# the team's MAP-A defense deck with the rationale-video opening (slides 2-4 are copied)
REF = os.environ.get("REFERENCE_DECK", os.path.join(HERE, "assets", "MAP-A-Proposal-Defense_WITH_RATIONALE.pptx"))
ICONS = os.path.join(HERE, "assets", "sdg")
LIG = os.path.join(R, "safe-shelter-open-schools")
BAN = os.path.join(R, "where-people-go-dengue")
LIG_BASE = os.path.join(LIG, "slides", "LIGTA-S_Safe-Shelter-Open-Schools_PR2_no-video.pptx")


def find(prs, words):
    for i, s in enumerate(prs.slides):
        t = " ".join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame).upper()
        if all(w in t for w in words):
            return i
    return -1


def insert_video(content, out, brand, lines):
    vid = os.path.join(R, brand[1], "video", "%s_Rationale_Video_v1_MCS_No_Narration.mp4" % brand[0])
    poster = os.path.join(R, brand[1], "video", "%s_Title_Page_1920x1080.png" % brand[0])
    subprocess.run([sys.executable, os.path.join(HERE, "insert_video_slides.py"), content, REF, vid, poster, out] + lines,
                   check=True)


# ---------------------------------------------------------------------------
def ligtas():
    prs = Presentation(LIG_BASE)
    src = prs.slides[find(prs, ["SIGNIFICANCE OF THE STUDY"])]
    mcs = K.mcs_slide(prs, src,
                      "Mathematics states the problem exactly, computation solves it at scale, and science grounds it in open data.",
                      [("M", "Mathematical",
                        "Roads become a graph G = (N, E) with travel times and capacities; shelters become three tiers; "
                        "the law's order of priorities becomes a lexicographic minimum-cost flow. Ten propositions are proven.",
                        r"\max V\ \succ\ \max D\ \succ\ \min Y\ \succ\ \min O\ \succ\ \min \textstyle\sum_e \tau_e x_e"),
                       ("C", "Computational",
                        "An exact flow solver returns the plan in seconds; a time-expanded network with bisection gives the "
                        "clearance time; a greedy rule sites Ligtas Pinoy Centers with a 63.2% guarantee.",
                        r"T^{*}=\min\{\,T : F(T)=D\,\},\qquad f(S_g)\ge (1-1/e)\,f(S^{*})"),
                       ("S", "Sciences",
                        "Inputs come from PSA, DepEd, PHIVOLCS and the Sphere standard of 3.5 m² per person. Every number is "
                        "reproduced by one seeded script, and test-network results are labelled synthetic.",
                        r"\text{cap}_s=\Big\lfloor \frac{F_s}{3.5\ \text{m}^2}\Big\rfloor,\qquad K_s=\Big\lceil \frac{y_s}{18}\Big\rceil")],
                      "10 results, proven, then verified:  300/300 plans  ·  660/660 networks  ·  4,796 checks  ·  0 violations",
                      os.path.join(LIG, "slides", "eq"))
    K.notes(mcs, "This is where MCS comes into play. Mathematics turns the evacuation into a graph and a lexicographic flow; "
                 "computation solves it exactly and fast; science keeps it grounded in public data and independent checks.")
    sdg = K.sdg_slide(prs, src, "Five goals, one plan: shelter everyone, the vulnerable first, and keep classrooms open.",
                      [(11, "SDG 11.5", "Fewer people affected by disasters: every evacuee gets a shelter, in time."),
                       (13, "SDG 13.1", "Resilience to climate hazards: clearance time and lahar bridges planned before the rain."),
                       (4, "SDG 4.a", "Safe learning environments: the fewest classrooms closed, so classes keep meeting."),
                       (10, "SDG 10.2", "Inclusion: vulnerable residents placed first, in accessible shelters."),
                       (1, "SDG 1.5", "Resilience of the poor: new Ligtas Pinoy Centers sited where they shelter the most.")])
    K.notes(sdg, "These are the Sustainable Development Goals the study serves. They are intended uses; none has been measured yet.")
    para = find(prs, ["FRAMEWORK", "PARADIGM", "RESEARCH PARADIGM"])
    K.move_slide(prs, mcs, para + 1)
    sig = find(prs, ["SIGNIFICANCE OF THE STUDY", "WHO BENEFITS"])
    K.move_slide(prs, sdg, sig + 1)
    content = os.path.join(LIG, "slides", "_content.pptx")
    prs.save(content)
    out = os.path.join(LIG, "slides", "LIGTA-S_Safe-Shelter-Open-Schools_PR2.pptx")
    insert_video(content, out, ("LIGTA-S", "safe-shelter-open-schools"),
                 ["A MAP SHOWS WHERE THE SHELTER IS,", "OUR MODEL SHOWS IF THERE IS ROOM.", "EVERYONE SHELTERED, CLASSROOMS LAST"])
    os.remove(content)
    return out


# ---------------------------------------------------------------------------
def bantay():
    res = json.load(open(os.path.join(BAN, "code", "results.json")))
    d1, v = res["d1"], res["verification"]
    prs = Presentation(LIG_BASE)
    old = list(prs.slides)
    title = old[0]
    src = old[find(prs, ["SIGNIFICANCE OF THE STUDY"])]
    qa = old[find(prs, ["QUESTIONS", "ANSWER"])]
    ty = old[find(prs, ["THANK YOU"])]
    eqdir = os.path.join(BAN, "slides", "eq")
    os.makedirs(eqdir, exist_ok=True)

    # title slide
    for sh in title.shapes:
        if not sh.has_text_frame:
            continue
        t = sh.text_frame.text
        if t.strip() == "LIGTA-S":
            K.set_text(sh, "BANTA-Y")
        elif t.startswith("Say it like"):
            K.set_text(sh, "Say it like bantay (BAN-tai), the Filipino word for watch or guard")
        elif t.startswith("Safe Shelter"):
            K.set_text(sh, "Where People Go, Dengue Goes: A Verified Mobility-Coupled Network Model for Ranking Dengue "
                           "Hotspots, Issuing Early Warnings, and Allocating Vector Control at Least Cost in Albay")
        elif "LIGTA-S" in t:
            for r in K.runs(sh):
                r.text = r.text.replace("LIGTA-S", "BANTA-Y")

    new = []

    def S(title_, sub, kick, note):
        s = K.skeleton(prs, src, title_, sub, kick)
        K.notes(s, note)
        new.append(s)
        return s

    X0, Y0, CW = K.X0, K.Y0, K.CW

    # 1 background
    s = S("INTRODUCTION", "Background of the Study",
          "Albay's 2026 dengue surge: cases are filed at home, but infections happen where people spend the day.",
          "Open with the 2026 numbers, then the key idea: the mosquito bites by day where people gather, but cases are filed by home address.")
    stats = [("2,179 cases · 14 deaths", "Albay, January 1 to September 12, 2026"),
             ("+84%", "over the 1,183 cases of the same months of 2025"),
             ("2,888 cases", "by September 21, 2026"),
             ("State of calamity", "declared Sept 10; public schools closed Sept 14 to 18 for cleanup and fogging")]
    w = (CW - 3 * 250000) // 4
    for i, (big, small) in enumerate(stats):
        x = X0 + i * (w + 250000)
        K.card(s, x, Y0, w, 2300000)
        K.textbox(s, x + 120000, Y0 + 180000, w - 240000, 900000, big, 30, True, K.CRIMSON)
        K.textbox(s, x + 120000, Y0 + 1150000, w - 240000, 1100000, small, 16)
    K.title_card(s, X0, Y0 + 2550000, CW // 2 - 150000, 3600000, "Most cases by municipality (by home address)",
                 ["Legazpi City 486", "Bacacay 296", "Daraga 220", "Tabaco 181", "Malilipot 171"], 22, 20)
    K.title_card(s, X0 + CW // 2 + 150000, Y0 + 2550000, CW // 2 - 150000, 3600000, "Why place matters",
                 ["Aedes aegypti bites by day and stays close to where it breeds.",
                  "People carry the virus between homes, schools, markets and workplaces (Stoddard et al., 2013).",
                  "DOH 4S: search and destroy, self-protection, seek early consultation, support fogging only in hotspots."], 22, 20)
    K.textbox(s, X0, 9600000, CW, 350000, "Sources: Daily Tribune, 2026; Philippine Information Agency (DOH 4S strategy).", 12,
              False, K.INK, italic=True)

    # 2 problem
    s = S("INTRODUCTION", "Statement of the Problem",
          "Nine problems in dengue control, each answered by one part of the model.",
          "Walk through the problems row by row; each row ends with the part of the model that answers it.")
    rows = [["No.", "Problem", "What goes wrong", "Model component"],
            ["P1", "Cases are recorded where patients live", "Cleanup goes to homes while the source persists elsewhere", "Residence-to-place inversion"],
            ["P2", "Province-wide figures look moderate", "Pockets of intense transmission stay hidden", "Local exposure numbers and bounds"],
            ["P3", "Brigades have fixed team-days", "Effort is spread evenly or by guesswork", "Least-cost control (convex program)"],
            ["P4", "Outbreaks are seen only after wards fill", "Response begins weeks late", "Poisson CUSUM alarm with proven delay"],
            ["P5", "No ranking of places to treat first", "The barangay with most cases goes first by default", "Place shares and hotspot score"],
            ["P6", "Schools and markets draw people from many barangays", "One busy place seeds cases across town", "Residence-time matrix"],
            ["P7", "The effect of a plan is unknown in advance", "Success is judged after the season", "Network reproduction number"],
            ["P8", "The rainy season multiplies mosquitoes", "A plan that works in March fails in August", "Season factor"],
            ["P9", "Officials need assurance a plan is enough", "Plans are approved without a guarantee", "Certificate and certified interval"]]
    K.table(s, X0, Y0, CW, rows, [1, 6, 7, 6], 14, 15, 640000)

    # 3 RRL
    s = S("RRL/RRS", "Related Literature and Studies",
          "Models of movement and dengue exist; none gives an Albay health office a verified, least-cost plan by place.",
          "Each row is one strand of literature and how this study uses it.")
    rows = [["Area", "Key sources", "Use in the present study"],
            ["Dengue and its vector", "Bhatt et al. (2013); WHO (2012)", "Burden and the case for vector control"],
            ["Dengue in the Philippines", "OCHA (2019); Edillo et al. (2015); RA 11332", "Reporting by address; national context"],
            ["Reproduction numbers", "Diekmann et al. (1990); van den Driessche & Watmough (2002); Smith et al. (2012)", "Next-generation matrix of the model"],
            ["Human movement", "Stoddard et al. (2009, 2013); Cosner et al. (2009)", "Residence-time (Lagrangian) coupling"],
            ["Uneven exposure", "Dye & Hasibeder (1986)", "Averages understate the risk"],
            ["Weather", "Mordecai et al. (2017); Su (2008); Sumi et al. (2017)", "Parameter ranges and the season factor"],
            ["Vector control", "Esu et al. (2010); Bowman et al. (2016)", "Control acts on mosquito numbers"],
            ["Outbreak detection", "Page (1954); Lucas (1985); Brook & Evans (1972); Hussain-Alkhateeb et al. (2018)", "CUSUM alarm and exact run length"],
            ["Matrix tools", "Horn & Johnson (2013); Overton (1988); Varah (1975)", "Bounds, convexity and the inversion error"]]
    K.table(s, X0, Y0, CW, rows, [4, 8, 6], 14, 15, 660000)

    # 4 gaps
    s = S("RRL/RRS", "Research Gap", "Six gaps remain after the review, and each one is closed by a part of the model.",
          "Read each gap and the part of the model that closes it.")
    gaps = [("G1 Cases by home, infections by place", "No tool turns cases by residence into infections by place."),
            ("G2 No provincial R0 with movement", "No residence-time model of a Philippine province from open data, with bounds a barangay can compute."),
            ("G3 No least-cost allocation", "No method gives the cheapest plan that provably brings transmission below its threshold."),
            ("G4 No ranking of places", "Hotspots are named by case counts, not by how much transmission each place carries."),
            ("G5 Alarms without guarantees", "Delays and false-alarm rates of thresholds are rarely computed."),
            ("G6 No verification", "Planning tools seldom show their formulas were checked against independent code.")]
    w = (CW - 2 * 250000) // 3
    for i, (h, b) in enumerate(gaps):
        x = X0 + (i % 3) * (w + 250000)
        y = Y0 + (i // 3) * 3450000
        K.title_card(s, x, y, w, 3200000, h, b, 22, 20)

    # 5 framework
    s = S("THEORETICAL/CONCEPTUAL FRAMEWORK PARADIGM", "Conceptual Framework",
          "Three layers turn open data into dengue decisions: movement, transmission, and decision.",
          "Explain the three layers from top to bottom: where people spend the day, how dengue spreads, and what to do.")
    K.picture(s, os.path.join(BAN, "paper", "fig_framework.png"), X0, Y0, CW, 6900000)

    # 6 MCS
    mcs = K.mcs_slide(prs, src,
                      "Mathematics states the problem exactly, computation solves it at scale, and science grounds it in open data.",
                      [("M", "Mathematical",
                        "Daily movement becomes a residence-time matrix; transmission becomes a symmetric matrix whose largest "
                        "eigenvalue is the reproduction number; the cheapest control becomes a convex program. Twelve propositions are proven.",
                        r"M=\kappa\,D_N P W P^{\top},\qquad \mathcal{R}_0^2=\lambda_{\max}(S)"),
                       ("C", "Computational",
                        "An eigen-solver ranks places in under a second for 720 barangays; an interior-point method finds the "
                        "least-cost plan with a certified gap; a Markov chain gives the alarm's exact run length.",
                        r"\min_u \textstyle\sum_j c_j u_j\ \ \text{s.t.}\ \ \mathcal{R}_0(u)\le 0.95"),
                       ("S", "Sciences",
                        "Inputs come from the PSA census, DepEd schools, case bulletins and published Aedes aegypti parameters. "
                        "Every number is reproduced by one seeded script; test-network results are labelled synthetic.",
                        r"\kappa=\frac{a^2 b c\,\nu}{\mu_v(\nu+\mu_v)(\gamma+\mu_h)}")],
                      "12 results, proven, then verified:  300/300 R0 values  ·  120/120 control plans  ·  10,000 alarm checks  ·  0 violations",
                      eqdir)
    K.notes(mcs, "This is where MCS comes into play: the matrix and eigenvalue give the reproduction number, optimisation gives the "
                 "cheapest plan with a certificate, and every result was proven and checked against independent code.")
    new.append(mcs)

    # 7 significance
    s = S("SIGNIFICANCE OF THE STUDY", "Who Benefits",
          "Every team-day sent to the right place lowers transmission the most.",
          "Name each group and what the model gives them.")
    ben = [("Households and schools", "See whether the places they visit by day carry the most transmission, and when cleanup days matter."),
           ("Barangay health workers and brigades", "A ranking per team-day and a schedule of team-days per barangay."),
           ("Provincial and municipal health offices", "A monthly reproduction number, infections by place, and an alarm with a known false-alarm rate."),
           ("Budget and disaster planners", "How many team-days a stronger rainy season will need, before the rains."),
           ("DOH 4S campaign", "Search-and-destroy and hotspot fogging aimed at the places that carry transmission."),
           ("Future researchers", "An open, verified pipeline for any province and any Aedes-borne disease.")]
    for i, (h, b) in enumerate(ben):
        x = X0 + (i % 3) * (w + 250000)
        y = Y0 + (i // 3) * 3450000
        K.title_card(s, x, y, w, 3200000, h, b, 22, 20)

    # 8 SDG
    sdg = K.sdg_slide(prs, src, "Three goals, one model: target dengue where it spreads and warn before wards fill.",
                      [(3, "SDG 3.3 and 3.d", "End the epidemics of neglected tropical diseases, dengue among them, and strengthen early warning."),
                       (4, "SDG 4.a", "Safe learning environments: schools are often the places that carry the most transmission."),
                       (17, "SDG 17.18", "Open, reusable data: an Albay data set any health office can rebuild and check.")])
    K.notes(sdg, "These are the Sustainable Development Goals the study serves. They are intended uses; none has been measured yet.")
    new.append(sdg)

    # 9 objectives
    s = S("OBJECTIVES OF THE STUDY / SOP", "Objectives",
          "Build, prove, and verify a network model of dengue in Albay that follows residents through their day.",
          "Read the general objective, then the eight specific objectives.")
    objs = ["Represent barangays, residents, mosquitoes and time away as a residence-time network from open data.",
            "Derive the reproduction number and prove its threshold, symmetric form and computable bounds.",
            "Rank places by their share of transmission and prove what the ranking measures.",
            "Formulate least-cost control as a convex program, with a certificate plan and a certified gap.",
            "Recover the places of infection from cases by residence, with a proven error bound.",
            "Design an outbreak alarm with a proven delay and an exact false-alarm rate.",
            "Test each proven property against separately written reference code.",
            "Run the pipeline on a test network and state the Albay hypotheses in advance."]
    half = CW // 2 - 150000
    for c in range(2):
        K.title_card(s, X0 + c * (half + 300000), Y0, half, 6900000, "Specific objectives %d to %d" % (1 + 4 * c, 4 + 4 * c),
                     ["%d. %s" % (1 + 4 * c + i, o) for i, o in enumerate(objs[4 * c:4 * c + 4])], 22, 20)

    # 10 SOP
    s = S("OBJECTIVES OF THE STUDY / SOP", "Statement of the Problem",
          "Can open data tell where dengue spreads, how much control is enough and where, and when an outbreak begins?",
          "Read the primary question, then Q1 to Q8.")
    qs = ["Can daily movement between barangays be written as a matrix from travel times and attraction?",
          "What is the reproduction number on such a network, and can each barangay bound it?",
          "Does treating a province as well mixed ever overstate its safety?",
          "Which places carry the most transmission, and does that predict where control works fastest?",
          "Can least-cost vector control be solved exactly, and how much does it save?",
          "Can cases counted at home be traced to places of infection, and how large is the error?",
          "How quickly does a CUSUM alarm detect a rise, and how often does it sound falsely?",
          "Do the proofs hold against separate code, and what does the pipeline show on a test network?"]
    for c in range(2):
        K.title_card(s, X0 + c * (half + 300000), Y0, half, 6900000, "Questions Q%d to Q%d" % (1 + 4 * c, 4 + 4 * c),
                     ["Q%d. %s" % (1 + 4 * c + i, q) for i, q in enumerate(qs[4 * c:4 * c + 4])], 22, 20)

    # 11 hypotheses
    s = S("HYPOTHESES", "Fixed in Advance", "Eight model hypotheses for the Albay open-data instance, each with its decision rule.",
          "These are tested on the Albay instance, not on the test network.")
    hyp = [["Code", "Hypothesis and decision rule"],
           ["H1", "Network R0 exceeds the provincial-average value by at least 10% (bootstrap interval above 1.10)."],
           ["H2", "In most municipalities with 10+ barangays, the top transmission share sits at a central school or market."],
           ["H3", "In at least half the municipalities, the top barangay by cases is not the top by inferred infections."],
           ["H4", "The least-cost plan costs at least 25% less than uniform control in most municipalities."],
           ["H5", "The certificate plan costs at most 30% more than the least-cost plan."],
           ["H6", "On 2026 data, the CUSUM alarm sounds before the single-week rule in at least 12 of 18 municipalities."],
           ["H7", "The ranking of places is stable across sensitivity sweeps (Spearman's rho above 0.8)."],
           ["H8", "Monotonicity is exact by Propositions 7 and 10; any violation is treated as a data error."]]
    K.table(s, X0, Y0, CW, hyp, [1, 12], 16, 17, 760000)

    # 12 methodology design
    s = S("METHODOLOGY", "Research Design", "Fully computational: every number comes from a proof, a declared parameter, a public report, or a test network.",
          "Go through the eight steps left to right.")
    steps = [("1 Barangays", "Census populations and barangay centers."), ("2 Travel and attraction", "Travel times from the companion model; schools, markets, jobs."),
             ("3 Residence-time matrix", "Share of biting hours in each place."), ("4 Mosquitoes", "Survey indices to adults per resident."),
             ("5 Transmission", "R0, local exposure numbers, place shares."), ("6 Control", "Five strategies to the same target; season factor."),
             ("7 Places and alarms", "Inversion of cases; CUSUM on weekly counts."), ("8 Verification", "Every proposition checked against independent code.")]
    w4 = (CW - 3 * 250000) // 4
    for i, (h, b) in enumerate(steps):
        x = X0 + (i % 4) * (w4 + 250000)
        y = Y0 + (i // 4) * 3450000
        K.title_card(s, x, y, w4, 3200000, h, b, 22, 20)

    # 13 model equations
    s = S("METHODOLOGY", "The Model", "From where people spend the day to the reproduction number and the places that carry it.",
          "Explain each equation in one sentence: time away, people present, the two-generation matrix, the bounds, the shares.")
    eqs = [("Where residents spend the day", r"p_{ii}=1-\omega_i,\qquad p_{ij}=\omega_i\,\frac{A_j e^{-\beta T_{ij}}}{\sum_{k\neq i}A_k e^{-\beta T_{ik}}}"),
           ("People present and mosquito density", r"\tilde N_j=\textstyle\sum_k p_{kj}N_k,\qquad m_j=V_j/\tilde N_j"),
           ("Reproduction number", r"M=\kappa\,D_N P W P^{\top},\qquad \mathcal{R}_0^2=\lambda_{\max}(S)"),
           ("Bounds and place shares", r"\min_i \mathcal{R}_i\le \mathcal{R}_0^2\le \max_i \mathcal{R}_i,\qquad s_j=\frac{\kappa w_j (q_j^{\top}v)^2}{\lambda}")]
    for i, (h, tex) in enumerate(eqs):
        x = X0 + (i % 2) * (half + 300000)
        y = Y0 + (i // 2) * 3450000
        K.card(s, x, y, half, 3200000)
        K.textbox(s, x + 150000, y + 90000, half - 300000, 520000, h, 20, True, K.CRIMSON)
        png = K.latex_dark(tex, os.path.join(eqdir, "m%d.png" % i))
        K.picture(s, png, x + 200000, y + 800000, half - 400000, 2200000)

    # 14 control, inversion, alarm
    s = S("METHODOLOGY", "Control, Infection Places, Alarm", "Three decision tools, each with a guarantee.",
          "Explain the control program, the inversion with its error bound, the alarm, and the season factor.")
    eqs = [("Least-cost vector control (convex)", r"\min_u \textstyle\sum_j c_j u_j\quad \text{s.t.}\quad \mathcal{R}_0(u)\le r,\ \ 0\le u_j\le \bar u_j"),
           ("Infections by place from cases by residence", r"y=P z,\qquad \|\hat z-z\|_\infty\le \frac{\|\varepsilon\|_\infty}{\min_i(2p_{ii}-1)}"),
           ("Poisson CUSUM alarm", r"S_t=\max\{0,\ S_{t-1}+x_t-k_t\},\qquad \text{alarm when } S_t\ge h"),
           ("Season factor", r"\mathcal{R}_0(\varsigma)=\sqrt{\varsigma}\ \mathcal{R}_0(1)")]
    for i, (h, tex) in enumerate(eqs):
        x = X0 + (i % 2) * (half + 300000)
        y = Y0 + (i // 2) * 3450000
        K.card(s, x, y, half, 3200000)
        K.textbox(s, x + 150000, y + 90000, half - 300000, 520000, h, 20, True, K.CRIMSON)
        png = K.latex_dark(tex, os.path.join(eqdir, "c%d.png" % i))
        K.picture(s, png, x + 200000, y + 800000, half - 400000, 2200000)

    # 15 test network
    s = S("METHODOLOGY", "Test Network D1", "Test network D1: a synthetic town of six barangays used to check every step (not Albay data).",
          "Introduce the six barangays; B1 has the central school and the public market.")
    rows = [["Brgy", "Description", "Residents", "Mosquitoes per resident", "Share of day away", "Team-days for full control"]]
    for r in d1["rows"]:
        rows.append([r["id"], r["desc"], "{:,}".format(r["residents"]), "%.1f" % r["mhat"], "%.2f" % r["away"], "%.2f" % r["cost"]])
    K.table(s, X0, Y0, 10200000, rows, [2, 9, 4, 5, 4, 5], 13, 13, 700000)
    K.picture(s, os.path.join(BAN, "code", "figures", "fig_d1_network.png"), X0 + 10500000, Y0, CW - 10500000, 5600000)

    # 16 results: where transmission happens
    s = S("RESULTS AND DISCUSSION", "Where Transmission Happens",
          "Homes point to B2, but 42.6% of transmission happens at B1, the school and the market (test network D1).",
          "Contrast the two percentage columns: cases by home versus transmission by place.")
    K.picture(s, os.path.join(BAN, "code", "figures", "fig_d1_shares.png"), X0, Y0, 10600000, 6600000)
    tiles = [("R0 = %.3f" % d1["r0"], "network reproduction number"),
             ("%.1f%%" % (100 * d1["shares"][0]), "of transmission at B1 (school + market)"),
             ("%.1f%%" % (100 * d1["case_share"][1]), "of cases filed at B2 (residential)"),
             ("%.3f" % d1["iso_r0"][0], "R0 of B1 if nobody moved")]
    for i, (big, small) in enumerate(tiles):
        y = Y0 + i * 1700000
        K.card(s, X0 + 10900000, y, CW - 10900000, 1550000)
        K.textbox(s, X0 + 11050000, y + 100000, CW - 11200000, 700000, big, 30, True, K.CRIMSON)
        K.textbox(s, X0 + 11050000, y + 820000, CW - 11200000, 650000, small, 16)

    # 17 results: least cost
    s = S("RESULTS AND DISCUSSION", "Least-Cost Vector Control",
          "The certified least-cost plan needs 40% fewer team-days than spraying everywhere (test network D1).",
          "Read the five strategies; the least-cost plan is cheapest and certified.")
    st = d1["strategies"]
    names = [("uniform", "Spray everywhere equally"), ("case_residence", "Spray where cases live"), ("place_share", "Place-share heuristic"),
             ("certificate", "Quick certificate (LP)"), ("exact", "Least cost (certified)")]
    rows = [["Strategy", "B1", "B2", "B3", "B4", "B5", "B6", "Team-days", "R0 reached"]]
    for k, lab in names:
        rows.append([lab] + ["%.0f%%" % (100 * u) for u in st[k]["u"]] + ["%.2f" % st[k]["cost"], "%.3f" % st[k]["r0"]])
    K.table(s, X0, Y0, CW, rows, [6, 2, 2, 2, 2, 2, 2, 3, 3], 15, 15, 700000)
    seas = "  ·  ".join("factor %.1f: %.1f" % (r["s"], r["cost"]) for r in d1["season"])
    K.title_card(s, X0, Y0 + 4500000, CW, 2300000, "Season factor and the team-days needed",
                 [seas, "Below a season factor of %.2f, dengue cannot take hold in D1; each rise of 0.2 adds about 10 to 12 team-days." % (1 / d1["r0_sq"])], 22, 20)

    # 18 results: inversion and alarm
    s = S("RESULTS AND DISCUSSION", "Infection Places and Early Warning",
          "Cases by residence point to B2; the inversion points to B1. The CUSUM alarm warns 1.7 weeks sooner (test network D1).",
          "Read the inversion table, then the alarm delays at the same 5% false-alarm rate.")
    inv = d1["inversion"]
    rows = [["Brgy", "Cases by residence", "Infections by place (truth)", "Infections by place (inferred)"]]
    for i, r in enumerate(d1["rows"]):
        rows.append([r["id"], str(inv["cases_by_residence"][i]), "%.1f" % inv["infections_by_place_true"][i], "%.1f" % inv["infections_by_place_inferred"][i]])
    K.table(s, X0, Y0, 8300000, rows, [2, 4, 5, 5], 14, 14, 640000)
    K.picture(s, os.path.join(BAN, "code", "figures", "fig_cusum.png"), X0 + 8600000, Y0, CW - 8600000, 4600000)
    cu = d1["cusum"]
    K.title_card(s, X0, Y0 + 4800000, CW, 2100000, "Mean weeks from outbreak start to alarm (5,000 simulated years, same 5% false-alarm rate)",
                 ["CUSUM: %.2f weeks (median %g)   ·   single-week threshold: %.2f weeks (median %g)   ·   neither missed an outbreak"
                  % (cu["delay_cusum_mean"], cu["delay_cusum_median"], cu["delay_threshold_mean"], cu["delay_threshold_median"])], 22, 20)

    # 19 verification
    s = S("RESULTS AND DISCUSSION", "Verification", "Twelve propositions, each proven and then checked against independent code: no failures.",
          "Point to the result column: every check agreed.")
    rows = [["Property", "Independent check", "Result"],
            ["Reproduction number (Prop. 1)", "%d networks vs numerical next-generation matrix" % v["V1"]["instances"], "max difference %.1e" % v["V1"]["max_rel_err"]],
            ["Threshold (Prop. 2)", "%d Jacobians; %d simulations" % (v["V2"]["jacobian_instances"], v["V2"]["simulations"]), "%d/%d and %d/%d agree" % (v["V2"]["jacobian_agree"], v["V2"]["jacobian_instances"], v["V2"]["simulation_agree"], v["V2"]["simulations"])],
            ["Bounds (Props. 4, 5)", "%d networks" % v["V3"]["instances"], "0 violations"],
            ["Shares and gradient (Prop. 6)", "%d networks vs finite differences" % v["V4"]["instances"], "gradient error %.1e" % v["V4"]["grad_max_rel_err"]],
            ["Convexity (Prop. 7)", "{:,} pairs of plans".format(v["V5"]["checks"]), "0 violations"],
            ["Least-cost control (Props. 8, 9)", "%d grid + %d SLSQP cases" % (v["V6"]["grid_cases"], v["V6"]["slsqp_cases"]), "all consistent; gap ≤ %.1e" % v["V6"]["max_gap"]],
            ["Inversion (Prop. 11)", "%d exact + %d noisy cases" % (v["V7"]["exact_instances"], v["V7"]["noisy_instances"]), "closer to truth in %d of %d" % (v["V7"]["inverse_closer"], v["V7"]["noisy_instances"])],
            ["Alarm (Prop. 12)", "6 designs vs 20,000 runs; {:,} sequences".format(v["V8"]["delay_checks"]), "all within 95%; 0 violations"],
            ["Model solutions (Prop. 3)", "30 one-year simulations, RK4", "states ≥ 0; order %.2f" % (sum(v["V9"]["rk4_slopes"]) / 3)]]
    K.table(s, X0, Y0, CW, rows, [5, 7, 5], 15, 15, 640000)

    # 20 conclusions
    s = S("CONCLUSIONS", "What the Study Shows", "Open data and routine case reports suffice to target dengue control by place, with guarantees.",
          "Summarize the four main findings.")
    conc = [("Where it spreads", "The reproduction number is a symmetric eigenvalue; place shares rank the true hotspots (B1 42.6% vs B2 by cases)."),
            ("How much is enough", "Least-cost control is a convex program; the certified plan used 22.60 team-days, 40% below uniform spraying."),
            ("Where people got infected", "Cases by residence can be traced to places with a proven error bound when residents stay home over half the day."),
            ("When to warn", "The CUSUM alarm warned 1.7 weeks sooner than a single-week rule at the same false-alarm rate.")]
    for i, (h, b) in enumerate(conc):
        x = X0 + (i % 2) * (half + 300000)
        y = Y0 + (i // 2) * 3450000
        K.title_card(s, x, y, half, 3200000, h, b, 24, 21)

    # 21 recommendations
    s = S("RECOMMENDATIONS", "Next Steps", "From a verified model to a pilot with the Provincial Health Office.",
          "Present the five next steps in order.")
    recs = [("Build the Albay instance", "All 720 barangays with census, travel times, schools, markets and mosquito surveys."),
            ("Ask about daily movement", "A short school questionnaire to estimate where families spend the day."),
            ("Record where cases were by day", "One more line on the case form: where the patient spent most daytime hours."),
            ("Let parameters follow the weather", "Temperature-dependent biting and survival; season factor from rainfall."),
            ("Pilot the brigade allocation", "One municipality follows the least-cost plan for a season; compare with a neighbor."),
            ("Release BANTA-Y", "The offline app for health offices and brigades, with the 4S checklist.")]
    for i, (h, b) in enumerate(recs):
        x = X0 + (i % 3) * (w + 250000)
        y = Y0 + (i // 3) * 3450000
        K.title_card(s, x, y, w, 3200000, h, b, 22, 20)

    # 22 references
    s = S("REFERENCES", "Key Sources", "Key sources cited in this presentation; the full list is in the paper.",
          "No need to read; show for completeness.")
    refs = ["Bhatt, S., et al. (2013). The global distribution and burden of dengue. Nature, 496, 504-507.",
            "Brook, D., & Evans, D. A. (1972). An approach to the probability distribution of CUSUM run length. Biometrika, 59, 539-549.",
            "Cosner, C., et al. (2009). The effects of human movement on the persistence of vector-borne diseases. J. Theor. Biol., 258, 550-560.",
            "Daily Tribune. (2026a-d). Albay dengue reports, September-October 2026.",
            "Diekmann, O., Heesterbeek, J. A. P., & Metz, J. A. J. (1990). J. Math. Biol., 28, 365-382.",
            "Horn, R. A., & Johnson, C. R. (2013). Matrix analysis (2nd ed.). Cambridge University Press.",
            "Mordecai, E. A., et al. (2017). PLOS Neglected Tropical Diseases, 11(4), e0005568.",
            "Page, E. S. (1954). Continuous inspection schemes. Biometrika, 41, 100-115.",
            "Philippine Statistics Authority. (2021). 2020 Census of Population and Housing.",
            "Smith, D. L., et al. (2012). Ross, Macdonald, and a theory for mosquito-transmitted pathogens. PLOS Pathogens, 8, e1002588.",
            "Stoddard, S. T., et al. (2013). House-to-house human movement drives dengue virus transmission. PNAS, 110, 994-999.",
            "United Nations General Assembly. (2015). Transforming our world: The 2030 Agenda (A/RES/70/1).",
            "van den Driessche, P., & Watmough, J. (2002). Mathematical Biosciences, 180, 29-48.",
            "Varah, J. M. (1975). Linear Algebra and Its Applications, 11, 3-5.",
            "World Health Organization. (2012). Global strategy for dengue prevention and control 2012-2020."]
    for c in range(2):
        part = refs[:8] if c == 0 else refs[8:]
        K.textbox(s, X0 + c * (half + 300000), Y0, half, 6900000, part, 14, False, K.INK)

    # order: title, new slides, Q&A, thank you; drop the old content slides
    for s_ in old[1:]:
        if s_ is not qa and s_ is not ty:
            K.delete_slide(prs, s_)
    for i, s_ in enumerate(new):
        K.move_slide(prs, s_, 1 + i)
    content = os.path.join(BAN, "slides", "_content.pptx")
    os.makedirs(os.path.dirname(content), exist_ok=True)
    cp = prs.core_properties
    cp.title = "BANTA-Y: Where People Go, Dengue Goes"
    prs.save(content)
    out = os.path.join(BAN, "slides", "BANTA-Y_Where-People-Go-Dengue-Goes_PR2.pptx")
    shutil.copy(content, out.replace(".pptx", "_no-video.pptx"))
    insert_video(content, out, ("BANTA-Y", "where-people-go-dengue"),
                 ["HOMES SHOW WHERE DENGUE IS REPORTED,", "OUR MODEL SHOWS WHERE IT SPREADS.", "TARGETING DENGUE BY PLACE ACROSS ALBAY"])
    os.remove(content)
    return out


if __name__ == "__main__":
    which = sys.argv[1:] or ["ligtas", "bantay"]
    if "ligtas" in which:
        print(ligtas())
    if "bantay" in which:
        print(bantay())

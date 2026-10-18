::: {custom-style="Figure Para"}
![](<<HEADER>>){width=2.3in}
:::

::: {custom-style="Title Main"}
Safe Shelter, Open Schools: A Verified Network-Flow Model for Planning Evacuations in Albay by Hazard Zone, Shelter Capacity, and Vulnerability While Keeping Classrooms Open
:::

::: {custom-style="Center Bold"}
Research Category
:::

::: {custom-style="Center"}
Mathematics and Computational Sciences, Team (MCS-T)
:::

::: {custom-style="Center"}
 
:::

::: {custom-style="Center Bold"}
Researchers
:::

::: {custom-style="Center"}
Brimbuela, Peter John A.
:::

::: {custom-style="Center"}
De Asis, Dave Justin Ll.
:::

::: {custom-style="Center"}
Shin, Yeaseong
:::

::: {custom-style="Center"}
 
:::

::: {custom-style="Center Bold"}
Research Adviser
:::

::: {custom-style="Center"}
Calleja, Dick Anthony M.
:::

::: {custom-style="Center"}
 
:::

::: {custom-style="Center"}
Legazpi City Science High School
:::

::: {custom-style="Center"}
Legazpi City, Albay
:::

::: {custom-style="Center"}
Bicol Region (Region V), Philippines
:::

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

TABLE OF CONTENTS

@@TOC@@

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# ABSTRACT

::: {custom-style="Abstract Title"}
Safe Shelter, Open Schools: A Verified Network-Flow Model for Planning Evacuations in Albay by Hazard Zone, Shelter Capacity, and Vulnerability While Keeping Classrooms Open
:::

::: {custom-style="Center"}
*Brimbuela, Peter John A., De Asis, Dave Justin Ll., Shin, Yeaseong*
:::

::: {custom-style="Center"}
*Legazpi City Science High School, Legazpi City, Albay, Bicol Region (Region V)*
:::

 

After Mayon Volcano was raised to Alert Level 3 on January 6, 2026, families from its six-kilometer danger zone were housed in schools and thousands of learners lost classrooms for weeks. Philippine law allows classrooms to serve as evacuation centers only as a last resort, yet no planning tool tells local governments how many classrooms they truly need. A laptop-solvable network model built from open data sends every evacuee in a hazard zone to a reachable shelter with room, ranking vulnerable residents first, then everyone, then the fewest persons in classrooms, the fewest in school open spaces, and the least travel. Shelter capacity follows the Sphere standard of 3.5 square meters per person. A time-expanded network gives the evacuation's clearance time, with and without lahar-damaged bridges, and a coverage function locates the Ligtas Pinoy Centers now required by Republic Act No. 12076. Ten results were proven, then checked on synthetic instances against reference code written separately. The plan matched five sequential linear programs in all <<V1_N>> instances, never exceeded the proven bound on extra classrooms in <<V2_N>> exact comparisons, and the time-expanded network agreed with the Ford-Fulkerson formula in all <<V3_N>> tests. On a synthetic volcano test network, the plan closed <<E1_ROOMS_LEX>> classrooms instead of <<E1_ROOMS_BLIND>> at Alert Level 3, displacing <<E1_LEARN_LEX>> learners instead of <<E1_LEARN_BLIND>>, for <<E1_EXTRA_MIN>> more minutes of average travel. Closing the bridges of both lahar channels trapped <<E1_TRAPPED>> residents in a pocket served by one school; a new evacuation center chosen greedily inside the pocket sheltered <<E1_POCKET_SAVED>> of them, and a second cut the persons housed in classrooms from <<E1_SIT_ROOM0>> to <<E1_SIT_ROOM2>>. Public data thus suffice for planning evacuations that keep schools open, supporting SDGs 4, 11, and 13. A pilot by the Provincial Government and DepEd Albay using verified shelter inventories is recommended.

**Keywords:** evacuation planning, minimum-cost flow, flow over time, lexicographic optimization, submodular site selection

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# 1. INTRODUCTION

In 2015 the United Nations set 17 Sustainable Development Goals to be met by 2030 and pledged that no one would be left out (United Nations General Assembly [UNGA], 2015). Under target 11.5, countries are to cut the number of people killed and affected by disasters; target 13.1 calls for stronger resilience to climate-related hazards; and target 4.a seeks safe and effective learning environments for all.

In Albay the three targets meet in the same building: the public school. When Mayon Volcano was raised to Alert Level 3 on January 6, 2026, the provincial government ordered the preemptive evacuation of residents of the six-kilometer Permanent Danger Zone (Interaksyon, 2026). Within days, 608 learners had been displaced from the danger zone, and 3,424 more were affected because four schools had become evacuation centers; several schools moved to modular and blended learning (Philippine Daily Inquirer, 2026a). By May 2026, 34 classrooms in three schools of Camalig were sheltering 488 families, or about 1,315 people (Daily Tribune, 2026). The same pattern followed the June 2023 unrest, when more than 19,000 people from 26 barangays stayed in 26 evacuation centers and over 20,000 were still displaced in August (ReliefWeb, 2023).

The law already sets a priority. Republic Act No. 10821 (2016) allows a school to serve as an evacuation center only when no other suitable space is available, and Department of Education guidance cited in 2026 asks that gymnasiums and other open spaces be used before classrooms, which are a last resort, and that school use stay within fifteen days unless the local government documents why (Schools Division Office of Muntinlupa City, 2026). Republic Act No. 12076 (2024), the Ligtas Pinoy Centers Act, now requires an evacuation center in every city and municipality. What the law cannot say is how many classrooms a given evacuation actually needs, which families should go where so that the fewest classrooms close, and where a new Ligtas Pinoy Center would free the most classrooms.

Here those questions are posed as problems of mathematics and computation. The barangays, roads, shelters, and classrooms form a network; each hazard alert defines a scenario; and the "best evacuation plan" is the solution of a minimum-cost flow problem whose priorities come from the law: protect the vulnerable first, shelter everyone, and only then use classrooms, as few as possible.

## 1.1 Statement of the Problem

Two viewpoints anchor the study: that of the evacuee and that of the school. Table 1 sets out the difficulties a family, a barangay captain, a school head, or a disaster officer in Albay faces during an evacuation, and names the model component designed for each.

::: {custom-style="Paper Caption"}
**Table 1.** Evacuation and sheltering problems taken up in this study, each paired with the model component that responds to it.
:::

| No. | Problem | What happens | Model component that responds |
|:---|:----------------------|:----------------------|:----------------------------|
| P1 | The nearest evacuation center is already full | Families are turned away and travel again | Shelter capacity from floor area (Def. 4); capacity constraints of the plan (Def. 7) |
| P2 | Classrooms are opened before gymnasiums and halls | Learners lose class days that a better plan would have kept | Shelter tiers and the lexicographic plan (Defs. 5, 8; Props. 1 to 3) |
| P3 | Evacuees are spread thinly over many classrooms | More rooms close than the number of evacuees requires | Classroom packing and its bound (Def. 9; Prop. 4) |
| P4 | Older persons, persons with disability, pregnant women, and small children reach a shelter they cannot use | Vulnerable residents wait or are moved twice | Vulnerable class, accessible shelters, and the vulnerable-first level (Defs. 2, 6; Prop. 2) |
| P5 | No one knows how long the whole evacuation will take | The order to leave comes too late | Time-expanded network and clearance time (Defs. 10, 11; Props. 6 to 8) |
| P6 | A lahar or flood takes out a bridge | Residents are cut off or must detour | Closure scenarios and bridge effects (Defs. 1, 12; Prop. 9) |
| P7 | A higher alert level brings more evacuees | Plans made for one alert level fail at the next | Nested scenarios and alert-level monotonicity (Def. 1; Prop. 5) |
| P8 | Local governments must build Ligtas Pinoy Centers but do not know where | Money goes where it frees few classrooms | Coverage function and greedy site selection (Defs. 13, 14; Prop. 10) |
| P9 | Planners compare plans by feel | No common measure of what a plan costs learners | Classrooms closed, learners displaced, and classroom-days (Def. 9) |
| P10 | The data are scattered across agencies | No machine-readable picture of shelters and schools | Open-data register and inventory schema (Appendices A to C) |

## 1.2 Objectives of the Study

**General objective.** The study set out to construct a network model, prove it correct, and verify it by computation. The model should send every evacuee in an Albay hazard zone to a reachable shelter with room, serve vulnerable residents first, and close as few classrooms as possible. It should also measure how long the evacuation takes to clear and how much new evacuation centers are worth.

**Specific objectives.** To reach that aim, the study set out to:

1. assemble, from open data, a model of hazard scenarios, evacuee origins, roads with their travel times and capacities, and shelters sized by a published space standard;
2. express the shelter plan as a minimum-cost flow ordered by the priorities of Republic Act No. 10821, and prove that the plan is integral, lexicographically optimal, and able to protect the vulnerable without denying anyone a place;
3. bound how far the plan's count of closed classrooms can exceed the true minimum, and prove that raising the alert level never frees classrooms;
4. find the exact clearance time of an evacuation on a time-expanded network, and prove a lower bound that does not need that network;
5. quantify, with proven monotonicity, how closing lahar-channel bridges and adding shelters alter the plan and the clearance time;
6. choose sites for Ligtas Pinoy Centers with a proven guarantee on the added coverage;
7. test each proven property numerically on synthetic instances by comparison with reference code written independently; and
8. run the complete pipeline on a small synthetic volcano test network and pre-register the hypotheses for later testing on the open-data instance of Albay.

## 1.3 Research Questions

**Primary question.** Imagine that Albay's hazard zones, barangays, roads, schools, and evacuation centers are captured in one machine-readable model drawn entirely from public sources. For a given alert level, how can every evacuee be assigned to a shelter so that vulnerable residents are protected first, everyone is sheltered, and the fewest classrooms close, and how long does such an evacuation take?

Eight subsidiary questions, aligned with the specific objectives, refine it (Table 2).

**Q1.** Can shelter capacity, hazard zones, and travel times be built from open registers in a form that a laptop can compute with?

**Q2.** Can the priorities of Republic Act No. 10821 be written as a single minimum-cost flow, and is its solution integral and lexicographically optimal?

**Q3.** Does placing vulnerable residents first ever reduce the total number of people who can be sheltered?

**Q4.** How far can the number of classrooms closed by the plan be from the true minimum, and does a higher alert level ever free classrooms?

**Q5.** Can the clearance time of an evacuation be computed exactly, and how close is a bound that needs only one static flow?

**Q6.** Which bridges and closures matter for the clearance time, and do closures ever shorten it?

**Q7.** Where would a new Ligtas Pinoy Center shelter the most evacuees outside classrooms, and how close to the best choice is a simple greedy rule?

**Q8.** Do the proven properties hold when checked against independent code, and what does the full pipeline show on a small worked instance?

::: {custom-style="Paper Caption"}
**Table 2.** Links between the specific objectives, the research questions, the supporting results, and their verification.
:::

| Specific objective | Research questions | Model parts and results | Verification |
|:----------------|:-------|:--------------------|:----------------|
| 1. Hazards, origins, roads, shelters | Q1 | Defs. 1 to 6 | Tables 10, 11; Appendix A |
| 2. Lexicographic shelter plan | Q2, Q3 | Defs. 7, 8; Props. 1 to 3 | Tables 7, 12 |
| 3. Classrooms and alert levels | Q4 | Def. 9; Props. 4, 5 | Tables 7, 12, 13 |
| 4. Clearance time | Q5 | Defs. 10, 11; Props. 6 to 8 | Tables 7, 9, 14 |
| 5. Closures and new shelters | Q6 | Def. 12; Prop. 9 | Tables 7, 15 |
| 6. Ligtas Pinoy Center siting | Q7 | Defs. 13, 14; Prop. 10 | Tables 7, 16 |
| 7. Verification | Q8 | Section 3.3 | Tables 7 to 9 |
| 8. Worked instance and hypotheses | Q8 | Sections 3.5, 3.6 | Tables 10 to 17 |

## 1.4 Review of Related Literature

### 1.4.1 Evacuation as a Network Problem

In mathematical evacuation models, a region is a network: nodes stand for places, arcs for roads, and people form a flow that must travel from dangerous nodes to safe ones (Hamacher & Tjandra, 2002). Two families of models are used. Static models assign each origin to a destination and minimize a total cost such as travel time. Dynamic models add the clock: every road can carry only so many people per minute, and people take time to cross it, so the question becomes how many people can reach safety by a given time.

### 1.4.2 Flows over Time

Ford and Fulkerson (1958) showed that the largest number of units that can be sent from one source to one sink by a time limit, when each arc has a capacity per period and a transit time, can be found from a single static minimum-cost flow, repeated over time. Their book made the time-expanded network a standard tool: one copy of every node for each period, with arcs that move forward in time (Ford & Fulkerson, 1962). Many sources with fixed supplies and many sinks with limited room lead to the quickest transshipment problem, which Hoppe and Tardos (2000) solved in polynomial time with a far more involved method. Skutella (2009) surveys these results. For an evacuation measured in whole minutes, the time-expanded network gives the exact answer with nothing more than a maximum-flow routine, at the price of a network whose size grows with the time horizon.

### 1.4.3 Shelter Location and Allocation

Sherali et al. (1991) chose shelter locations and assigned evacuees to them for hurricanes and floods in one model, and Kongsomsaksakul et al. (2005) did the same for floods with a two-level model in which evacuees choose their own shelter. Bayram et al. (2015) balanced the total evacuation time against what each evacuee would choose for himself or herself. None of these models separates the kinds of space inside a shelter or treats a classroom as a resource whose use carries a cost to learners.

### 1.4.4 Coverage, Location, and Submodular Functions

Church and ReVelle (1974) posed the maximal covering location problem: locate a given number of sites so as to maximize the demand lying within the service standard of at least one chosen site. If the coverage function is submodular, meaning each added site brings diminishing returns, greedy selection is guaranteed to attain 63.2 percent or more of the optimal coverage (Nemhauser et al., 1978). Edmonds (1970) introduced polymatroids, the sets of vectors whose sums are bounded by a submodular function; Gale (1957) gave the condition under which supplies can be shipped through a network to demands, which links the largest flow to a minimum over cuts. Fujishige (2005) brings these results together.

### 1.4.5 Space Standards in Shelters and Schools

The Sphere Handbook sets a key indicator of 3.5 square meters of covered living space per person (Sphere Association, 2018), while noting that a smaller area may be accepted for a short time to save lives. In the Philippines a standard classroom measures 7 by 9 meters (Department of Education [DepEd], 2010), so one classroom holds 18 evacuees at the Sphere indicator. A classroom that receives even one family is closed to its class.

### 1.4.6 Schools as Evacuation Centers in the Philippines

The Philippine Disaster Risk Reduction and Management Act (Republic Act No. 10121, 2010) gives local governments the duty to plan and carry out evacuations. Republic Act No. 10821 (2016), the Children's Emergency Relief and Protection Act, restricts the use of schools as evacuation centers to cases where no other space is available. Guidance from the Department of Education cited in 2026 adds an order inside the school: gymnasiums, activity centers, and other open spaces first, classrooms last, with use limited to fifteen days for medium- and long-term displacement unless the local government documents the need, and an agreement between the local government and the school before use (Schools Division Office of Muntinlupa City, 2026). Republic Act No. 12076 (2024) now requires every city and municipality to have an evacuation center that meets minimum standards (Estrada, 2024).

### 1.4.7 Mayon Volcano and the Albay Setting

At the 2020 census, Albay counted 1,374,768 residents living in 720 barangays across 18 cities and municipalities (Philippine Statistics Authority [PSA], 2021). Mayon Volcano dominates the province. The Philippine Institute of Volcanology and Seismology keeps a six-kilometer Permanent Danger Zone around the summit and, during unrest, may extend the danger zone to seven kilometers on the southern flank (ReliefWeb, 2023). Lahars are a second hazard: in November 2006 Typhoon Durian washed old eruption deposits down the volcano, and Albay counted about 1,200 people dead and missing (Philippine Daily Inquirer, 2016). Albay answered with a "zero casualty" approach built on early warning and preemptive evacuation (Philippine Daily Inquirer, 2015). The cost of that approach is paid partly in classrooms: in 2026 alone, the January and May unrest both turned schools into shelters (Philippine Daily Inquirer, 2026a, 2026b; Daily Tribune, 2026; Philippine Star, 2026).

### 1.4.8 Vulnerable Groups in Evacuation

Older persons, persons with disability, pregnant women, and small children need ground-level, accessible space and often need transport. Their rights are set out in the Expanded Senior Citizens Act (Republic Act No. 9994, 2010), the law on the benefits of persons with disability (Republic Act No. 10754, 2016), and Republic Act No. 10821 (2016) for children. The Sphere Association (2018) asks that shelters be accessible to all. A plan that treats every evacuee alike may give the last accessible place to someone who could have climbed the stairs.

### 1.4.9 Lexicographic Optimization and Integral Flows

When goals have a strict order, a plan is lexicographically optimal if no other plan is better on the first goal, or equal on the first and better on the second, and so on. For network flows such an order can be imposed with weights large enough that one unit of a higher goal outweighs every possible change in the lower ones. A flow problem has a totally unimodular constraint matrix, so its linear program always admits an optimal solution in integers, and no person is ever divided between shelters (Ahuja et al., 1993; Schrijver, 2003).

### 1.4.10 Open Data on Hazards, Schools, and Shelters

The hazard maps of the Philippine Institute of Volcanology and Seismology and the Mines and Geosciences Bureau are public through HazardHunterPH (Philippine Institute of Volcanology and Seismology [PHIVOLCS], n.d.). The Department of Education publishes a masterlist of schools (DepEd, 2021), local governments list designated evacuation centers in their disaster plans, the Department of Social Welfare and Development reports the evacuation centers in use during each event (Department of Social Welfare and Development [DSWD], n.d.), and OpenStreetMap supplies the roads (OpenStreetMap contributors, 2026). A companion study by the same researchers built a landmark-anchored road and transit model of Albay from these sources (Brimbuela et al., 2026), and this study reuses its road layer.

## 1.5 Research Gap

Six gaps remain after this review.

* **(G1) No model counts classrooms.** Evacuation and shelter models treat a shelter as one block of capacity. None separates a gymnasium from a classroom, so none can say how many classrooms an evacuation must close, which is the quantity Republic Act No. 10821 asks to keep small.
* **(G2) No plan follows the legal order of priorities.** Philippine law and guidance give a clear order: vulnerable residents and everyone's safety first, non-school space before schools, open space before classrooms. No published plan turns that order into mathematics that can be checked.
* **(G3) No clearance time for Albay.** Preemptive evacuation needs to know how long moving everyone takes, given road capacities, and how lahar-damaged bridges change it. No open model computes this for Albay.
* **(G4) No guidance for the Ligtas Pinoy Centers.** Republic Act No. 12076 requires new evacuation centers but gives no method for placing them where they would free the most classrooms.
* **(G5) No proof that plans behave sensibly.** Planners need to know that a higher alert level never makes the plan look better and that closing a road never shortens the evacuation. Without proofs, a single counter-intuitive output can discredit a tool.
* **(G6) No open inventory.** Shelter floor areas, classroom counts, and accessibility are scattered across agencies, and no machine-readable inventory joins them.

## 1.6 Contributions of the Study

* **C1. A shelter model that knows classrooms.** Sections 2.4 and 2.5 split every shelter into non-school space, school open space, and classrooms, with capacities from the Sphere indicator and the standard classroom.
* **C2. A plan that follows the law.** Section 2.6 writes the legal order of priorities as a single minimum-cost flow, and Propositions 1 to 3 prove that it is integral, that protecting vulnerable residents never costs anyone a place, and that the order is met exactly.
* **C3. A classroom guarantee.** Proposition 4 proves that packing evacuees into full classrooms closes at most one more classroom per school in use than the true minimum, and Proposition 5 proves that a higher alert level never frees classrooms.
* **C4. An exact clearance time with a quick bound.** Section 2.8 computes the clearance time on a time-expanded network, and Propositions 6 to 8 prove it exact, show that bisection finds it, and give a lower bound from one static flow.
* **C5. Closures and new shelters with guarantees.** Proposition 9 proves that closing roads never shortens the evacuation and that adding shelters never increases classroom use when everyone is already sheltered.
* **C6. Siting with a guarantee.** Proposition 10 shows that the coverage gained from new evacuation centers is submodular, which guarantees a greedy choice 63.2 percent or more of the optimum.
* **C7. A repeatable, open pipeline.** Appendix A names the public register behind every input; scripts with one fixed random seed regenerate every result (Appendix F); and verified inventories can later take the place of synthetic data with no change to the mathematics.

Section 3.2 states ten numbered results, and two of them are not new: Propositions 6 and 10 adapt known theorems of Ford and Fulkerson (1958, 1962), Gale (1957), Edmonds (1970), and Nemhauser et al. (1978) to this setting, and each heading cites its source. The other eight, Propositions 1 to 5 and 7 to 9, were developed by the researchers.

## 1.7 Scope and Delimitation

Geographically, the work is confined to Albay province and its 18 cities and municipalities; the hazards considered are those of Mayon Volcano (the Permanent and Extended Danger Zones and lahar channels) and typhoon floods. It is entirely computational. No evacuation center was visited and no evacuee was interviewed; every reported number comes from a proof, from synthetic test instances, or from a public register.

The model plans; it does not order. Decisions remain with the local disaster risk reduction and management offices, the Department of Education, and the Provincial Government. The model does not route individual vehicles, schedule trucks, or forecast eruptions; it starts from an alert level that the Philippine Institute of Volcanology and Seismology has declared. Shelter stays, food, water, and sanitation are outside its scope except through the space standard.

## 1.8 Relation to the Sustainable Development Goals

Because the SDGs are linked to one another, a single study may contribute to more than one of them (UNGA, 2015). The work reported here is computational and offers a planning tool. It has not yet been put into practice, so the paper reports no Albay value for any indicator.

The study bears most directly on two goals: Sustainable Cities and Communities (SDG 11), via target 11.5 on reducing the people affected by disasters, and Climate Action (SDG 13), via target 13.1 on resilience to climate-related hazards. The classroom measures serve SDG 4, Quality Education, through target 4.a on safe learning environments: every classroom the plan keeps open is a class that keeps meeting. The vulnerable-first level relates to SDG 10, Reduced Inequalities (target 10.2), and the siting tool to SDG 1 (target 1.5, resilience of the poor). Each of these links is a likely use of the work, not a demonstrated outcome.

::: {custom-style="Figure Para"}
![](<<FIG_SDG>>){width=6.2in}
:::

::: {custom-style="Source Line"}
SDG icons: United Nations
:::


## 1.9 How Mathematics and Computational Sciences Come into Play

This is a study in Mathematics and Computational Sciences in a precise sense: each of its three parts does work that the other two cannot.

* **Mathematics** states the problem exactly. Roads become a graph with travel times and capacities, shelters become three tiers of capacity, and the legal order of priorities becomes a lexicographic minimum-cost flow. Ten propositions then say what any plan of this kind can and cannot do.
* **Computation** turns those statements into answers. An exact flow solver produces a plan in seconds, a time-expanded network gives the clearance time by bisection, and a greedy rule sites new centers with a proven guarantee.
* **Science** keeps the work honest. Every input comes from a public register or a published standard, every proposition was tested against separately written code, and every number in Chapter 3 can be reproduced from one seeded script.

Together the three move from open data to a graph, from the graph to an algorithm, from the algorithm to numbers, and from the numbers to a plan that is both optimal and proven (Figure 1).

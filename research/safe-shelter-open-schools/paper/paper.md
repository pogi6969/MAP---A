::: {custom-style="Figure Para"}
![](/home/user/MAP---A/research/tools/assets/deped_header.png){width=2.3in}
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

 

After Mayon Volcano was raised to Alert Level 3 on January 6, 2026, families from its six-kilometer danger zone were housed in schools and thousands of learners lost classrooms for weeks. Philippine law allows classrooms to serve as evacuation centers only as a last resort, yet no planning tool tells local governments how many classrooms they truly need. A laptop-solvable network model built from open data sends every evacuee in a hazard zone to a reachable shelter with room, ranking vulnerable residents first, then everyone, then the fewest persons in classrooms, the fewest in school open spaces, and the least travel. Shelter capacity follows the Sphere standard of 3.5 square meters per person. A time-expanded network gives the evacuation's clearance time, with and without lahar-damaged bridges, and a coverage function locates the Ligtas Pinoy Centers now required by Republic Act No. 12076. Ten results were proven, then checked on synthetic instances against reference code written separately. The plan matched five sequential linear programs in all 300 instances, never exceeded the proven bound on extra classrooms in 150 exact comparisons, and the time-expanded network agreed with the Ford-Fulkerson formula in all 660 tests. On a synthetic volcano test network, the plan closed 14 classrooms instead of 40 at Alert Level 3, displacing 532 learners instead of 1,702, for 1.70 more minutes of average travel. Closing the bridges of both lahar channels trapped 450 residents in a pocket served by one school; a new evacuation center chosen greedily inside the pocket sheltered 400 of them, and a second cut the persons housed in classrooms from 920 to 570. Public data thus suffice for planning evacuations that keep schools open, supporting SDGs 4, 11, and 13. A pilot by the Provincial Government and DepEd Albay using verified shelter inventories is recommended.

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
![](/home/user/MAP---A/research/safe-shelter-open-schools/paper/fig_sdg.png){width=6.2in}
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


# 2. FRAMEWORK

Figure 1 shows the three layers of the framework. Sections 2.1 to 2.5 set out the data layer: hazard scenarios, the residents who must leave, the roads they travel, and the shelters able to receive them. Sections 2.6 and 2.7 form the planning layer, which assigns each evacuee to a shelter. Sections 2.8 to 2.10 make up the time and siting layer, which estimates how long the evacuation lasts, identifies the bridges that matter, and chooses sites for new evacuation centers.

::: {custom-style="Figure Para"}
![](/home/user/MAP---A/research/safe-shelter-open-schools/paper/fig_framework.png){width=6.3in}
:::

::: {custom-style="Figure Caption"}
**Figure 1.** How the model turns open data into an evacuation plan. The data layer is drawn in blue, the planning layer in orange, and the time and siting layer in green.
:::

## 2.1 Study Area, Hazard Zones, and Scenarios

This study covers Albay as a whole: its 18 cities and municipalities, grouped into three legislative districts (Table 3).

::: {custom-style="Paper Caption"}
**Table 3.** Land area and 2020 population of Albay's 18 local government units, by district. Population: PSA (2021); land area: PhilAtlas (n.d.).
:::

| District | Local Government Units | Population (2020) | Land Area (km²) |
|:-----|:------------------------------|---------:|--------:|
| First District | Bacacay, Malilipot, Malinao, Santo Domingo, Tiwi, Tabaco City | 395,907 | 547.88 |
| Second District | Camalig, Daraga, Manito, Rapu-Rapu, Legazpi City | 477,781 | 673.85 |
| Third District | Guinobatan, Jovellar, Libon, Oas, Pio Duran, Polangui, Ligao City | 501,080 | 1,353.18 |
| Total | 18 cities and municipalities | 1,374,768 | 2,574.91 |

Mayon Volcano rises between the First, Second, and Third Districts, and its Permanent Danger Zone touches Camalig, Daraga, Guinobatan, Legazpi City, Ligao City, Malilipot, Santo Domingo, and Tabaco City.

**Definition 1 (Hazard scenario).** A hazard scenario is a pair

$$\sigma = (Z_\sigma,\; X_\sigma)$$

EQNUM:(1)

::: {custom-style="Source Line"}
Source: this study (Definition 1)
:::

where $Z_\sigma$ is the set of active hazard zones (for example, the Permanent Danger Zone, the Extended Danger Zone, a lahar channel, or a flood zone) and $X_\sigma$ is the set of road segments closed by the hazard (for example, bridges over a lahar channel). Scenario $\sigma$ is *contained in* scenario $\sigma'$, written $\sigma \preceq \sigma'$, when $Z_\sigma \subseteq Z_{\sigma'}$ and $X_\sigma \subseteq X_{\sigma'}$.

Table 4 lists the scenarios used in this paper. Alert Level 3 follows the preemptive evacuation of the Permanent Danger Zone; Alert Level 4 adds the Extended Danger Zone; and the compound scenario adds a lahar on top of Alert Level 4, as when a typhoon strikes during an eruption.

::: {custom-style="Paper Caption"}
**Table 4.** Hazard scenarios. Zones follow the conventions of PHIVOLCS for Mayon; the compound scenario is a planning case, not a forecast.
:::

| Scenario | Active zones | Closed roads | When it applies |
|:-------|:---------------------|:----------------|:-----------------------|
| AL3 | Permanent Danger Zone (6-km radius) | none | Alert Level 3: preemptive evacuation |
| AL4 | Permanent Danger Zone and Extended Danger Zone (7 km on the southern flank) | none | Alert Level 4, or Alert Level 3 with an extended zone |
| AL4+L | as AL4, plus lahar-prone areas | every bridge over an active lahar channel | heavy rain or a typhoon during an eruption |

## 2.2 Origins and Evacuees

**Definition 2 (Origins and evacuees).** An origin $a \in A$ is a barangay or purok assembly point, with road node $o_a$, the set $\zeta_a$ of hazard zones it lies in, a population $P_a$, and a count $V_a \le P_a$ of vulnerable residents: persons aged 60 and over, children under five, persons with disability, and pregnant women. In scenario $\sigma$ the origin must evacuate

$$D_a(\sigma) = P_a \cdot \mathbf{1}\big[\zeta_a \cap Z_\sigma \neq \varnothing\big], \qquad V_a(\sigma) = V_a \cdot \mathbf{1}\big[\zeta_a \cap Z_\sigma \neq \varnothing\big]$$

EQNUM:(2)

::: {custom-style="Source Line"}
Source: this study (Definition 2)
:::

persons, of whom $V_a(\sigma)$ are vulnerable. The total is $D(\sigma) = \sum_a D_a(\sigma)$.

Origins are fixed places named in public registers, as in the companion study (Brimbuela et al., 2026); barangay populations come from the 2020 census and the vulnerable counts from the census age structure and the barangay registries kept under the laws on senior citizens and persons with disability.

## 2.3 Road Network, Travel Time, and Capacity

**Definition 3 (Road network).** $G = (N, E)$ is a directed graph built from OpenStreetMap. Each arc $e$ has a transit time $\tau_e \ge 1$ in whole time steps (one step is one minute) and a capacity $u_e$, the number of evacuees that the road and the vehicles assigned to it can move per minute. In scenario $\sigma$ the open graph is $G_\sigma = (N, E \setminus X_\sigma)$, and $T_\sigma(a, s)$ is the shortest transit time from $o_a$ to shelter $s$ on $G_\sigma$, computed by Dijkstra's (1959) algorithm.

The transit time comes from the length of the road and a speed for its class, and the capacity from its lanes and the trucks the local government assigns; both are declared parameters (Section 2.12), varied in the sensitivity sweeps of Section 3.6.

## 2.4 Shelters and the Space Standard

**Definition 4 (Shelter capacity).** A shelter $s \in S$ sits at road node $n_s$ outside every active zone. Its capacity comes from its covered, usable floor area: a space of $F$ square meters holds

$$C(F) = \left\lfloor \frac{F}{3.5} \right\rfloor, \qquad q = C(63) = 18$$

EQNUM:(3)

::: {custom-style="Source Line"}
Source: Sphere Association (2018) for 3.5 m² per person; DepEd (2010) for the 7 m by 9 m classroom
:::

persons, so a standard classroom holds $q = 18$ evacuees. A school $s$ has an open-space area $F^{open}_s$ (gymnasium, covered court, multipurpose hall), $k_s$ classrooms, and $\ell_s$ learners per classroom, its average class size; a non-school shelter has a floor area $F^{ec}_s$.

## 2.5 Shelter Tiers and Suitability

**Definition 5 (Shelter tiers).** Each shelter splits into up to three *slots*, one per tier $\iota$:

$$c^{0}_s = C\big(F^{ec}_s\big), \qquad c^{1}_s = C\big(F^{open}_s\big), \qquad c^{2}_s = q\, k_s$$

EQNUM:(4)

::: {custom-style="Source Line"}
Source: this study, based on Republic Act No. 10821 (2016) and DepEd guidance (Schools Division Office of Muntinlupa City, 2026)
:::

Tier 0 is non-school space (an evacuation center, a Ligtas Pinoy Center, a church hall, a covered court not in a school), tier 1 is school open space, and tier 2 is classrooms. The order of the tiers is the order of the law (Table 5).

::: {custom-style="Paper Caption"}
**Table 5.** Shelter tiers, their capacity, and the rule each follows.
:::

| Tier | Space | Capacity | Rule |
|:--|:--------------------|:-------------|:----------------------------|
| 0 | Non-school evacuation space | $\lfloor F^{ec}/3.5 \rfloor$ | Use first (Republic Act No. 12076; Republic Act No. 10821) |
| 1 | School gymnasium, covered court, hall | $\lfloor F^{open}/3.5 \rfloor$ | Use when non-school space is full (Republic Act No. 10821) |
| 2 | School classrooms | $18 k_s$ | Last resort; each classroom used is closed to its class |

**Definition 6 (Suitable slot).** A person of class $\kappa \in \{V, N\}$ (vulnerable or not) from origin $a$ may use slot $(s, \iota)$ in scenario $\sigma$ when

$$\phi_\sigma(a, \kappa, s) = \mathbf{1}\big[T_\sigma(a,s) \le \theta_{\max}\big] \cdot \mathbf{1}\big[\kappa = N \ \text{or}\ \alpha_s = 1\big] = 1$$

EQNUM:(5)

::: {custom-style="Source Line"}
Source: this study (Definition 6)
:::

where $\theta_{\max}$ is the longest acceptable trip (120 minutes in this paper) and $\alpha_s = 1$ when the shelter is accessible: ground level or ramped, with an accessible toilet. Shelters inside an active zone are removed before the plan is made.

## 2.6 The Shelter Plan as a Lexicographic Flow

**Definition 7 (Shelter plan).** A plan is a set of whole numbers $x_{a\kappa, s\iota} \ge 0$, one for every suitable pair, counting the persons of class $\kappa$ from origin $a$ placed in slot $(s,\iota)$, such that

$$\sum_{s,\iota} x_{aV, s\iota} \le V_a(\sigma), \qquad \sum_{s,\iota} x_{aN, s\iota} \le D_a(\sigma) - V_a(\sigma), \qquad \sum_{a,\kappa} x_{a\kappa, s\iota} \le c^{\iota}_s$$

EQNUM:(6)

::: {custom-style="Source Line"}
Source: this study; a transportation model (Ahuja et al., 1993)
:::

for every origin $a$ and every slot $(s,\iota)$.

**Definition 8 (Lexicographic order).** For a plan $x$, let $F_V(x)$ be the number of vulnerable persons placed, $F(x)$ the number of persons placed, $Y(x)$ the number in classrooms, $O(x)$ the number in school open spaces, and $\Theta(x) = \sum x_{a\kappa,s\iota}\, T_\sigma(a,s)$ the person-minutes of travel. A plan is *lexicographically optimal* when no other plan is better in the order

$$\max F_V \;\succ\; \max F \;\succ\; \min Y \;\succ\; \min O \;\succ\; \min \Theta$$

EQNUM:(7)

::: {custom-style="Source Line"}
Source: this study, following the priorities of Republic Act No. 10821 (2016)
:::

that is, no plan places more vulnerable persons; among those that tie, none places more persons; and so on down the list.

The first two levels are maximum flows. Let $F_V^*$ be the largest number of vulnerable persons that can be placed and $F^*$ the largest number of persons. The last three levels are imposed by penalties. With $T_{\max}$ the longest finite travel time,

$$M_O = D(\sigma)\, T_{\max} + 1, \qquad M_Y = D(\sigma)\,\big(M_O + T_{\max}\big) + 1$$

EQNUM:(8)

::: {custom-style="Source Line"}
Source: this study (Proposition 3)
:::

and the plan solves the minimum-cost flow in which the vulnerable classes jointly supply exactly $F_V^*$ persons, the other classes jointly supply $F^* - F_V^*$, and a person sent to slot $(s,\iota)$ costs $T_\sigma(a,s) + M_O\,\mathbf{1}[\iota = 1] + M_Y\,\mathbf{1}[\iota = 2]$. Algorithm 1 gives the steps.

::: {custom-style="Paper Caption"}
**Algorithm 1.** The school-preserving shelter plan for one scenario.
:::

```
Input : origins a with D_a, V_a; shelters with slots (s, tier, capacity);
        travel times T(a, s); limit theta_max
Output: plan x, persons per tier, classrooms closed
 1  keep only suitable pairs (Definition 6)
 2  F_V* <- max flow of vulnerable persons into accessible slots
 3  F*   <- max flow of all persons into all slots
 4  cost(a, s, tier) <- T(a, s) + M_O*[tier = 1] + M_Y*[tier = 2]   (Equation 8)
 5  solve the min-cost flow in which the vulnerable classes supply F_V*
    and the other classes supply F* - F_V* (network simplex)
 6  for every school: pack its classroom evacuees into full classrooms
 7  return x, Y(x), O(x), Theta(x), classrooms closed (Definition 9)
```

## 2.7 Classrooms Closed and Learners Displaced

**Definition 9 (Classrooms closed and learners displaced).** If a plan places $y_s$ persons in the classrooms of school $s$, packing fills one classroom before opening the next, so the classrooms closed and the learners displaced are

$$K_s = \left\lceil \frac{y_s}{q} \right\rceil, \qquad K = \sum_s K_s, \qquad L = \sum_s K_s\, \ell_s, \qquad \text{classroom-days} = K \cdot d$$

EQNUM:(9)

::: {custom-style="Source Line"}
Source: this study (Definition 9)
:::

where $d$ is the expected length of stay in days. A stay of $d$ days in $K$ classrooms costs $L \cdot d$ learner-days of face-to-face schooling.

## 2.8 Evacuation over Time

The plan says where everyone goes. It does not say how long the movement takes when many people share the same roads. For that the road network is copied once per minute.

**Definition 10 (Time-expanded network, following Ford & Fulkerson, 1962).** For a horizon $T$, the network $G^T_\sigma$ has a vertex $(v, t)$ for every node $v$ and minute $t = 0, \dots, T$; a movement arc from $(v,t)$ to $(w, t + \tau_e)$ with capacity $u_e$ for every open arc $e = (v, w)$ and every $t$ with $t + \tau_e \le T$; a waiting arc from $(v,t)$ to $(v, t+1)$ without limit; an arc from a super-source to $(o_a, 0)$ whose capacity is the number of persons the plan moves out of $a$; and, for every shelter, arcs from each $(n_s, t)$ to a shelter vertex, whose single arc to a super-sink has capacity equal to the number of persons the plan assigns to $s$. $F_\sigma(T)$ is the value of a maximum flow from the super-source to the super-sink.

**Definition 11 (Clearance time).** For a plan that moves $D'$ persons,

$$T^{*}_\sigma = \min\{\, T \ge 0 : F_\sigma(T) = D' \,\}$$

EQNUM:(10)

::: {custom-style="Source Line"}
Source: this study (Definition 11)
:::

the first minute by which every evacuee can be inside a shelter, with $T^*_\sigma = +\infty$ when some evacuees cannot reach their shelters at all. Algorithm 2 finds it.

::: {custom-style="Paper Caption"}
**Algorithm 2.** Clearance time by doubling and bisection.
:::

```
Input : open road graph, persons per origin, persons per shelter
Output: clearance time T*
 1  if a max flow with no time limit cannot move everyone: return infinity
 2  hi <- 8; while F(hi) < D': hi <- 2*hi        (F from Definition 10)
 3  lo <- -1                                      (invariant F(lo) < D' <= F(hi))
 4  while hi - lo > 1:
 5      mid <- (lo + hi) / 2, rounded down
 6      if F(mid) >= D': hi <- mid  else: lo <- mid
 7  return hi
```

## 2.9 Bridges and Channel Closures

**Definition 12 (Closure effect).** For a set $B$ of road segments, such as the bridges over one lahar channel, the closure effect on a scenario $\sigma$ with its plan held fixed is

$$\Delta_B = T^{*}_{\sigma + B} - T^{*}_{\sigma}$$

EQNUM:(11)

::: {custom-style="Source Line"}
Source: this study, adapting a link-importance measure from Jenelius et al. (2006)
:::

where $\sigma + B$ adds $B$ to the closed roads. A segment with a large $\Delta_B$ is one to protect before a typhoon and to clear first after it; $\Delta_B = +\infty$ means some evacuees are cut off from their shelters.

## 2.10 Where to Build Ligtas Pinoy Centers

**Definition 13 (Coverage outside classrooms).** For a set $B$ of shelters, each counted only with its non-classroom capacity $c^0_s + c^1_s$, and a travel-time standard $\theta$, let $\Phi_\theta(B)$ be the largest number of evacuees that can be placed in $B$ outside classrooms using only trips of at most $\theta$ minutes, a maximum flow on the network with arcs from each origin to the shelters within $\theta$ of it.

**Definition 14 (Siting gain).** Let $E$ be the existing shelters and $Q$ the candidate sites for new centers, each with a planned capacity $C_j$. The gain of building the set $S \subseteq Q$ is

$$f(S) = \Phi_\theta(E \cup S) - \Phi_\theta(E)$$

EQNUM:(12)

::: {custom-style="Source Line"}
Source: this study, a variant of the maximal covering location problem (Church & ReVelle, 1974)
:::

the number of evacuees the new centers add to those who can be sheltered outside classrooms within $\theta$. The task is to choose $|S| = k$ sites with the largest $f(S)$. Algorithm 3 makes the choice greedily, and Proposition 10 bounds its shortfall from the best possible set.

::: {custom-style="Paper Caption"}
**Algorithm 3.** Greedy selection of Ligtas Pinoy Center sites.
:::

```
Input : origins with D_a; existing shelters E; candidates Q with C_j;
        standard theta; number of sites k
Output: chosen sites S
 1  S <- empty set
 2  repeat k times:
 3      for each j in Q not in S: gain(j) <- f(S + j) - f(S)   (max flows)
 4      j* <- the j with the largest gain (smallest index on ties)
 5      S <- S + j*
 6  return S
```

## 2.11 Baselines

Two plans serve as baselines. In the *nearest-site rule*, each origin sends everyone to the nearest safe shelter site, ignoring capacity; the excess at full sites is the *overflow*, the number of people who would arrive to find no room. In the *time-only plan*, Algorithm 1 is run with $M_O = M_Y = 0$: it shelters as many people as possible, vulnerable residents first, and then minimizes travel alone, using classrooms whenever they are nearer.

## 2.12 Assumptions

* **Assumption 1 (Whole minutes).** Transit times are whole numbers of minutes, at least one. Rounding up never makes a road look faster than it is.
* **Assumption 2 (Capacity per minute).** Each road moves at most $u_e$ evacuees per minute in each direction, whatever mix of walking and riding they use. Vehicle routing and truck schedules are outside the model.
* **Assumption 3 (Order to evacuate).** All evacuees of a scenario are ready at minute zero. Staggered departures are modeled by running the plan once per wave.
* **Assumption 4 (Space standard).** Capacity follows the 3.5 square meter indicator of the Sphere Association (2018); the sweeps of Section 3.6 repeat the analysis at 4.5 square meters.
* **Assumption 5 (Divisible origins, whole persons).** Families from one origin may be placed in different shelters, but persons are not split. Keeping each family together is left to the local officer who carries out the plan.
* **Assumption 6 (Open data only).** Each number reported here is derived mathematically, set as a declared parameter, taken from a public register (Appendix A), or produced by a synthetic test instance. The study involved no shelter survey and no interviews.
* **Assumption 7 (Safe shelters).** A shelter outside every active zone is safe for the length of the stay; ashfall, which may close schools outside the danger zones, is not modeled.

## 2.13 Notation

::: {custom-style="Paper Caption"}
**Table 6.** Symbols and their meanings.
:::

| Symbol | Meaning |
|:-----------------|:---------------------------------------------|
| $\sigma$, $Z_\sigma$, $X_\sigma$ | hazard scenario; its active zones; its closed roads |
| $A$, $o_a$, $\zeta_a$ | origins; road node of origin $a$; zones it lies in |
| $P_a$, $V_a$, $D_a(\sigma)$, $V_a(\sigma)$ | population; vulnerable residents; evacuees and vulnerable evacuees in $\sigma$ |
| $G = (N, E)$, $\tau_e$, $u_e$ | road network; transit time of arc $e$; its capacity per minute |
| $T_\sigma(a,s)$, $\theta_{\max}$ | shortest travel time from $a$ to $s$; longest acceptable trip |
| $S$, $n_s$, $\alpha_s$ | shelters; road node of $s$; accessibility flag |
| $c^0_s$, $c^1_s$, $c^2_s$, $q$, $k_s$, $\ell_s$ | tier capacities; persons per classroom; classrooms; learners per classroom |
| $x_{a\kappa,s\iota}$ | persons of class $\kappa$ from $a$ placed in tier $\iota$ of $s$ |
| $F_V$, $F$, $Y$, $O$, $\Theta$ | vulnerable placed; placed; in classrooms; in school open space; person-minutes |
| $M_O$, $M_Y$ | penalties for school open space and classrooms |
| $K_s$, $K$, $L$ | classrooms closed at $s$; in all; learners displaced |
| $G^T_\sigma$, $F_\sigma(T)$, $T^*_\sigma$ | time-expanded network; evacuees sheltered by minute $T$; clearance time |
| $\Delta_B$ | change in clearance time when the roads $B$ close |
| $\Phi_\theta(B)$, $f(S)$, $Q$, $C_j$ | coverage outside classrooms; siting gain; candidate sites; their capacities |

**Sources of the equations.** Equation (3) applies the Sphere indicator and the DepEd classroom standard; Equation (6) is the classic transportation problem; Definition 10 is the time-expanded network of Ford and Fulkerson (1962); Equation (11) follows Jenelius et al. (2006); and Equation (12) follows Church and ReVelle (1974). All remaining equations are original to this study.


# 3. FINDINGS

## 3.0 Data Sources and the Integrity of Results

Each result reported below was obtained either by proof or by computing on synthetic instances. Two scripts produced the numbers: `evacmodel.py`, which implements the model of Chapter 2, and `verify_evacuation.py`, which checks it against independently written reference code and works the instance of Section 3.5. Both were run with the fixed random seed 20261017 and write every figure reported here to `results.json` (Appendix F). No number in this chapter describes a real shelter, school, road, or barangay of Albay; the worked instance is a synthetic volcano built to exercise every part of the pipeline.

## 3.1 General Methods

The analysis ran through eight stages.

**Stage 1: Hazard scenarios.** The danger zones of Mayon and the lahar channels were written as scenarios (Definition 1, Table 4).

**Stage 2: Origins.** Barangay and purok assembly points were taken as origins, with populations and vulnerable counts (Definition 2).

**Stage 3: Road network.** The road layer of the companion study (Brimbuela et al., 2026), built from OpenStreetMap, gave the arcs, their transit times, and their capacities (Definition 3).

**Stage 4: Shelter inventory.** Every shelter received a record with its floor areas, classrooms, accessibility, and tier capacities (Definitions 4 and 5; Appendix C).

**Stage 5: Shelter plan.** Algorithm 1 produced the school-preserving plan and the two baselines of Section 2.11.

**Stage 6: Evacuation over time.** Algorithm 2 computed the clearance time of each plan, with and without bridge closures, together with the lower bound of Proposition 8.

**Stage 7: Siting.** Algorithm 3 chose candidate sites for Ligtas Pinoy Centers, and the plan was recomputed with the new centers in place.

**Stage 8: Verification.** Every proven property was checked against reference code on random synthetic instances (Section 3.3), and the running time was measured (Section 3.4).

## 3.2 Theoretical Results

A classroom count is only as trustworthy as the plan that produces it, so the theory comes first.

**Proposition 1 (Plans in whole numbers).** In every scenario, some optimal solution of the minimum-cost flow in Algorithm 1 uses whole numbers only, and the network simplex method finds one of that kind. No evacuee is ever split between shelters.

*Proof.* Algorithm 1 solves a minimum-cost flow on a directed network: two supply nodes (vulnerable and other), one node per origin and class, one node per slot, and a sink. Every variable is the flow on one arc, and every constraint is either the conservation of flow at a node or the capacity of an arc. Incidence matrices of directed graphs, with nodes as rows and arcs as columns, are totally unimodular; a linear program built on one, with whole-number supplies and capacities, therefore has an optimal vertex in whole numbers, and the network simplex method moves only between such vertices (Ahuja et al., 1993; Schrijver, 2003). □

**Proposition 2 (Placing the vulnerable first costs no one a place).** Let $F^*$ be the largest number of persons that any plan can place, ignoring the vulnerable class. Some plan places both $F_V^*$ vulnerable persons and $F^*$ persons in all.

*Proof.* Start from a flow that places $F_V^*$ vulnerable persons and nobody else; it is feasible in the network that holds both classes. The augmenting-path method raises any feasible flow to a maximum flow (Ford & Fulkerson, 1962). An augmenting path starts at the source and never returns to it, so it never lowers the flow on an arc leaving the source; in particular, it never lowers the number of vulnerable persons placed. When no augmenting path remains, the flow is maximum, so it places $F^*$ persons, still including $F_V^*$ vulnerable ones. □

**Proposition 3 (The penalties give the order of the law exactly).** Every minimum-cost flow of Algorithm 1, with the penalties of Equation (8), is lexicographically optimal in the sense of Definition 8.

*Proof.* A plan $x$ is a feasible flow of the network exactly when $F_V(x) = F_V^*$ and $F(x) = F^*$; by Proposition 2 such plans exist, so they are the plans that are optimal at the first two levels. For them the cost is $M_Y Y(x) + M_O O(x) + \Theta(x)$. Since $0 \le \Theta(x) \le D\, T_{\max} < M_O$ and $0 \le M_O O(x) + \Theta(x) \le D (M_O + T_{\max}) < M_Y$, a plan with fewer persons in classrooms always costs less: if $Y(x) < Y(x')$ then the cost of $x$ is below $M_Y\,(Y(x) + 1) \le M_Y\, Y(x')$, which is at most the cost of $x'$. With $Y$ equal, the same argument applies to $O$ with $M_O$, and with both equal the cost is $\Theta$. A minimum-cost flow is therefore best at every level in turn. □

**Remark 1 (What the penalties mean).** The penalties are a device, not a price. The plan never trades a single classroom for any amount of travel, but it also never sends anyone farther than $\theta_{\max}$, because a pair beyond that limit is not suitable in the first place. The limit, not the penalty, is where safety and schooling are balanced.

**Proposition 4 (Packing closes at most one extra classroom per school in use).** Let $x$ be the plan of Algorithm 1, $m$ the number of schools in whose classrooms it places anyone, and $K^*$ the fewest classrooms closed by any plan that places $F_V^*$ vulnerable persons and $F^*$ persons in all. Then

$$K^* \le K(x) \le K^* + m - 1 \quad (m \ge 1), \qquad K(x) = K^* \ \text{when}\ m \le 1$$

EQNUM:(13)

::: {custom-style="Source Line"}
Source: derived here (Proposition 4)
:::

*Proof.* The lower inequality holds because $x$ is one of the plans over which $K^*$ is the minimum. For the upper one, let $Y^* = Y(x) = \sum_s y_s$, the fewest persons that any such plan places in classrooms (Proposition 3). A classroom holds at most $q$ persons, so every such plan closes at least $\lceil Y^*/q \rceil$ classrooms, and $K^* \ge Y^*/q$. Packing gives $K_s = \lceil y_s/q \rceil \le y_s/q + (q-1)/q$ for each of the $m$ schools, so

$$K(x) - K^* \le \frac{Y^*}{q} + m\,\frac{q-1}{q} - \frac{Y^*}{q} = m\,\frac{q-1}{q} < m$$

EQNUM:(14)

::: {custom-style="Source Line"}
Source: derived here (proof of Proposition 4)
:::

and since both sides are whole numbers, $K(x) - K^* \le m - 1$. When $m = 1$, $K(x) = \lceil Y^*/q \rceil \le K^*$. □

**Remark 2 (Why not minimize classrooms exactly).** The exact minimum of $K$ is an integer program, because a classroom counts as closed as soon as one person enters it. Proposition 4 shows that the simple rule of filling one room before opening the next costs at most one room per school in use, and the tests of Section 3.3 found no extra room at all in 144 of 150 instances.

**Proposition 5 (A higher alert level never frees classrooms).** Let $\sigma \preceq \sigma'$, and suppose a plan for $\sigma'$ places every evacuee. Then a plan for $\sigma$ places every evacuee too, and the fewest persons in classrooms satisfy $Y^*(\sigma) \le Y^*(\sigma')$.

*Proof.* Take a lexicographically optimal plan $x'$ for $\sigma'$; it places all $D(\sigma')$ persons, so it places every vulnerable person as well. Every origin active in $\sigma$ is active in $\sigma'$ with the same population, because $Z_\sigma \subseteq Z_{\sigma'}$. Every road open in $\sigma'$ is open in $\sigma$, because $X_\sigma \subseteq X_{\sigma'}$, so $T_\sigma(a,s) \le T_{\sigma'}(a,s)$; and every shelter outside the zones of $\sigma'$ is outside the zones of $\sigma$. Every pair suitable in $\sigma'$ is therefore suitable in $\sigma$. Deleting from $x'$ the flows of origins that are not active in $\sigma$ leaves a plan for $\sigma$ that places everyone, all vulnerable persons included, with at most $Y(x') = Y^*(\sigma')$ persons in classrooms. The minimum for $\sigma$ can only be smaller. □

**Remark 3 (Plan for the highest alert first).** Proposition 5 lets a local government sign agreements with schools once, for the highest alert level it plans for: the classrooms needed at a lower level never exceed that number, provided the higher plan shelters everyone.

**Proposition 6 (The time-expanded network is exact; Ford & Fulkerson, 1958, 1962).** (i) Under Assumptions 1 to 3, $F_\sigma(T)$ equals the largest number of evacuees who can be inside their shelters by minute $T$ without any road carrying more than its capacity in any minute and without any shelter receiving more than its assigned number. (ii) For one origin and one shelter with no limit on supply or room,

$$F(T) = \max_{f}\; \Big[ (T+1)\,|f| - \sum_{e} \tau_e\, f_e \Big]$$

EQNUM:(15)

::: {custom-style="Source Line"}
Source: Ford and Fulkerson (1958), written for departures at minutes 0 to T
:::

where the maximum runs over static flows $f$ respecting the capacities $u_e$ and $|f|$ is the value of $f$.

*Proof.* (i) A movement in time is the same object as a flow in $G^T_\sigma$: a person who leaves $v$ at minute $t$ along $e$ uses the arc from $(v,t)$ to $(w, t+\tau_e)$, a person who waits uses a waiting arc, the capacity of each movement arc is the capacity of the road in that minute, and the shelter vertex collects arrivals at any minute up to $T$ and lets through only the assigned number. By the argument of Proposition 1 a maximum flow can be taken in whole persons. (ii) A static flow split into paths $P$ carrying $f_P$ can be repeated every minute from $0$ to $T - \tau(P)$, which delivers $\sum_P f_P\,(T - \tau(P) + 1) = (T+1)|f| - \sum_e \tau_e f_e$ by minute $T$. Ford and Fulkerson (1958) proved that the best such repeated flow is a maximum flow over time. □

**Proposition 7 (Bisection finds the clearance time exactly).** $F_\sigma(T)$ never decreases as $T$ grows, and Algorithm 2 returns $T^*_\sigma$ exactly. It needs about $2\log_2 T^*_\sigma$ maximum-flow computations, each on a network with $|N|(T+1)$ road vertices and at most $|N|\,T + |E|\,(T+1)$ road arcs.

*Proof.* Every vertex and arc of $G^T_\sigma$ exists in $G^{T+1}_\sigma$ with the same capacity, and an arrival by minute $T$ is an arrival by minute $T+1$, so a flow for $T$ is a flow for $T+1$ of the same value and $F(T) \le F(T+1)$. If step 1 passes, everyone can reach a shelter with no time limit, and sending one person per minute along such paths moves everyone in finite time, so the doubling of step 2 stops. Steps 3 to 6 keep $F(\text{lo}) < D' \le F(\text{hi})$ and halve the gap each round; when the gap is one minute, hi is the least $T$ with $F(T) \ge D'$, which by monotonicity is $T^*$. Doubling and bisection each take about $\log_2 T^*$ rounds. The counts of vertices and arcs follow from Definition 10. □

**Proposition 8 (A lower bound from one static flow).** Let $c$ be the value of a maximum static flow from the origins that send evacuees to the shelters that receive them, with arc capacities $u_e$ and no other limit, and let $\tau_{\min}$ be the shortest travel time from such an origin to such a shelter. Then

$$T^{*}_\sigma \;\ge\; \max\Big\{\, \tau_{\min} - 1 + \Big\lceil \frac{D'}{c} \Big\rceil,\;\; \max_{a} \min_{s} T_\sigma(a, s) \,\Big\}$$

EQNUM:(16)

::: {custom-style="Source Line"}
Source: derived here (Proposition 8)
:::

*Proof.* By the max-flow min-cut theorem, $c$ is the capacity of a set of arcs that every path from an origin to a shelter must cross. Count each evacuee at the first minute $t$ at which he or she enters such an arc $e = (v,w)$. Reaching $v$ takes at least the distance $d(O, v)$ from the nearest origin, and after the arc at least $\tau_e + d(w, S)$ more minutes remain, so $d(O,v) \le t \le T - \tau_e - d(w,S)$. Since $d(O,v) + \tau_e + d(w,S)$ is the length of some path from an origin to a shelter, it is at least $\tau_{\min}$, and there are at most $T - \tau_{\min} + 1$ usable minutes, each carrying at most $u_e$ persons. Summing over the cut gives $F(T) \le c\,(T - \tau_{\min} + 1)$, and $F(T^*) = D'$ gives the first term. The second holds because the last evacuee of an origin cannot arrive before the travel time to the nearest shelter. □

**Proposition 9 (Closures and new shelters move the plan in one direction).** Fix a scenario $\sigma$.

(i) Closing a set $B$ of roads never shortens a travel time, never raises $F_V^*$ or $F^*$, and, with the plan held fixed, never shortens the clearance time: $T^*_{\sigma+B} \ge T^*_\sigma$. If the closure leaves $F_V^*$ and $F^*$ unchanged, it never lowers $Y^*$.

(ii) Adding a shelter, or room to one, never lowers $F_V^*$ or $F^*$; if both stay the same, it never raises $Y^*$; and with the same persons per origin and shelter limits at least as large, it never lengthens the clearance time.

*Proof.* (i) Removing arcs cannot shorten a shortest path, so the set of suitable pairs can only shrink, and maximum flows over fewer arcs cannot grow. $G^T_{\sigma+B}$ is a subgraph of $G^T_\sigma$, so $F$ can only fall for every $T$, and the first minute at which it reaches $D'$ can only come later. If $F_V^*$ and $F^*$ are unchanged, every plan that is optimal at the first two levels after the closure is also such a plan before it, so the least $Y$ after the closure is at least the least $Y$ before. (ii) The same arguments with the inclusions reversed: new slots and new pairs can only enlarge the feasible plans, and larger arc capacities to the super-sink can only raise $F$. □

**Remark 4 (One bridge or a whole channel).** A road network with alternatives absorbs the loss of a single bridge, so the closure effect of one segment is often zero. A lahar, however, closes every bridge over its channel at once. Proposition 9 holds for any set $B$, so the model tests whole channels as well as single bridges (Section 3.5.3).

**Proposition 10 (Greedy siting is near-optimal; Gale, 1957; Edmonds, 1970; Nemhauser et al., 1978).** The coverage $\Phi_\theta$ is nondecreasing and submodular. Hence the siting gain $f$ of Equation (12) is nondecreasing and submodular with $f(\varnothing) = 0$, and the sites $S_g$ chosen by Algorithm 3 satisfy

$$f(S_g) \;\ge\; \Big[1 - \Big(1 - \frac{1}{k}\Big)^{k}\Big] f(S^{opt}) \;\ge\; \Big(1 - \frac{1}{e}\Big) f(S^{opt}) \approx 0.632\, f(S^{opt})$$

EQNUM:(17)

::: {custom-style="Source Line"}
Source: Nemhauser et al. (1978), applied here to the coverage of Definition 13
:::

where $S^{opt}$ is the best set of $k$ sites.

*Proof.* By the max-flow min-cut theorem on the network of Definition 13, a cut either removes the source arc of an origin or the sink arc of every shelter that origin reaches within $\theta$. Writing $c(X) = \sum_{s \in X} (c^0_s + c^1_s)$ and $N_\theta(B')$ for the evacuees of the origins within $\theta$ of some shelter in $B'$, this gives Gale's (1957) formula

$$\Phi_\theta(B) = \min_{B' \subseteq B}\; \Big[\, c(B \setminus B') + D\big(N_\theta(B')\big) \Big]$$

EQNUM:(18)

::: {custom-style="Source Line"}
Source: Gale (1957), written for the coverage of Definition 13
:::

The function $B' \mapsto D(N_\theta(B'))$ counts weighted coverage: it never decreases, it is submodular, and it vanishes on the empty set, which makes it the rank function of a polymatroid. Equation (18) gives the rank function of that polymatroid restricted to the box $\{z : z_s \le c^0_s + c^1_s\}$; the restriction is a polymatroid as well (Edmonds, 1970; Fujishige, 2005), and every polymatroid rank function is nondecreasing and submodular. Holding the existing shelters $E$ fixed preserves both properties, and $f(\varnothing) = 0$. The approximation bound then follows from the result of Nemhauser et al. (1978) on maximizing such functions when only a fixed number of elements may be picked. □

**Remark 5 (What the planning results buy).** By Proposition 10, a provincial planner may pick Ligtas Pinoy Center sites by a rule that fits in a spreadsheet, and the coverage obtained is guaranteed to reach 63.2 percent or more of the optimum. In practice the greedy rule beat this guarantee by a wide margin in the tests of Section 3.3.

## 3.3 Software Verification

Each proven property was then tested numerically against reference code written separately, so that a coding mistake could not pass unnoticed into the results (Table 7). Random instances were geometric road graphs on a 10-by-10-kilometer square with transit times at 24 kilometers per hour, capacities of 5 to 30 persons per minute, origins of 40 to 400 persons with 10 to 35 percent vulnerable, and shelters of both kinds, 15 percent of them inside the second hazard zone.

::: {custom-style="Paper Caption"}
**Table 7.** Checks on the model, all run by `verify_evacuation.py` on random synthetic instances with independently computed correct answers.
:::

| Property verified | Method of check | Result |
|:----------------|:------------------------------|:-------------------------|
| Integral, lexicographically optimal plan (Props. 1 to 3) | 300 instances (14 to 26 road nodes, 3 to 7 origins, 3 to 8 shelters, two hazard zones); Algorithm 1 against five sequential linear programs solved with HiGHS | All five levels equal in all 300 instances (1,500 values); no fractional flow |
| Classroom packing bound (Prop. 4) | 150 instances that use classrooms; exact minimum from a mixed-integer program (HiGHS) | Bound held in all 150; packing exact in 144; one extra classroom in 5 and two in 1 (up to 6 schools in use) |
| Time-expanded network (Prop. 6) | 60 random graphs with one origin and one shelter, horizons 0 to 60 minutes; maximum flow on $G^T$ against the linear program of Equation (15) | Agreement in all 660 pairs (480 with positive flow) |
| Clearance time and its bound (Props. 7, 8) | 79 instances; Algorithm 2 against a minute-by-minute scan | Same $T^*$ in all 79; bound never violated; bound over $T^*$ averaged 0.585 (lowest 0.125); 5.2 maximum flows per bisection against 26.9 per scan |
| Monotonicity (Props. 5, 9) | 120 instances: a random road closed, a shelter added, nested alert scenarios | No violation in 119 clearance checks after a closure, 120 classroom checks after a closure, 53 after an added shelter, 119 clearance checks after an added shelter, or 52 alert-level checks |
| Submodularity of coverage (Prop. 10) | 80 instances (40 road networks, 40 built with overlapping coverage), 60 random triples each | No violation in 4,796 checks of diminishing returns |
| Greedy siting (Prop. 10) | The same 80 instances, $k = 1$ to 4, against exhaustive search over all sets | Worst ratio 0.890, mean 0.997, optimal in 303 of 320 cases; guaranteed 0.632 |

Two rows deserve comment. The packing row shows that the bound of Proposition 4 is not merely safe but nearly tight in practice: in the 6 instances where packing missed the exact minimum, the exact program regrouped evacuees between schools so that each school filled whole rooms. The clearance row shows the value of bisection: on the same instances, a minute-by-minute scan needed about five times as many maximum-flow computations.

## 3.4 Computational Cost

::: {custom-style="Paper Caption"}
**Table 8.** Time to compute the school-preserving plan (Algorithm 1, plain Python, network simplex, fastest of five runs).
:::

| Road nodes | Origins | Shelters | Road arcs | Evacuees | Time (s) |
|---------:|--------:|--------:|---------:|---------:|--------:|
| 100 | 20 | 15 | 382 | 5,022 | 0.016 |
| 200 | 40 | 30 | 774 | 8,293 | 0.074 |
| 400 | 80 | 60 | 1,550 | 18,237 | 0.465 |
| 800 | 160 | 120 | 3,032 | 36,654 | 2.917 |

::: {custom-style="Paper Caption"}
**Table 9.** Size of the time-expanded network and time for one maximum flow (40 road nodes, 6 origins, 6 shelters, fastest of five runs).
:::

| Horizon (min) | Vertices | Arcs | Time per maximum flow (s) |
|---------:|---------:|---------:|---------:|
| 30 | 1,245 | 5,416 | 0.044 |
| 60 | 2,445 | 11,266 | 0.120 |
| 120 | 4,845 | 22,966 | 0.208 |
| 240 | 9,645 | 46,366 | 0.560 |

Albay has 720 barangays, and the largest row of Table 8, with 160 origin clusters and 120 shelters, already exceeds the evacuation of the whole Permanent and Extended Danger Zones of Mayon. The time-expanded network grows linearly with the horizon, as Proposition 7 predicts, and a clearance time of four hours costs about half a second per maximum flow, or a few seconds for the whole bisection.

## 3.5 Worked Instance E1

Instance E1 is a compact synthetic volcano on which a reader can follow each stage of the pipeline by hand (Figure 2). A ring road runs eight kilometers from the summit; five towns lie outside it, joined to the ring and to each other by highways; six barangay clusters lie inside or near the danger zones; and two lahar channels run down the southern flank, crossing seven road segments, each crossing a bridge. One minute is one time step; barangay roads carry 20 persons per minute at 15 kilometers per hour, the ring 30 persons per minute at 30 kilometers per hour, and highways 40. All figures are invented for the test; the names of the towns are only positions on the compass.

::: {custom-style="Figure Para"}
![](/home/user/MAP---A/research/safe-shelter-open-schools/paper/../code/figures/fig_e1_map.png){width=5.2in}
:::

::: {custom-style="Figure Caption"}
**Figure 2.** Instance E1: a synthetic volcano with six barangay clusters (red), six shelters in five towns (blue), the six-kilometer Permanent Danger Zone, the seven-kilometer Extended Danger Zone on the southern flank, and two lahar channels (brown lines) whose bridges are marked A1 to A4 and B1 to B3.
:::

::: {custom-style="Paper Caption"}
**Table 10.** Origins of E1 (synthetic).
:::

| Origin | Zone | Distance from summit (km) | Population | Vulnerable | Nearest shelter, minutes |
|:---|:---|---:|---:|---:|:-------|
| O1 | Permanent Danger Zone | 4.6 | 520 | 114 | SCH3, 28 |
| O2 | Permanent Danger Zone | 5.4 | 430 | 82 | EC1, 22 |
| O3 | Permanent Danger Zone | 5.6 | 610 | 146 | EC2, 24 |
| O4 | Extended Danger Zone | 6.6 | 380 | 80 | SCH1, 14 |
| O5 | Extended Danger Zone | 6.8 | 450 | 90 | EC3, 19 |
| O6 | Lahar area | 9.4 | 300 | 75 | EC2, 16 |

::: {custom-style="Paper Caption"}
**Table 11.** Shelters of E1 with capacities from Equation (3) (synthetic).
:::

| Shelter | Kind | Floor area for tiers 0 or 1 (m²) | Tier 0 | Tier 1 | Classrooms | Tier 2 | Accessible | Learners per room |
|:------------|:-------|--------:|-----:|-----:|----------:|-----:|:----------|--------:|
| EC1 (municipal evacuation center) | Non-school | 1,400 | 400 | – | – | – | yes | – |
| EC2 (parish hall) | Non-school | 700 | 200 | – | – | – | yes | – |
| EC3 (barangay covered court) | Non-school | 1,050 | 300 | – | – | – | yes | – |
| SCH1 (central elementary school) | School | 630 | – | 180 | 20 | 360 | yes | 40 |
| SCH2 (national high school) | School | 840 | – | 240 | 30 | 540 | yes | 45 |
| SCH3 (two-storey elementary school) | School | – | – | – | 14 | 252 | no | 38 |

The non-school shelters hold 900 persons, the school open spaces 420, and the 64 classrooms 1,152, for 2,472 in all. SCH3 is a two-storey school without a ramp, so vulnerable evacuees may not be placed there.

### 3.5.1 Shelter Plans on E1

Table 12 compares the three plans of Section 2.11 in the three scenarios of Table 4.

::: {custom-style="Paper Caption"}
**Table 12.** Shelter plans on E1 by scenario. "Time-only" minimizes travel after placing everyone; "school-preserving" is Algorithm 1 (synthetic instance).
:::

| Scenario and plan | Evacuees | Placed | In non-school space | In school open space | In classrooms | Classrooms closed | Learners displaced | Mean trip (min) |
|:------------|--------:|-------:|-------:|-------:|----------:|----------:|---------:|------:|
| Alert Level 3, time-only | 1,560 | 1,560 | 600 | 240 | 720 | 40 | 1,702 | 29.48 |
| Alert Level 3, school-preserving | 1,560 | 1,560 | 900 | 420 | 240 | 14 | 532 | 31.18 |
| Alert Level 4, time-only | 2,390 | 2,390 | 900 | 410 | 1,080 | 60 | 2,502 | 25.36 |
| Alert Level 4, school-preserving | 2,390 | 2,390 | 900 | 420 | 1,070 | 60 | 2,502 | 25.36 |
| Compound (AL4 + lahar), time-only | 2,690 | 2,240 | 900 | 420 | 920 | 52 | 2,142 | 29.21 |
| Compound (AL4 + lahar), school-preserving | 2,690 | 2,240 | 900 | 420 | 920 | 52 | 2,142 | 29.21 |

Three effects stand out. The first is capacity: if every barangay simply went to its nearest shelter site, 298 evacuees would arrive at full sites at Alert Level 3, 448 at Alert Level 4, and 898 in the compound scenario. The second is the classroom saving at Alert Level 3: both optimal plans shelter all 1,560 evacuees and all 342 vulnerable residents, but the time-only plan fills the nearby classrooms of SCH2 and SCH3 while the gymnasiums and halls farther away stay part-empty. The school-preserving plan fills every non-school space and school open space first and closes 14 classrooms instead of 40, sparing 1,170 learners, at a cost of 1.70 minutes of average travel. The third is saturation: at Alert Level 4 the shelters are 97 percent full, and the two plans almost coincide, because nearly every classroom is needed whatever the plan. When the shelter network itself is too small, only new shelters help (Section 3.5.4).

::: {custom-style="Paper Caption"}
**Table 13.** Who goes where under the school-preserving plan at Alert Level 3 (synthetic instance).
:::

| Origin | Shelter | Space | Persons |
|:---|:---|:----------|---:|
| O1 | EC3 | non-school | 280 |
| O1 | SCH3 | classroom | 240 |
| O2 | EC1 | non-school | 400 |
| O2 | EC2 | non-school | 30 |
| O3 | EC2 | non-school | 170 |
| O3 | EC3 | non-school | 20 |
| O3 | SCH1 | school open space | 180 |
| O3 | SCH2 | school open space | 240 |

The plan sends part of O1 past the nearby two-storey school to the covered court of EC3 and fills the school open spaces of SCH1 and SCH2 from O3. Only the 240 persons who cannot fit anywhere else go to classrooms, all in SCH3 and packed into 14 rooms. By Proposition 4 with $m = 1$, no plan that shelters everyone could close fewer.

### 3.5.2 Classrooms and Learners

The classroom count turns into lost schooling. With the average class sizes of Table 11, the time-only plan at Alert Level 3 displaces 1,702 learners and the school-preserving plan 532. If the stay lasts the fifteen days that DepEd guidance allows for medium- and long-term displacement, the difference is 17,550 learner-days of face-to-face classes kept, or 390 classroom-days.

### 3.5.3 Evacuation over Time and the Lahar Bridges

::: {custom-style="Paper Caption"}
**Table 14.** Clearance time of the school-preserving plan and the lower bound of Proposition 8 (synthetic instance).
:::

| Scenario | Persons moved | Clearance time $T^*$ (min) | Lower bound (min) | Bound over $T^*$ |
|:----|---:|---:|---:|---:|
| Alert Level 3 | 1,560 | 53 | 34 | 0.64 |
| Alert Level 4 | 2,390 | 53 | 28 | 0.53 |
| Compound (AL4 + lahar) | 2,240 | 74 | 28 | 0.38 |

::: {custom-style="Figure Para"}
![](/home/user/MAP---A/research/safe-shelter-open-schools/paper/../code/figures/fig_e1_arrivals.png){width=5.6in}
:::

::: {custom-style="Figure Caption"}
**Figure 3.** Evacuees inside shelters, $F(T)$, against minutes after the order to evacuate, for the three scenarios of E1 (synthetic instance).
:::

At Alert Level 3 the last evacuee is sheltered after 53 minutes. Adding the Extended Danger Zone does not lengthen the evacuation in E1: under the Alert Level 4 plan the residents of the Permanent Danger Zone alone need 53 minutes and those of the Extended Danger Zone alone 32 minutes, and moving both groups together still takes 53. Figure 3 shows the shape behind these numbers: nobody arrives until the shortest trips end, then the curve climbs at the rate the busiest roads allow and flattens as the last, longest trips finish.

::: {custom-style="Paper Caption"}
**Table 15.** Closure of lahar bridges at Alert Level 4: with the plan held fixed (Definition 12) and with a new plan for the damaged network (synthetic instance).
:::

| Bridges closed | Clearance, plan held fixed (min) | Evacuees who cannot be sheltered | Classrooms closed | Clearance, new plan (min) | Mean trip, new plan (min) |
|:---------|---:|---:|---:|---:|---:|
| None | 53 | 0 | 60 | 53 | 25.36 |
| Channel A (A1 to A4) | 95 | 0 | 60 | 95 | 46.73 |
| Channel B (B1 to B3) | 74 | 0 | 60 | 74 | 29.82 |
| Both channels (all seven) | never finishes | 450 | 35 | 74 | 31.25 |

Closed one at a time, the seven bridges barely matter: six leave the clearance time at 53 minutes and the seventh, A4, adds one minute. The network has alternatives for every single crossing. A lahar, however, closes all the bridges over its channel at once. Losing channel A adds 42 minutes, and losing channel B adds 21. Losing both cuts the southern pocket, the ring between the two channels with O3, O4, and the central school SCH1, from every other shelter: 450 residents can no longer be sheltered at all, and the plan held fixed can never finish. The model therefore gives a concrete warning that no single-bridge analysis would give: O3 and O4 must be evacuated before lahar-producing rain, or the pocket needs a shelter of its own.

### 3.5.4 Where to Build Ligtas Pinoy Centers on E1

The compound scenario is the hardest test for the shelter network: 2,690 evacuees, 450 of them unplaceable. Five candidate sites, one in each town, were offered with planned capacities from floor plans of 875 to 1,400 square meters, and coverage was measured with a 30-minute standard. Without new centers, 1,180 evacuees can be sheltered outside classrooms within that standard. Single sites would add 400 (south town), 350 (northeast town), 150 (southwest town), 30 (east town), 0 (southeast city) evacuees.

::: {custom-style="Paper Caption"}
**Table 16.** Greedy choice of Ligtas Pinoy Center sites in the compound scenario, against exhaustive search, and the plan recomputed with the chosen centers (synthetic instance). $k$ is the number of sites built, rooms are classrooms; towns: TS south, TNE northeast, TSW southwest.
:::

| $k$ | Greedy choice | Gain $f(S_g)$ | Best choice | Best gain | Not sheltered | Persons in rooms | Rooms closed | Learners displaced | Clearance (min) |
|:----|:--------|-----:|:--------|-----:|---------:|----------:|-----------:|----------:|-----------:|
| 0 | – | 0 | – | 0 | 450 | 920 | 52 | 2,142 | 74 |
| 1 | TS | 400 | TS | 400 | 50 | 920 | 52 | 2,142 | 74 |
| 2 | TS, TNE | 750 | TS, TNE | 750 | 50 | 570 | 32 | 1,256 | 74 |
| 3 | TS, TNE, TSW | 900 | TS, TSW, TNE | 900 | 50 | 360 | 20 | 800 | 67 |

The greedy rule found the best set for every $k$. Its first choice, the south town, is inside the cut-off pocket, and it shelters 400 of the 450 residents who had nowhere to go. The second and third choices cut the persons in classrooms from 920 to 570 and then 360, closing 32 and then 20 classrooms instead of 52. The southeast city gains nothing: its existing shelters already cover everyone who can reach it within half an hour.

## 3.6 Planned Experiments on the Albay Open-Data Set

The experiments below use the Albay data set assembled in Stages 1 to 4 from the registers of Appendix A, along with randomized versions of that data set. Their results will appear in a separate report; every test and decision rule that follows was settled before the instance was run.

### 3.6.1 Sensitivity Analysis

Six inputs are varied in the sensitivity tests: the space standard (3.5 and 4.5 square meters per person), the persons per classroom (18 and 14), the longest acceptable trip $\theta_{\max}$ (60, 90, and 120 minutes), road capacities ($\pm 25$ and $\pm 50$ percent), travel speeds ($\pm 20$ percent), and the share of vulnerable residents ($\pm 5$ percentage points). Every scenario of Table 4 is rerun under each setting.

### 3.6.2 Statistical Treatment

Eight questions are tested formally (Table 17).

::: {custom-style="Paper Caption"}
**Table 17.** How each question is tested.
:::

| Question | Test or estimator | Why it was chosen |
|:-------------------|:--------------------|:--------------------|
| (S1) How many classrooms does the school-preserving plan save over the time-only plan? | Ratio of classrooms closed, with a 95% percentile bootstrap interval from 2,000 resamples of origins (Efron & Tibshirani, 1993) | Assumes no distribution; reflects the uncertainty from the set of origins |
| (S2) What extra travel does keeping schools open cost each evacuee? | Paired difference in travel time per evacuee, Wilcoxon signed-rank test (Wilcoxon, 1945) with a bootstrap interval for the mean | Paired, skewed, and bounded below by zero |
| (S3) How often does the nearest-site rule overfill a shelter? | Weighted share of evacuees arriving at a full site, with a bootstrap interval | For a proportion, an interval says more than a test |
| (S4) Are rural origins farther from their assigned shelter than urban ones? | Mann-Whitney U (Mann & Whitney, 1947) with the rank-biserial effect size (Kerby, 2014) | Travel times are skewed and floored at zero |
| (S5) Can every vulnerable resident be placed in an accessible shelter? | Deficit $V(\sigma) - F_V^*$ by municipality, exact | A deficit is a count, not an estimate |
| (S6) Which closures matter? | Clearance effect of each lahar channel (Definition 12), exact | Proposition 9 makes every effect nonnegative |
| (S7) How much do new centers help? | Classrooms closed after $k = 1$ to 3 greedy sites, with the guarantee of Proposition 10 | The guarantee bounds what exhaustive search could add |
| (S8) How sensitive are the results to the space standard? | Spearman rank correlation (Spearman, 1904) of municipal classroom counts at 3.5 and 4.5 m² | Asks whether the ranking of municipalities survives |

### 3.6.3 Model Hypotheses Fixed in Advance

Each hypothesis below, with its rule for deciding support, was stated before any computation on the study-area instance.

* **M1.** At Alert Level 3, the school-preserving plan closes fewer than half the classrooms of the time-only plan. Supported if the bootstrap interval of the ratio lies wholly below 0.5.
* **M2.** The extra mean travel time of the school-preserving plan is below ten minutes per evacuee. Supported if the whole bootstrap interval falls under 10.
* **M3.** The nearest-site rule overfills at least one shelter in every scenario. Supported if the overflow is positive in all scenarios of Table 4.
* **M4.** Larger alert levels never free classrooms and closures never shorten the evacuation. Propositions 5 and 9 guarantee this exactly; any violation would therefore signal a data error, and the record would go back for checking.
* **M5.** In the compound scenario, at least one barangay cluster is cut off from every shelter outside its pocket. Supported if the list of trapped origins is not empty; the list is then reported to the PDRRMO.
* **M6.** Two Ligtas Pinoy Centers placed by Algorithm 3 cut the persons housed in classrooms at Alert Level 4 by at least 30 percent.
* **M7.** Every vulnerable resident can be placed in an accessible shelter at Alert Level 3. Supported if $F_V^* = V(\sigma)$; otherwise the deficit is reported by municipality.
* **M8.** The ranking of municipalities by classrooms closed is stable under the space standard: Spearman's $\rho$ above 0.8.

Within the model, M1, M2, and M6 measure the trade-offs relevant to targets 4.a and 11.5.

### 3.6.4 Sensitivity Sweeps

Across seven sweeps, the main results are recomputed over a range of one parameter at a time: the space standard, the classroom capacity, $\theta_{\max}$, road capacities, travel speeds, the vulnerable share, and the travel-time standard $\theta$ of the siting problem (15, 30, and 45 minutes).


# 4. CONCLUSIONS

## 4.1 Evaluation of the Findings

This study set out to answer one main question. How can each evacuee from an Albay hazard zone receive a shelter so that vulnerable residents come first, everyone has a place, and the fewest classrooms close? The question also covered how much time such an evacuation would need. The findings show that such a plan can be stated precisely and solved exactly within seconds on a laptop. Separately written code confirms it, and it can be analyzed before any field survey.

**Objective 1: hazards, origins, roads, and shelters.** Scenarios, origins, the road network, and shelter capacities were defined from public registers and published standards (Definitions 1 to 6). A standard classroom holds 18 evacuees at the Sphere indicator, which turns the abstract rule "classrooms last" into a count that can be minimized.

**Objective 2: the lexicographic shelter plan.** The legal order of priorities became one minimum-cost flow. Plans are always in whole persons (Proposition 1), placing vulnerable residents first never costs anyone a place (Proposition 2), and the penalties reproduce the order exactly (Proposition 3). The plan matched five sequential linear programs at every level in all 300 test instances.

**Objective 3: classrooms and alert levels.** Packing evacuees into full classrooms closes at most one more classroom per school in use than the true minimum (Proposition 4); in 144 of 150 exact comparisons it closed none more. A higher alert level never frees classrooms (Proposition 5), which lets local governments plan once for the highest level.

**Objective 4: clearance time.** The time-expanded network gives the exact clearance time (Propositions 6 and 7) and agreed with the Ford-Fulkerson formula in all 660 tests; bisection found it with about five maximum-flow computations instead of about 27. The lower bound of Proposition 8 was never violated.

**Objective 5: closures and new shelters.** Closures never shorten an evacuation and new shelters never add classroom use when everyone is already sheltered (Proposition 9); no violation appeared in 463 checks. On E1, single bridges did not matter, but losing both lahar channels trapped 450 residents in a pocket served by one school.

**Objective 6: Ligtas Pinoy Center siting.** Because the extra coverage from new centers is submodular, greedy siting always attains no less than 63.2 percent of the optimum (Proposition 10). Across the test instances, greedy siting never dropped below 89.0 percent of the optimum and matched it exactly in 94.7 percent of them.

**Objective 7: verification.** Every proven property was checked against independently written code, and none failed (Table 7). Computing a plan for 160 origin clusters and 120 shelters took under three seconds in plain Python.

**Objective 8: worked instance and hypotheses.** The synthetic volcano makes the stakes concrete. At Alert Level 3 the school-preserving plan closed 14 classrooms instead of 40 and displaced 532 learners instead of 1,702, at a cost of 1.70 minutes of average travel; the nearest-site rule would have sent 298 people to full shelters. Eight hypotheses for the open-data instance were fixed in advance (Section 3.6.3).

## 4.2 Limitations

* **(L1) Synthetic worked instance.** Tables 10 to 16 demonstrate only that the pipeline obeys its own rules; they carry no empirical information about Albay. The classroom counts of E1 must not be read as estimates for any real school.
* **(L2) Capacities on roads are declared.** Road capacities stand in for both the road and the trucks assigned to it. Real evacuations depend on how many vehicles the local government has and where they start, which the model does not schedule.
* **(L3) Everyone leaves at once.** Assumption 3 puts every evacuee on the road at minute zero. Real evacuations come in waves and people hesitate; the clearance time is therefore a best case for a given road network.
* **(L4) Families may be split.** Assumption 5 allows the persons of one origin to go to different shelters. Keeping families together is a further constraint that would make the problem harder; the plan should be adjusted by the officer in charge.
* **(L5) Floor areas are not yet surveyed.** No register lists the usable floor area of every gymnasium, hall, and classroom, so capacities in the open-data instance will rest on building plans and the DepEd standard. A field inventory would replace them without changing the mathematics.
* **(L6) Accessibility is a single flag.** Real accessibility has degrees: a ramp, an accessible toilet, a ground-floor room. The model asks only whether a shelter is accessible.
* **(L7) The space standard is one number.** The Sphere indicator of 3.5 square meters is a minimum for covered living space. Cooking, sanitation, and privacy need more, and the sweeps at 4.5 square meters bound the effect.
* **(L8) Safety of shelters.** Assumption 7 treats a shelter outside the danger zones as safe. Ashfall reached up to 132 schools in Albay in May 2026 (Philippine Star, 2026), and a shelter under heavy ash may need to close.
* **(L9) Stays, not only trips.** The model plans the trip and the first placement. It does not model the length of stay, the return home, or the rotation of classrooms during a long evacuation.
* **(L10) Coverage-based siting.** Definition 14 counts evacuees who could be sheltered outside classrooms. It ignores the cost of land and construction and the use of a center between disasters.
* **(L11) Provincial border.** Shelters in Camarines Sur or Sorsogon are not considered, which may understate the options for border municipalities.

## 4.3 Recommendations and Challenges in Extending the Results

**Shelter inventory.** The first step is an inventory of every designated evacuation center and every school in the danger-zone municipalities, with floor areas of gymnasiums, halls, and classrooms, accessibility, and contact persons, following the schema of Appendix C. DepEd Albay and the municipal disaster offices already hold most of this information.

**Field validation.** Evacuation drills give the data needed to calibrate road capacities: the number of trucks, their loads, and the time between trips. Records of the January and May 2026 evacuations from the reports of the DSWD would allow a direct test: given the evacuees and centers actually used, how many classrooms would the plan have kept open?

**Use by the Provincial Government.** Moving the model into operation needs the consent and oversight of the Provincial Disaster Risk Reduction and Management Office (PDRRMO), the Albay Public Safety and Emergency Management Office (APSEMO), and the Schools Division Offices. The plan should be offered as advice to the officer who signs the evacuation order, never as an automatic order.

**Ligtas Pinoy Centers.** Local governments preparing proposals under Republic Act No. 12076 can use Algorithm 3 to rank candidate lots by the classrooms they would free, then weigh the ranking against land, cost, and hazard information that the model does not hold.

**Extensions.** Three extensions follow directly from the mathematics: waves of departure (one plan per wave, with the shelters already used carried forward), family integrity (whole families as flow units, which turns the plan into an integer program), and vehicle routing for the vulnerable, who often cannot walk to a pick-up point.

## 4.4 Applications

**For families.** A family in a danger zone can see, before an alert, which shelter its barangay is assigned to at each alert level, how long the trip takes, and whether the shelter is accessible for an older or disabled member.

**For barangay captains and school heads.** A school head can see in advance whether, and how many of, the school's classrooms are likely to be needed at each alert level, and can prepare learning materials for the classes that would move to modular or blended learning.

**For the PDRRMO, APSEMO, and DepEd.** During an alert, the plan can be recomputed in seconds when a shelter fills or a bridge fails; the clearance time tells the office how early the order must be given; and the channel closure analysis tells it which pockets must be emptied before heavy rain.

**For planners.** The siting tool proposes where a Ligtas Pinoy Center would shelter the most evacuees outside classrooms, and Proposition 10 guarantees the quality of the proposal.

**Links to the Sustainable Development Goals.** Every application above maps onto a specific target of the 2030 Agenda, although actual deployment remains a future step: open classrooms serve target 4.a, timely shelter for all serves targets 11.5 and 13.1, and placing vulnerable residents first serves target 10.2.

**Scalability.** Nothing in the framework is specific to Albay. Its only inputs are public registers, OpenStreetMap, and the Sphere indicator, and it runs on everyday computers; any province that houses evacuees in schools, from Taal to Kanlaon, could therefore adopt it.

# 5. REFERENCES

::: {custom-style="Reference"}
Ahuja, R. K., Magnanti, T. L., & Orlin, J. B. (1993). *Network flows: Theory, algorithms, and applications*. Prentice Hall.
:::

::: {custom-style="Reference"}
Bayram, V., Tansel, B. Ç., & Yaman, H. (2015). Compromising system and user interests in shelter location and evacuation planning. *Transportation Research Part B: Methodological, 72*, 146–163.
:::

::: {custom-style="Reference"}
Brimbuela, P. J. A., De Asis, D. J. Ll., & Shin, Y. (2026). *Right hospital, right bed, right time: A verified network model for mapping hospitals and routing patients in Albay by clinical need, live bed availability, and ability to pay* [Unpublished research paper]. Legazpi City Science High School.
:::

::: {custom-style="Reference"}
Church, R., & ReVelle, C. (1974). The maximal covering location problem. *Papers of the Regional Science Association, 32*(1), 101–118. https://doi.org/10.1007/BF01942293
:::

::: {custom-style="Reference"}
Daily Tribune. (2026, May 4). *DepEd urges Albay schools to prioritize safety as Mayon Volcano unrest intensifies, evacuation centers activated*. https://tribune.net.ph/2026/05/04/deped-tells-albay-schools-to-prioritize-safety-amid-mayon-unrest
:::

::: {custom-style="Reference"}
Department of Education. (2010). *Educational facilities manual* (Rev. ed.). Department of Education.
:::

::: {custom-style="Reference"}
Department of Education. (2021). *Masterlist of schools SY 2020–2021 based on LIS, as of January 15, 2021* [Data set].
:::

::: {custom-style="Reference"}
Department of Social Welfare and Development. (n.d.). *Disaster Response Operations Monitoring and Information Center (DROMIC) reports*. Retrieved October 17, 2026, from https://dromic.dswd.gov.ph
:::

::: {custom-style="Reference"}
Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. *Numerische Mathematik, 1*(1), 269–271. https://doi.org/10.1007/BF01386390
:::

::: {custom-style="Reference"}
Edmonds, J. (1970). Submodular functions, matroids, and certain polyhedra. In R. Guy, H. Hanani, N. Sauer, & J. Schönheim (Eds.), *Combinatorial structures and their applications* (pp. 69–87). Gordon and Breach.
:::

::: {custom-style="Reference"}
Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall.
:::

::: {custom-style="Reference"}
Estrada, J. (2024, December 6). *Jinggoy: Permanent evacuation centers for every city, municipality now a law* [Press release]. https://jinggoyestrada.ph/2024/12/06/jinggoy-permanent-evacuation-centers-for-every-city-municipality-now-a-law/
:::

::: {custom-style="Reference"}
Ford, L. R., Jr., & Fulkerson, D. R. (1958). Constructing maximal dynamic flows from static flows. *Operations Research, 6*(3), 419–433. https://doi.org/10.1287/opre.6.3.419
:::

::: {custom-style="Reference"}
Ford, L. R., Jr., & Fulkerson, D. R. (1962). *Flows in networks*. Princeton University Press.
:::

::: {custom-style="Reference"}
Fujishige, S. (2005). *Submodular functions and optimization* (2nd ed.). Elsevier.
:::

::: {custom-style="Reference"}
Gale, D. (1957). A theorem on flows in networks. *Pacific Journal of Mathematics, 7*(2), 1073–1082.
:::

::: {custom-style="Reference"}
Hamacher, H. W., & Tjandra, S. A. (2002). Mathematical modelling of evacuation problems: A state of the art. In M. Schreckenberg & S. D. Sharma (Eds.), *Pedestrian and evacuation dynamics* (pp. 227–266). Springer.
:::

::: {custom-style="Reference"}
Hoppe, B., & Tardos, É. (2000). The quickest transshipment problem. *Mathematics of Operations Research, 25*(1), 36–62.
:::

::: {custom-style="Reference"}
Interaksyon. (2026, January 6). *Philippines raises alert level at restive Mayon volcano*. Philstar.com. https://interaksyon.philstar.com/politics-issues/2026/01/06/307226/philippines-raises-alert-level-at-restive-mayon-volcano/
:::

::: {custom-style="Reference"}
Jenelius, E., Petersen, T., & Mattsson, L.-G. (2006). Importance and exposure in road network vulnerability analysis. *Transportation Research Part A: Policy and Practice, 40*(7), 537–560. https://doi.org/10.1016/j.tra.2005.11.003
:::

::: {custom-style="Reference"}
Kerby, D. S. (2014). The simple difference formula: An approach to teaching nonparametric correlation. *Comprehensive Psychology, 3*, Article 11.IT.3.1. https://doi.org/10.2466/11.IT.3.1
:::

::: {custom-style="Reference"}
Kongsomsaksakul, S., Yang, C., & Chen, A. (2005). Shelter location-allocation model for flood evacuation planning. *Journal of the Eastern Asia Society for Transportation Studies, 6*, 4237–4252.
:::

::: {custom-style="Reference"}
Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *The Annals of Mathematical Statistics, 18*(1), 50–60. https://doi.org/10.1214/aoms/1177730491
:::

::: {custom-style="Reference"}
Nemhauser, G. L., Wolsey, L. A., & Fisher, M. L. (1978). An analysis of approximations for maximizing submodular set functions, I. *Mathematical Programming, 14*(1), 265–294. https://doi.org/10.1007/BF01588971
:::

::: {custom-style="Reference"}
OpenStreetMap contributors. (2026). *OpenStreetMap* [Data set]. OpenStreetMap Foundation. https://www.openstreetmap.org
:::

::: {custom-style="Reference"}
PhilAtlas. (n.d.). *Albay*. Retrieved October 3, 2026, from https://www.philatlas.com/luzon/r05/albay.html
:::

::: {custom-style="Reference"}
Philippine Daily Inquirer. (2015). *Zero: Saving lives* [Pinas to Paris special report]. https://www.inquirer.net/climatechange/zero/
:::

::: {custom-style="Reference"}
Philippine Daily Inquirer. (2016). *Albay survivors remember 'Reming' a decade after*. https://newsinfo.inquirer.net/850250/albay-survivors-remember-reming-a-decade-after
:::

::: {custom-style="Reference"}
Philippine Daily Inquirer. (2026a). *4,000 students shift to modular, blended learning amid Mayon unrest*. https://newsinfo.inquirer.net/2166450/4000-students-shift-to-modular-blended-learning-amid-mayon-unrest
:::

::: {custom-style="Reference"}
Philippine Daily Inquirer. (2026b). *DepEd prepares for class opening in Bicol amid Mayon Volcano unrest*. https://newsinfo.inquirer.net/2230984/deped-prepares-for-class-opening-in-bicol-amid-mayon-volcano-unrest
:::

::: {custom-style="Reference"}
Philippine Institute of Volcanology and Seismology. (n.d.). *HazardHunterPH* [Web application]. Retrieved October 17, 2026, from https://hazardhunter.georisk.gov.ph
:::

::: {custom-style="Reference"}
Philippine Star. (2026, May 6). *Mayon ashfall affects 132 schools*. https://www.philstar.com/nation/2026/05/06/2525891/mayon-ashfall-affects-132-schools
:::

::: {custom-style="Reference"}
Philippine Statistics Authority. (2021). *The 2020 Census of Population and Housing (2020 CPH) population counts declared official by the President* [Press release]. https://psa.gov.ph/content/2020-census-population-and-housing-2020-cph-population-counts-declared-official-president
:::

::: {custom-style="Reference"}
ReliefWeb. (2023). *Philippines: Mayon Volcano - Jun 2023*. https://reliefweb.int/disaster/VO-2023-000099-PHL
:::

::: {custom-style="Reference"}
Republic Act No. 9994. (2010). *Expanded Senior Citizens Act of 2010*. Congress of the Philippines.
:::

::: {custom-style="Reference"}
Republic Act No. 10121. (2010). *Philippine Disaster Risk Reduction and Management Act of 2010*. Congress of the Philippines.
:::

::: {custom-style="Reference"}
Republic Act No. 10173. (2012). *Data Privacy Act of 2012*. Congress of the Philippines.
:::

::: {custom-style="Reference"}
Republic Act No. 10754. (2016). *An act expanding the benefits and privileges of persons with disability*. Congress of the Philippines.
:::

::: {custom-style="Reference"}
Republic Act No. 10821. (2016). *Children's Emergency Relief and Protection Act*. Congress of the Philippines.
:::

::: {custom-style="Reference"}
Republic Act No. 12076. (2024). *Ligtas Pinoy Centers Act: An act establishing evacuation centers for every city and municipality, and appropriating funds therefor*. Congress of the Philippines.
:::

::: {custom-style="Reference"}
Schools Division Office of Muntinlupa City. (2026). *Unnumbered memorandum No. 174, s. 2026* [Division memorandum on the use of schools as evacuation centers]. Department of Education. https://deped-muntinlupa.com/wp-content/uploads/2026/04/UN-2026-174.pdf
:::

::: {custom-style="Reference"}
Schrijver, A. (2003). *Combinatorial optimization: Polyhedra and efficiency*. Springer.
:::

::: {custom-style="Reference"}
Sherali, H. D., Carter, T. B., & Hobeika, A. G. (1991). A location-allocation model and algorithm for evacuation planning under hurricane/flood conditions. *Transportation Research Part B: Methodological, 25*(6), 439–452.
:::

::: {custom-style="Reference"}
Skutella, M. (2009). An introduction to network flows over time. In W. Cook, L. Lovász, & J. Vygen (Eds.), *Research trends in combinatorial optimization* (pp. 451–482). Springer.
:::

::: {custom-style="Reference"}
Spearman, C. (1904). The proof and measurement of association between two things. *The American Journal of Psychology, 15*(1), 72–101. https://doi.org/10.2307/1412159
:::

::: {custom-style="Reference"}
Sphere Association. (2018). *The Sphere handbook: Humanitarian charter and minimum standards in humanitarian response* (4th ed.). Sphere Association.
:::

::: {custom-style="Reference"}
United Nations General Assembly. (2015). *Transforming our world: The 2030 Agenda for Sustainable Development* (A/RES/70/1). United Nations. https://undocs.org/A/RES/70/1
:::

::: {custom-style="Reference"}
Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin, 1*(6), 80–83. https://doi.org/10.2307/3001968
:::

# APPENDIX A. OPEN DATA SOURCE REGISTER

Table A1 names the source behind each input of the model.

::: {custom-style="Paper Caption"}
**Table A1.** The source of each model layer.
:::

| Source | Publisher | Layer filled | Access |
|:-------------------|:--------------|:-------------------|:----------|
| Bicol Region extract of OpenStreetMap (OpenStreetMap contributors, 2026) | OpenStreetMap Foundation | Road graph, road classes, bridges | Open Database License |
| 2020 Census of Population and Housing (PSA, 2021) | Philippine Statistics Authority | Barangay populations; age structure for the vulnerable counts | Public release |
| HazardHunterPH and GeoRiskPH (PHIVOLCS, n.d.) | PHIVOLCS and partner agencies | Permanent and Extended Danger Zones, lahar and flood hazard areas | Public web application |
| Mayon volcano bulletins | PHIVOLCS | Alert levels and recommended danger zones | Public bulletins |
| Masterlist of schools (DepEd, 2021) | Department of Education | Schools, locations, enrollment | Public release |
| School building and classroom counts | DepEd Schools Division Offices | Classrooms $k_s$, learners per classroom $\ell_s$ | On request; public summaries |
| Educational facilities manual (DepEd, 2010) | Department of Education | Standard classroom size | Public document |
| Local disaster risk reduction and management plans | City and municipal DRRM offices | Designated evacuation centers | Varies by LGU |
| DROMIC reports (DSWD, n.d.) | Department of Social Welfare and Development | Evacuation centers actually used and evacuees per event (for validation) | Public reports |
| Sphere Handbook (Sphere Association, 2018) | Sphere Association | Space standard of 3.5 m² per person | Public document |
| Road layer of the companion study (Brimbuela et al., 2026) | Legazpi City Science High School | Landmark anchors, road attributes, travel times | Released with the project |

# APPENDIX B. DATA FILES PRODUCED

::: {custom-style="Paper Caption"}
**Table B1.** Files of the shelter data set.
:::

| File | Contents |
|:------------|:------------------------------------------------|
| origins.csv | Origin identifier, name, road node, hazard zones, population, vulnerable count, source and date |
| shelters.csv | Shelter identifier, name, kind, road node, floor areas, classrooms, learners per classroom, accessibility, hazard zones, contact |
| roads.csv | Arc identifier, from and to nodes, length, class, transit time, capacity, bridge flag, lahar channel |
| scenarios.json | Active zones and closed roads for each scenario of Table 4 |
| plan_<scenario>.csv | The plan: origin, class, shelter, tier, persons, travel time |
| results.json | Every number reported in Chapter 3, written by `verify_evacuation.py` |

# APPENDIX C. RULES FOR INCLUDING SHELTERS AND THE INVENTORY SCHEMA

**Inclusion criteria.** A building is added to the shelter inventory only if it satisfies each of the four conditions below.

1. It is named in a local disaster plan, in the DepEd masterlist, or in a DSWD report of an evacuation center in use.
2. Its coordinates are within 150 m of some road node, so the matching road node can be assigned by a fixed rule.
3. It lies outside the Permanent Danger Zone and outside every lahar and flood hazard area marked high on HazardHunterPH.
4. Its usable floor area is recorded, from a building plan or the DepEd standard, separately for open space and classrooms.

::: {custom-style="Paper Caption"}
**Table C1.** Fields of the shelter inventory.
:::

| Field | Type | Description |
|:------------|:--------|:--------------------------------------------|
| shelter_id | string | Fixed ID that the project assigns |
| name | string | Name spelled exactly as in the source register |
| kind | enum | evacuation center, Ligtas Pinoy Center, school, other public building |
| lat, lon | decimal | Published coordinate (WGS 84) |
| road_node | integer | Node of the road graph used as $n_s$ |
| area_ec_m2 | decimal | Non-school floor area $F^{ec}_s$ |
| area_open_m2 | decimal | School open-space area $F^{open}_s$ |
| classrooms | integer | Classrooms $k_s$ available as a last resort |
| learners_per_room | decimal | Average class size $\ell_s$ |
| accessible | boolean | Ground level or ramped, with an accessible toilet ($\alpha_s$) |
| hazard_zones | list | Zones the shelter lies in (normally none) |
| lgu_code | string | LGU code under the Philippine Standard Geographic Code |
| source, source_date | string, date | Register and date consulted |

# APPENDIX D. APPLICATION FEATURE CHECKLIST

The model is packaged as LIGTA-S, a companion to the MAP-A application built by the same team. Where a feature supports a specific SDG target, that target is named in parentheses at the end of the item.

**Planner mode (for the PDRRMO, APSEMO, and LGUs)**

1. A scenario switch for Alert Levels 3 and 4 and the compound lahar scenario, each with its active zones and closed bridges (targets 11.5 and 13.1).
2. An editable table of origins (population, vulnerable residents) and shelters (floor areas, classrooms, accessibility), with capacities from the Sphere indicator computed on entry.
3. The school-preserving plan of Algorithm 1, with persons per tier, classrooms closed, learners displaced, and classroom-days at a chosen length of stay (target 4.a).
4. The time-only plan and the nearest-site rule side by side, so that the classrooms saved and the extra minutes are visible.
5. The clearance time of Algorithm 2 with its lower bound, and the effect of closing each bridge or each lahar channel (target 11.5).
6. Greedy siting of Ligtas Pinoy Centers with the guarantee of Proposition 10 (target 11.5).

**Resident mode**

7. A barangay picker that shows the assigned shelter at each alert level, the travel time, and whether it is accessible (target 10.2).
8. A capacity calculator that converts a floor area into persons at 3.5 square meters each.
9. Offline storage, so that the plan opens without a signal during a typhoon (target 13.1).

# APPENDIX E. RISK REGISTER

No human subject faces any physical danger from this work. The risks lie in how its outputs are used, and Table E1 lists them.

::: {custom-style="Paper Caption"}
**Table E1.** Each risk and the safeguard against it.
:::

| Risk | Likelihood | Safeguard |
|:------------------|:---------|:----------------------------------------|
| Model output taken for a real measurement | High | Each computed value carries a model-output label, and every table marks the synthetic instance as synthetic. |
| Floor areas or classroom counts out of date | High | Each record keeps its source and date (Appendix C); sweeps bound the effect of capacity errors. |
| Plan used as an order instead of advice | Moderate | The plan is shown to the officer in charge, who confirms each assignment; the application never notifies residents automatically. |
| Families split between shelters | Moderate | Recognized as Limitation L4; the officer keeps families together when carrying out the plan. |
| A shelter becomes unsafe (ash, flood) | Moderate | Shelters can be switched off in the scenario, and the plan recomputed in seconds. |
| Unchecked software shortcut gives wrong plans | Moderate | All outputs were checked against independent reference code before analysis (Table 7). |
| Vulnerable residents miscounted | Moderate | Deficits are reported by municipality (hypothesis M7); barangay registries are the preferred source. |
| Personal information in origin data | Low | Only aggregate counts per barangay or purok are used (Republic Act No. 10173, 2012). |
| Code or data lost | Low | Remote backups under version control; each reported figure traces back to a script, a seed, and an input. |

# APPENDIX F. REPRODUCING THE RESULTS

One script, `verify_evacuation.py`, generates Tables 7 to 16 and Figures 2 and 3; the project repository stores it together with the model `evacmodel.py` and its output file `results.json`. With the seed 20261017, the script:

1. generates random synthetic instances and checks Propositions 1 to 5 and 9 against five sequential linear programs, a mixed-integer program, and recomputation after closures, added shelters, and nested scenarios;
2. checks Propositions 6 to 8 against the linear program of Ford and Fulkerson and a minute-by-minute scan;
3. checks Proposition 10 by testing diminishing returns on random triples and by exhaustive search over all sets of sites;
4. times Algorithms 1 and 2 on growing instances; and
5. builds instance E1, computes Tables 10 to 16, and draws Figures 2 and 3.

All numbers the script reports are model outputs computed from synthetic inputs; they describe no real shelter or school in Albay.

# ETHICS STATEMENT

This research was carried out entirely by computation. It involved no human participants and collected no personal data.

The road, hazard, school, shelter, and population inputs have only two origins: the public sources listed in Appendix A, and clearly labeled synthetic instances built for verification, instance E1 among them. Each source is used under the terms its publisher sets, and OpenStreetMap data are credited as the Open Database License demands (OpenStreetMap contributors, 2026).

Any plan must clear two checks before it reaches a local government: the protocol needs approval from the school's Scientific Review Committee, and the offices that own the real shelter records must confirm them. Care was taken at every stage to keep the data sound. No figure in this paper measures an actual evacuation.

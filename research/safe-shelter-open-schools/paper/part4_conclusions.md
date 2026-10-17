# 4. CONCLUSIONS

## 4.1 Evaluation of the Findings

This study set out to answer one main question. How can each evacuee from an Albay hazard zone receive a shelter so that vulnerable residents come first, everyone has a place, and the fewest classrooms close? The question also covered how much time such an evacuation would need. The findings show that such a plan can be stated precisely and solved exactly within seconds on a laptop. Separately written code confirms it, and it can be analyzed before any field survey.

**Objective 1: hazards, origins, roads, and shelters.** Scenarios, origins, the road network, and shelter capacities were defined from public registers and published standards (Definitions 1 to 6). A standard classroom holds 18 evacuees at the Sphere indicator, which turns the abstract rule "classrooms last" into a count that can be minimized.

**Objective 2: the lexicographic shelter plan.** The legal order of priorities became one minimum-cost flow. Plans are always in whole persons (Proposition 1), placing vulnerable residents first never costs anyone a place (Proposition 2), and the penalties reproduce the order exactly (Proposition 3). The plan matched five sequential linear programs at every level in all <<V1_N>> test instances.

**Objective 3: classrooms and alert levels.** Packing evacuees into full classrooms closes at most one more classroom per school in use than the true minimum (Proposition 4); in <<V2_EXACT>> of <<V2_N>> exact comparisons it closed none more. A higher alert level never frees classrooms (Proposition 5), which lets local governments plan once for the highest level.

**Objective 4: clearance time.** The time-expanded network gives the exact clearance time (Propositions 6 and 7) and agreed with the Ford-Fulkerson formula in all <<V3_N>> tests; bisection found it with about five maximum-flow computations instead of about 27. The lower bound of Proposition 8 was never violated.

**Objective 5: closures and new shelters.** Closures never shorten an evacuation and new shelters never add classroom use when everyone is already sheltered (Proposition 9); no violation appeared in <<V5_TOTAL>> checks. On E1, single bridges did not matter, but losing both lahar channels trapped <<E1_TRAPPED>> residents in a pocket served by one school.

**Objective 6: Ligtas Pinoy Center siting.** Because the extra coverage from new centers is submodular, greedy siting always attains no less than 63.2 percent of the optimum (Proposition 10). Across the test instances, greedy siting never dropped below <<V7_MIN_PCT>> percent of the optimum and matched it exactly in <<V7_OPT_PCT>> percent of them.

**Objective 7: verification.** Every proven property was checked against independently written code, and none failed (Table 7). Computing a plan for 160 origin clusters and 120 shelters took under three seconds in plain Python.

**Objective 8: worked instance and hypotheses.** The synthetic volcano makes the stakes concrete. At Alert Level 3 the school-preserving plan closed <<E1_ROOMS_LEX>> classrooms instead of <<E1_ROOMS_BLIND>> and displaced <<E1_LEARN_LEX>> learners instead of <<E1_LEARN_BLIND>>, at a cost of <<E1_EXTRA_MIN>> minutes of average travel; the nearest-site rule would have sent <<E1_OVER_AL3>> people to full shelters. Eight hypotheses for the open-data instance were fixed in advance (Section 3.6.3).

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

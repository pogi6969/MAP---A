::: {custom-style="Figure Para"}
![](/home/user/MAP---A/research/tools/assets/deped_header.png){width=2.3in}
:::

::: {custom-style="Title Main"}
Where People Go, Dengue Goes: A Verified Mobility-Coupled Network Model for Ranking Dengue Hotspots, Issuing Early Warnings, and Allocating Vector Control at Least Cost in Albay
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
Where People Go, Dengue Goes: A Verified Mobility-Coupled Network Model for Ranking Dengue Hotspots, Issuing Early Warnings, and Allocating Vector Control at Least Cost in Albay
:::

::: {custom-style="Center"}
*Brimbuela, Peter John A., De Asis, Dave Justin Ll., Shin, Yeaseong*
:::

::: {custom-style="Center"}
*Legazpi City Science High School, Legazpi City, Albay, Bicol Region (Region V)*
:::

 

Albay declared a state of calamity over dengue in September 2026 after reported cases rose by 84 percent over the year before. Cases are logged at the patient's home address, but the day-biting *Aedes aegypti* mosquito infects people where they spend their daylight hours, at school, at the market, and at work, so cleanup brigades and spraying are often sent to the wrong barangay. A model small enough for a laptop was built to link mosquito density in each barangay to the share of the day residents spend in every other barangay. Its reproduction number is the largest eigenvalue of a symmetric matrix, which yields four tools: bounds that flag where transmission can persist, a ranking of places by their share of transmission, a least-cost allocation of brigade team-days solved as a convex program with a certified optimality gap, and an inversion that moves case counts from homes to the places of infection. A Poisson CUSUM rule gives the outbreak alarm. Twelve propositions were proven, and each was tested on synthetic instances against independently written code; the reproduction number agreed with a numerical next-generation matrix to $5.3 \times 10^{-15}$ in 300 instances, and the control solver matched a fine grid and a general nonlinear solver in all 120 cases. On a six-barangay test network, homes pointed to a residential barangay, while 42.6 percent of transmission took place at the town center with the school and market; the least-cost plan reached the target with 22.60 team-days, 40 percent fewer than uniform spraying and 42 percent fewer than spraying where cases live. At an equal false-alarm rate, the CUSUM rule sounded on average 1.7 weeks earlier than a single-week threshold. Open data and routine case reports therefore suffice to target dengue control by place, supporting SDG 3. A pilot with barangay dengue brigades, led by the Provincial Health Office, is recommended.

**Keywords:** dengue, next-generation matrix, residence-time model, semidefinite optimization, CUSUM

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# 1. INTRODUCTION

The World Health Organization (2012) describes dengue as the most rapidly spreading mosquito-borne viral disease in the world, and most of its burden falls on Asia (Bhatt et al., 2013). The Philippines declared a national dengue epidemic on August 6, 2019, after more than 146,000 cases and 622 deaths in the first seven months of that year (United Nations Office for the Coordination of Humanitarian Affairs [OCHA], 2019). Seven years later the disease returned to Albay with force. By September 12, 2026, the province had logged 2,179 cases and 14 deaths, 84 percent more cases than in the same months of 2025; the Provincial Board declared a state of calamity, public schools closed for a week of cleanup and fogging, and the count passed 2,888 by September 21 (Daily Tribune, 2026a, 2026b, 2026c).

Every one of those cases was written down at a home address. Legazpi City led the provincial tally with 486 cases, followed by Bacacay, Daraga, Tabaco, and Malilipot (Daily Tribune, 2026b). The mosquito that carries dengue, *Aedes aegypti*, feeds during the day and seldom travels far from where it breeds, so a child is often bitten not in the bedroom but in the classroom, the jeepney terminal, or the market stall (Stoddard et al., 2013). A barangay can therefore post many cases while the mosquitoes that infected its residents live in another barangay altogether.

The Department of Health asks communities to follow its 4S strategy: search and destroy breeding sites, use self-protection, seek early consultation, and support fogging or spraying only in hotspots (Philippine Information Agency, n.d.). Each S needs a decision that mathematics can sharpen. Which places are the hotspots? How many team-days of cleanup are enough to stop transmission, and where should they go? When does a rise in reported cases mean an outbreak rather than ordinary noise?

This study answers those questions with a model of places and people. Barangays become the nodes of a network, the hours residents spend away from home become the weights of its links, and the condition "dengue cannot sustain itself" becomes an inequality on the largest eigenvalue of a matrix. Once the health problem is recast as linear algebra and convex optimization, what a plan achieves can be proven and the plan itself computed in seconds.

## 1.1 Statement of the Problem

The study begins with the people who fight dengue every season: the barangay health worker, the dengue brigade, the school head, and the provincial epidemiologist. Their problems, each paired with the piece of the model designed to answer it, appear in Table 1.

::: {custom-style="Paper Caption"}
**Table 1.** Dengue-control problems taken up here, each matched with the model component that answers it.
:::

| No. | Problem | What goes wrong | Model component |
|:---|:----------------------|:----------------------|:----------------------------|
| P1 | Cases are recorded where patients live, not where they were bitten | Cleanup and spraying go to homes while the source persists elsewhere | Residence-to-place inversion (Def. 11; Prop. 11) |
| P2 | Province-wide figures look moderate | Pockets of intense transmission stay hidden | Local exposure numbers and the averaging bound (Def. 7; Props. 4, 5) |
| P3 | Brigades have a fixed number of team-days | Effort is spread evenly or by guesswork | Least-cost control as a convex program (Defs. 9, 10; Props. 7 to 9) |
| P4 | Outbreaks are recognized only after wards fill | Response begins weeks late | Poisson CUSUM alarm with proven delay (Def. 12; Prop. 12) |
| P5 | No ranking says which place to treat first | The barangay with the most cases is treated first by default | Place shares of transmission and the hotspot score (Def. 8; Prop. 6) |
| P6 | Schools and markets draw people from many barangays | One busy place seeds cases across the town | Residence-time matrix (Defs. 2, 3) |
| P7 | The effect of a plan on the whole province is unknown | Success is judged only after the season | Network reproduction number (Def. 6; Props. 1, 2) |
| P8 | The rainy season multiplies mosquitoes | A plan that works in March fails in August | Season factor (Def. 13; Prop. 10) |
| P9 | Officials need assurance that a plan is enough | Plans are approved without a guarantee | Certificate program and certified interval (Props. 8, 9) |

## 1.2 Objectives of the Study

**General objective.** The aim was to construct a network model of dengue transmission in Albay that follows residents through their day, to prove its properties and confirm them by computation, and to use the model to rank hotspots, to allocate vector-control effort at least cost, to locate the places of infection behind reported cases, and to raise early outbreak alarms.

**Specific objectives.** More specifically, this work set out to:

1. represent barangays, their residents, their mosquitoes, and the hours residents spend in other barangays as a residence-time network built from open data;
2. derive the reproduction number of dengue on that network and prove its threshold property, its symmetric form, and computable bounds on it;
3. rank places by their share of transmission and prove that the ranking measures the effect of control at each place;
4. formulate the least-cost allocation of vector control as a convex program, give a quick certificate plan, and compute the exact plan with a certified gap;
5. recover the places of infection from cases counted by residence, with a proven error bound;
6. design an outbreak alarm with a proven worst-case delay and an exactly computed false-alarm rate;
7. test each proven property by computation, comparing the model code with separately written reference code on synthetic instances; and
8. run the complete pipeline on a small test network and state beforehand the hypotheses that the Albay instance will test.

## 1.3 Research Questions

**Primary question.** Assume a machine-readable model, assembled from public sources alone, describes Albay's barangays, their residents, the travel times linking them, and an index of mosquito density. Can such a model tell where dengue is transmitted, how much vector control is enough and where it should go, and when an outbreak has begun?

Each specific objective has a matching question below (Table 2).

**Q1.** Can the daily movement of residents between barangays be written as a matrix from travel times and the attraction of schools, markets, and workplaces?

**Q2.** What is the reproduction number of dengue on such a network, and can it be bounded by quantities that each barangay can compute for itself?

**Q3.** Does treating a province as one well-mixed population ever overstate its safety?

**Q4.** Which places carry the largest share of transmission, and does that share predict where control lowers the reproduction number fastest?

**Q5.** Is the least-cost allocation of vector control a problem that can be solved exactly, and how much does it save over spraying evenly or spraying where cases live?

**Q6.** Can cases counted at home be traced back to the places of infection, and how large can the error be?

**Q7.** How quickly does a CUSUM alarm detect a rise in cases, and how often does it sound falsely?

**Q8.** Do the proofs hold up when tested against separately written code, and what does the full pipeline reveal on a worked test network?

::: {custom-style="Paper Caption"}
**Table 2.** How the objectives, the questions, and the sections that answer them line up.
:::

| Objective | Questions | Where defined and proven | Where verified |
|:----------------|:-------|:--------------------|:----------------|
| 1. Residence-time network | Q1 | Defs. 1 to 5 | Tables 9, 10 |
| 2. Reproduction number and bounds | Q2, Q3 | Defs. 6, 7; Props. 1 to 5 | Table 7 (V1 to V3, V9); Table 11 |
| 3. Hotspot ranking | Q4 | Def. 8; Prop. 6 | Table 7 (V4); Table 11 |
| 4. Least-cost control | Q5 | Defs. 9, 10, 13; Props. 7 to 10 | Table 7 (V5, V6); Tables 12, 13 |
| 5. Places of infection | Q6 | Def. 11; Prop. 11 | Table 7 (V7); Table 14 |
| 6. Outbreak alarm | Q7 | Def. 12; Prop. 12 | Table 7 (V8); Table 15 |
| 7. Verification | Q8 | Section 3.3 | Tables 7, 8 |
| 8. Worked instance and hypotheses | Q8 | Sections 3.5, 3.6 | Tables 9 to 16 |

## 1.4 Review of Related Literature

### 1.4.1 Dengue and Its Vector

Dengue is caused by four related viruses and passed between people by *Aedes* mosquitoes, chiefly *Aedes aegypti*, which breeds in water held by containers around houses. Bhatt et al. (2013) estimated about 390 million infections a year worldwide, of which roughly a quarter show symptoms. The World Health Organization (2012) asks countries to cut dengue deaths and cases through integrated vector management, early detection, and surveillance. Because no drug treats dengue itself, control rests on the mosquito and on catching outbreaks early.

### 1.4.2 Dengue in the Philippines and in Albay

The Philippine dengue epidemic of 2019 showed how quickly cases can overwhelm health services: by late July of that year the Department of Health had recorded 146,062 cases and 622 deaths (OCHA, 2019). Edillo et al. (2015) estimated the economic cost of dengue in the country at hundreds of millions of US dollars a year. The disease is a notifiable condition under Republic Act No. 11332 (2019), so every confirmed or suspected case is reported to the surveillance system with the patient's address. In 2026 Albay's count rose sharply even while the national total stayed 24 percent below that of 2025 (Daily Tribune, 2026d), a reminder that dengue is a local problem that national averages can hide.

### 1.4.3 Reproduction Numbers for Mosquito-Borne Infections

Ross and Macdonald gave the first mathematical theory of malaria, and its quantities, such as the biting rate, the mosquito density per person, and the chance that a mosquito survives the incubation of the virus, still organize models of every mosquito-borne infection (Smith et al., 2012). The basic reproduction number counts the new infections one case produces in a fully susceptible population. Diekmann et al. (1990) defined it for heterogeneous populations as the spectral radius of a next-generation operator, and van den Driessche and Watmough (2002) gave the recipe used in this paper: split the infected compartments into new infections and transfers, linearize at the disease-free state, and take the spectral radius of the product of the two resulting matrices.

### 1.4.4 Human Movement and Dengue

Stoddard et al. (2009) argued that for a mosquito that stays near its breeding site, the movement of people, not of mosquitoes, links one neighborhood to another. In Iquitos, Peru, they later showed that the risk of infection followed the places a person visited, independent of how far those places were from home (Stoddard et al., 2013). Cosner et al. (2009) wrote such movement into a patch model in which each person spends a fixed share of time in each patch, the residence-time or Lagrangian approach, and showed that movement can keep an infection alive in places where it would die out on its own. This paper builds on that approach.

### 1.4.5 Uneven Exposure

Dye and Hasibeder (1986) proved that when some people are bitten more often than others, the reproduction number rises above the value computed from the average biting rate. Their insight carries over to places: a province where mosquitoes concentrate in a few barangays has more transmission potential than its average density suggests.

### 1.4.6 Weather and Dengue

Mosquito traits depend on temperature. Mordecai et al. (2017) fitted laboratory data for *Aedes aegypti* and found that transmission is possible between about 18 and 34 °C and peaks between 26 and 29 °C, the range of a Philippine rainy season. In Metro Manila, dengue cases have been linked to rainfall and temperature with lags of several weeks (Su, 2008; Sumi et al., 2017). This paper does not forecast weather; it lets the season scale the mosquito numbers and asks how the required control changes.

### 1.4.7 Vector Control and Its Evidence

Reviews find that the evidence for many vector-control methods is weaker than their popularity suggests. Space spraying by fogging kills adult mosquitoes for a short time but has limited measured effect on dengue when used alone (Esu et al., 2010), and community-based removal of breeding sites performs better when combined with other methods (Bowman et al., 2016). This is why the Department of Health limits fogging to hotspots, and why knowing where the hotspots are matters.

### 1.4.8 Detecting Outbreaks

Page (1954) introduced the cumulative sum (CUSUM) chart for detecting a shift in a process mean. Lucas (1985) adapted it to counts, such as weekly cases, and Brook and Evans (1972) showed how to compute its average run length by treating the statistic as a Markov chain. Dengue early-warning systems used by health ministries, such as the Early Warning and Response System promoted by the World Health Organization, compare weekly counts with an endemic channel built from past years (Hussain-Alkhateeb et al., 2018).

### 1.4.9 Matrix Tools

Three classic results of matrix theory carry the proofs of this paper. The Perron-Frobenius theory and the Collatz-Wielandt bounds locate the spectral radius of a nonnegative matrix between the smallest and largest ratios $(Mx)_i / x_i$ for any positive vector $x$ (Horn & Johnson, 2013). The largest eigenvalue of a symmetric matrix that depends linearly on parameters is a convex function of them (Overton, 1988; Boyd & Vandenberghe, 2004), which makes semidefinite programming possible (Vandenberghe & Boyd, 1996). And a matrix whose diagonal dominates its rows is invertible with a computable bound on its inverse (Varah, 1975).

### 1.4.10 Open Data for Dengue Planning

The 2020 census gives the population of every barangay (Philippine Statistics Authority [PSA], 2021). The Department of Health publishes weekly surveillance summaries, and the provincial health office releases case counts by municipality during outbreaks. The Department of Education masterlist locates every public school (Department of Education [DepEd], 2021). An earlier study by this team modeled Albay's roads and public transport and computed travel times between landmarks (Brimbuela et al., 2026); those times feed the present model.

## 1.5 Research Gap

Six gaps remain after this review.

* **(G1) Cases by home, infections by place.** Surveillance records addresses, and control follows addresses. No tool available to an Albay health office converts cases by residence into infections by place.
* **(G2) No provincial reproduction number with movement.** Models with residence times exist in the literature, but none has been built for a Philippine province from open data, and none turns the reproduction number into bounds a barangay can compute for itself.
* **(G3) No least-cost allocation with a guarantee.** Brigades and budgets are limited, yet no method tells a local government the cheapest allocation that provably brings transmission below its threshold.
* **(G4) No ranking of places.** Hotspots are named by case counts. No ranking measures how much transmission each place carries.
* **(G5) Alarms without guarantees.** Thresholds based on past years are easy to read, but their delay and false-alarm rate are rarely computed.
* **(G6) No verification.** Planning tools in print rarely demonstrate that their formulas were tested against an independent implementation.

## 1.6 Contributions of the Study

* **C1. A residence-time network for Albay.** Sections 2.1 to 2.3 turn travel times, the pull of schools and markets, and mosquito indices into a matrix of hours spent by each barangay's residents in every other barangay.
* **C2. A reproduction number with local bounds.** Propositions 1, 4, and 5 show that the reproduction number is the largest eigenvalue of a symmetric matrix, lies between the smallest and largest local exposure numbers, and is never below the province-average value.
* **C3. A hotspot ranking with meaning.** Proposition 6 splits the reproduction number into shares by place and shows that each share measures how fast control at that place lowers transmission.
* **C4. Least-cost control with a certified gap.** Propositions 7 to 9 prove that the least-cost allocation is a convex program, give a linear program whose solution is always safe, and certify how far the computed plan can be from the best.
* **C5. Infections traced to places.** Proposition 11 proves that cases by residence determine infections by place whenever residents spend more than half of their day at home, with an explicit error bound.
* **C6. An alarm with proven delay.** Proposition 12 bounds the delay of the CUSUM alarm and computes its false-alarm rate exactly.
* **C7. A verified, open pipeline.** Each input can be followed back to a public register (Appendix A); one seeded script regenerates all results (Appendix F); and separately written code tested each proven property.

Of the twelve propositions in Section 3.2, Propositions 2 and 3 restate standard results (van den Driessche & Watmough, 2002), and parts of Propositions 4, 11, and 12 apply named theorems (Horn & Johnson, 2013; Varah, 1975; Brook & Evans, 1972) to this model. Everything else, including the formulations and the other results, was developed by the researchers.

## 1.7 Scope and Delimitation

This study covers Albay province at the barangay level and dengue carried by *Aedes aegypti*. It is entirely computational: no mosquito was collected, no patient was examined, and no case record was opened. Every figure in the findings was produced by a proof, a synthetic test instance, or a public report.

The model treats dengue as one virus. It does not distinguish the four serotypes, model immunity across seasons, or predict severe dengue. It ranks places and allocates effort; it does not diagnose patients, replace the judgment of the provincial epidemiologist, or decide which chemical to use. Whatever method a brigade uses, the model sees only how much it lowers mosquito numbers.

## 1.8 Contribution to the Sustainable Development Goals

SDG 3 (Good Health and Well-being) is the goal served most directly. Target 3.3 calls for ending epidemics of neglected tropical diseases, dengue among them, and target 3.d for stronger early warning and better handling of health risks (United Nations General Assembly [UNGA], 2015). The CUSUM alarm addresses target 3.d, and the least-cost control addresses target 3.3. The hotspot ranking often singles out schools as places of transmission, so target 4.a (safe learning environments) is touched as well, while the open data set relates to target 17.18. None of these links has been measured in practice; they describe intended uses of a model that is still to be field-tested.

::: {custom-style="Figure Para"}
![](/home/user/MAP---A/research/where-people-go-dengue/paper/fig_sdg.png){width=4.2in}
:::

::: {custom-style="Source Line"}
SDG icons: United Nations
:::


## 1.9 How Mathematics and Computational Sciences Come into Play

This is a study in Mathematics and Computational Sciences in a precise sense: each of its three parts does work that the other two cannot.

* **Mathematics** states the problem exactly. Daily movement becomes a residence-time matrix, transmission becomes a symmetric matrix whose largest eigenvalue is the reproduction number, and the cheapest effective control becomes a convex program. Twelve propositions then fix what the model guarantees.
* **Computation** turns those statements into answers. An eigen-solver gives the reproduction number and the place shares for all 720 barangays in under a second, an interior-point method finds the least-cost plan with a certified gap, and a Markov chain gives the exact run length of the alarm.
* **Science** keeps the work honest. Inputs come from public registers and published parameter ranges, every proposition was tested against separately written code, and every number in Chapter 3 is reproduced by one seeded script.

Together the three move from open data to a matrix, from the matrix to an algorithm, from the algorithm to numbers, and from the numbers to a control plan that is both cheapest and proven (Figure 1).


# 2. FRAMEWORK

The model is built in three layers (Figure 1). The movement layer (Sections 2.1 and 2.2) records where the residents of each barangay spend their daylight hours. The transmission layer (Sections 2.3 to 2.5) adds mosquitoes, writes the equations of infection, and extracts the reproduction number and its parts. The decision layer (Sections 2.6 to 2.9) turns those quantities into a control plan, a map of infection places, and an outbreak alarm.

::: {custom-style="Figure Para"}
![](/home/user/MAP---A/research/where-people-go-dengue/paper/fig_framework.png){width=6.3in}
:::

::: {custom-style="Figure Caption"}
**Figure 1.** From open data to dengue decisions. The movement layer is drawn in blue, the transmission layer in orange, and the decision layer in green.
:::

## 2.1 Study Area and Barangays

At the 2020 census, Albay's 18 cities and municipalities held 720 barangays and 1,374,768 residents (PSA, 2021). Table 3 shows the municipalities that reported the most dengue cases during the 2026 surge.

::: {custom-style="Paper Caption"}
**Table 3.** Dengue in Albay during the 2026 surge, as reported by the provincial government (Daily Tribune, 2026b, 2026c).
:::

| Item | Value |
|:-------------------------------|:----------------------|
| Cases, January 1 to September 12, 2026 | 2,179 (14 deaths) |
| Cases in the same period of 2025 | 1,183 |
| Cases by September 21, 2026 | 2,888 |
| Municipalities with the most cases (by residence) | Legazpi City 486; Bacacay 296; Daraga 220; Tabaco City 181; Malilipot 171 |
| Response | State of calamity; barangay dengue brigades reactivated; public schools closed September 14 to 18 for cleanup and fogging |

**Definition 1 (Barangay network).** The study area is a set $B = \{1, \dots, n\}$ of barangays. Barangay $i$ has $N_i$ residents and a center $o_i$, a landmark such as the barangay hall. The travel time $T_{ij}$ in minutes is the door-to-door trip time from $o_i$ to $o_j$ by public transport and on foot, as given by the companion study's timetable model (Brimbuela et al., 2026), with $T_{ii} = 0$.

## 2.2 Where Residents Spend the Day

**Definition 2 (Time away and destination choice).** During the hours when *Aedes aegypti* bites, a resident of barangay $i$ spends a share $\omega_i \in [0, 1)$ of the time away from home. Time away is divided among the other barangays in proportion to how strongly each attracts visitors and how close it is:

$$\pi_{ij} = \frac{A_j \, e^{-\beta T_{ij}}}{\sum_{k \neq i} A_k \, e^{-\beta T_{ik}}} \quad (j \neq i)$$

EQNUM:(1)

::: {custom-style="Source Line"}
Source: a gravity-type destination choice; Cosner et al. (2009) for the residence-time framing
:::

where $A_j > 0$ is the attraction of barangay $j$ (school seats, market stalls, and jobs, from the registers of Appendix A) and $\beta > 0$ sets how fast attraction fades with travel time.

**Definition 3 (Residence-time matrix).** The matrix $P = [p_{ij}]$ records the share of biting hours that residents of $i$ spend in $j$:

$$p_{ii} = 1 - \omega_i, \qquad p_{ij} = \omega_i \, \pi_{ij} \ (j \neq i), \qquad \tilde{N}_j = \sum_{k} p_{kj} N_k$$

EQNUM:(2)

::: {custom-style="Source Line"}
Source: this study, after the Lagrangian patch model of Cosner et al. (2009)
:::

Each row of $P$ sums to one. The number $\tilde{N}_j$ is the average number of people present in barangay $j$ during biting hours: residents who stay plus visitors who come. A town center with a large school can host far more people by day than live there.

## 2.3 Mosquitoes and Transmission

**Definition 4 (Mosquito density).** Barangay $j$ holds $V_j$ adult female mosquitoes at equilibrium, estimated from larval or ovitrap surveys. The density that matters for transmission is the number of mosquitoes per person present:

$$m_j = \frac{V_j}{\tilde{N}_j}$$

EQNUM:(3)

::: {custom-style="Source Line"}
Source: this study; the classic density $m$ of Ross-Macdonald theory (Smith et al., 2012) measured per person present
:::

**Definition 5 (Residence-time host-vector model).** Residents of $i$ are susceptible ($S_{h,i}$), infectious ($I_{h,i}$), or recovered ($R_{h,i}$); mosquitoes in $j$ are susceptible ($S_{v,j}$), incubating the virus ($E_{v,j}$), or infectious ($I_{v,j}$). With biting rate $a$, transmission probabilities $b$ (mosquito to person) and $c$ (person to mosquito), human recovery rate $\gamma$, human birth and death rate $\mu_h$, mosquito death rate $\mu_v$, rate $\nu$ of completing the extrinsic incubation, and mosquito recruitment $\Lambda_j = \mu_v V_j$,

$$\begin{aligned}
\dot S_{h,i} &= \mu_h N_i - \lambda_{h,i} S_{h,i} - \mu_h S_{h,i}, &\quad \lambda_{h,i} &= a b \sum_j p_{ij} \frac{I_{v,j}}{\tilde N_j},\\
\dot I_{h,i} &= \lambda_{h,i} S_{h,i} - (\gamma + \mu_h) I_{h,i}, &\quad \lambda_{v,j} &= a c\, \frac{\sum_k p_{kj} I_{h,k}}{\tilde N_j},\\
\dot R_{h,i} &= \gamma I_{h,i} - \mu_h R_{h,i}, & \dot S_{v,j} &= \Lambda_j - \lambda_{v,j} S_{v,j} - \mu_v S_{v,j},\\
\dot E_{v,j} &= \lambda_{v,j} S_{v,j} - (\nu + \mu_v) E_{v,j}, & \dot I_{v,j} &= \nu E_{v,j} - \mu_v I_{v,j}.
\end{aligned}$$

EQNUM:(4)

::: {custom-style="Source Line"}
Source: this study, a residence-time version of the Ross-Macdonald model (Cosner et al., 2009; Smith et al., 2012)
:::

The forces of infection follow from where bites happen: a mosquito in $j$ bites $a$ times a day, and its bites fall on the people present in $j$ in proportion to the time they spend there. A resident of $i$ therefore receives a share $p_{ij}/\tilde{N}_j$ of the bites made in $j$.

::: {custom-style="Paper Caption"}
**Table 4.** Parameters of the transmission model. The researchers declared these design values within the published ranges for *Aedes aegypti* at about 28 °C (Mordecai et al., 2017) and for Ross-Macdonald models (Smith et al., 2012); Section 3.6 varies them in sensitivity sweeps.
:::

| Symbol | Meaning | Value |
|:----|:-------------------------------------|----------:|
| $a$ | bites per mosquito per day | 0.29 |
| $b$ | chance that an infectious bite infects a person | 0.50 |
| $c$ | chance that biting an infectious person infects the mosquito | 0.50 |
| $1/\mu_v$ | mean life of an adult mosquito (days) | 10 |
| $1/\nu$ | extrinsic incubation period (days) | 8 |
| $1/\gamma$ | infectious period of a person (days) | 5 |
| $1/\mu_h$ | human life expectancy (years) | 70 |
| $\kappa$ | two-generation constant of Equation (5) | 0.584 |

## 2.4 The Reproduction Number

**Definition 6 (Two-generation matrix and reproduction number).** Following van den Driessche and Watmough (2002), the infected states are $I_h$ (persons) and $E_v$, $I_v$ (mosquitoes). Linearizing Equation (4) at the disease-free state gives the next-generation matrix $K$, whose spectral radius is the basic reproduction number $\mathcal{R}_0 = \rho(K)$. Two generations of $K$, person to mosquito and mosquito to person, combine into the matrix

$$M = \kappa\, D_N\, P\, W\, P^{\top}, \qquad W = \mathrm{diag}\Big(\frac{V_j}{\tilde N_j^{\,2}}\Big), \qquad \kappa = \frac{a^2 b c\, \nu}{\mu_v (\nu + \mu_v)(\gamma + \mu_h)}, \qquad \mathcal{R}_0 = \sqrt{\rho(M)}$$

EQNUM:(5)

::: {custom-style="Source Line"}
Source: this study, by the next-generation method of van den Driessche and Watmough (2002)
:::

where $D_N = \mathrm{diag}(N_1, \dots, N_n)$. The entry $M_{ik}$ is the expected number of residents of $i$ infected, through mosquitoes, by one infectious resident of $k$. With one barangay and no movement, $\mathcal{R}_0^2 = \kappa m$, the familiar Ross-Macdonald number.

**Definition 7 (Local exposure number).** For barangay $i$,

$$\mathcal{R}_i = \kappa \sum_{j} p_{ij}\, m_j$$

EQNUM:(6)

::: {custom-style="Source Line"}
Source: this study
:::

is the Ross-Macdonald number its residents would face if the mosquito density they meet, averaged over where they spend the day, applied everywhere. Each barangay can compute its own $\mathcal{R}_i$ from its row of $P$ and the densities of the places its residents visit.

## 2.5 How Much Transmission Each Place Carries

Let $S$ be the symmetric matrix of Proposition 1, $v$ its unit eigenvector for the largest eigenvalue, and $q_j = D_N^{1/2} P e_j$ the $j$-th column of $D_N^{1/2} P$.

**Definition 8 (Place share and hotspot score).** The share of transmission carried by place $j$ and its hotspot score per team-day are

$$s_j = \frac{\kappa\, w_j\, (q_j^{\top} v)^2}{\mathcal{R}_0^2}, \qquad H_j = \frac{\kappa\, w_j\, (q_j^{\top} v)^2}{c_j}, \qquad w_j = \frac{V_j}{\tilde N_j^{\,2}}$$

EQNUM:(7)

::: {custom-style="Source Line"}
Source: this study (Proposition 6)
:::

where $c_j$ is the cost of full control at $j$ (Definition 9). A large share means that much of the province's transmission passes through mosquitoes in $j$; a large score means that each team-day spent at $j$ lowers the reproduction number by much.

## 2.6 Vector Control at Least Cost

**Definition 9 (Control and its cost).** A control plan is a vector $u = (u_1, \dots, u_n)$ in which $u_j \in [0, \bar u_j]$ is the fraction by which cleanup, larviciding, and spraying reduce the mosquitoes of place $j$; $\bar u_j < 1$ is the most that is achievable. Under plan $u$,

$$V_j(u) = (1 - u_j)\, V_j, \qquad \text{cost}(u) = \sum_j c_j\, u_j$$

EQNUM:(8)

::: {custom-style="Source Line"}
Source: this study
:::

where $c_j$ is the number of brigade team-days needed for full control at $j$. In this paper $c_j$ is the number of households divided by 50, the households one team can treat in a day, and $\bar u_j = 0.8$; both are declared values.

**Definition 10 (Least-cost control program).** For a target $r < 1$, the least-cost plan solves

$$\min_{u}\ \sum_j c_j u_j \quad \text{subject to} \quad \mathcal{R}_0(u) \le r, \quad 0 \le u_j \le \bar u_j$$

EQNUM:(9)

::: {custom-style="Source Line"}
Source: this study
:::

and the *certificate program* replaces the constraint on $\mathcal{R}_0(u)$ by one linear inequality per barangay:

$$\min_{u}\ \sum_j c_j u_j \quad \text{subject to} \quad \kappa \sum_j p_{ij}\, m_j\, (1 - u_j) \le r^2 \ \ \text{for every } i, \quad 0 \le u_j \le \bar u_j$$

EQNUM:(10)

::: {custom-style="Source Line"}
Source: this study (Proposition 8)
:::

Program (10) is a linear program and is solved in milliseconds. Program (9) is solved by Algorithm 1, an interior-point method that also returns a lower bound, so the user knows how far the plan can be from the best possible one.

::: {custom-style="Paper Caption"}
**Algorithm 1.** Least-cost control with a certified gap.
:::

```
Input : P, N, V, parameters; costs c; limits u_bar; target r
Output: plan u with R0(u) <= r; certified interval [lower, upper]
 1  if R0(0) <= r: return u = 0
 2  if R0(u_bar) >= r: report "target not reachable"
 3  start at u slightly inside u_bar (strictly feasible); t <- 3n / cost(u)
 4  repeat
 5      center: Newton steps on  t*cost(u) - log det(r^2 I - S(u))
                                 - sum log u_j - sum log(u_bar_j - u_j)
            (scaled Cholesky solve, backtracking that keeps r^2 I - S(u) > 0)
 6      upper <- cost(u);  Z <- (r^2 I - S(u))^-1
 7      lower <- max(lower, g(sZ)) maximized over s >= 0   (Proposition 9)
 8      t <- mu * t
 9  until upper - lower <= 1e-6 * upper
10  return u, lower, upper
```

## 2.7 Where People Get Infected

**Definition 11 (Residence-to-place inversion).** Let $y_i$ be the new cases among residents of $i$ in a period, divided by $N_i$, and let $z_j$ be the infection pressure at place $j$, the chance per person-period of being infected while there. If infection happens where people spend their time, then

$$y = P\, z, \qquad \text{infections at place } j = z_j\, \tilde N_j$$

EQNUM:(11)

::: {custom-style="Source Line"}
Source: this study
:::

and $z$ is recovered from reported cases by nonnegative least squares (Lawson & Hanson, 1974), which keeps every pressure at zero or above (Algorithm 2).

::: {custom-style="Paper Caption"}
**Algorithm 2.** Infections by place from cases by residence.
:::

```
Input : cases by barangay of residence over a period; residents N; matrix P
Output: infection pressure z and infections by place
 1  y_i <- cases_i / N_i
 2  z <- argmin ||P z - y||  subject to z >= 0   (Lawson-Hanson)
 3  infections at place j <- z_j * Ntilde_j
 4  report the error bound of Proposition 11 when every p_ii > 1/2
```

## 2.8 The Outbreak Alarm

**Definition 12 (Poisson CUSUM).** Let $x_t$ be the cases reported in week $t$ and $\mu_t$ the expected count in that week of a normal year. To detect a rise to $\theta \mu_t$, the CUSUM statistic and its alarm are

$$S_t = \max\{0,\; S_{t-1} + x_t - k_t\}, \qquad k_t = \frac{(\theta - 1)\,\mu_t}{\ln \theta}, \qquad \text{alarm at the first } t \text{ with } S_t \ge h$$

EQNUM:(12)

::: {custom-style="Source Line"}
Source: Page (1954); reference value for counts after Lucas (1985)
:::

with $S_0 = 0$. This paper uses $\theta = 1.5$, a rise of one half, and sets $h$ so that a normal year raises a false alarm with probability 0.05. For comparison, the *single-week rule* sounds when one week's count exceeds $\mu_t + z\sqrt{\mu_t}$, with $z$ set to the same false-alarm probability.

::: {custom-style="Paper Caption"}
**Algorithm 3.** Alarm and its average run length.
:::

```
Input : weekly counts x_t; baseline mu_t; rise theta; threshold h
Output: alarm week, or none; average run length when k and h are integers
 1  S <- 0
 2  for t = 1, 2, ...:  S <- max(0, S + x_t - k_t);  if S >= h: return t
 3  average run length: states 0..h-1, Q[i][j] = P(next state j | state i)
    under Poisson counts; ARL = ((I - Q)^-1 1) at state 0   (Brook & Evans, 1972)
```

## 2.9 Seasons

**Definition 13 (Season factor).** Rain and temperature change the number of mosquitoes. A season factor $\varsigma > 0$ scales every $V_j$ to $\varsigma V_j$; $\varsigma = 1$ is the reference season of the survey, and values above one describe the peak of the rainy season.

## 2.10 Strategies Compared

Five allocations of the same effort are compared in Section 3.5. *Uniform* reduces mosquitoes by the same fraction everywhere. *Where cases live* reduces them in proportion to the share of cases by residence during the growth of an outbreak, which is the dominant eigenvector of $M$. *Place shares* reduces them in proportion to $s_j$. *Certificate* solves program (10), and *least cost* solves program (9). The first three are scaled up until they reach the target.

## 2.11 Assumptions

* **Assumption 1 (Fixed routines).** The shares $p_{ij}$ do not change during an outbreak. School closures, which change them, are studied by recomputing $P$.
* **Assumption 2 (One virus).** The four serotypes are treated as one infection with lasting immunity during a season.
* **Assumption 3 (Equilibrium mosquitoes).** Without control, mosquito numbers sit at the level $V_j$ set by the season.
* **Assumption 4 (Control lowers numbers).** Every control method acts by lowering the adult mosquitoes of a place by a fraction $u_j$, at a cost proportional to $u_j$.
* **Assumption 5 (Reports follow infections).** Within a period, reported cases are a fixed fraction of infections in every barangay, so that rates of reported cases can stand in for rates of infection in Equation (11).
* **Assumption 6 (Open data only).** Each number reported here is a derivation, a declared parameter, a figure from a public report, or an output of a synthetic test instance. No surveillance record, survey sheet, or patient file was used.

## 2.12 Notation

::: {custom-style="Paper Caption"}
**Table 5.** Symbols used in the paper.
:::

| Symbol | Meaning |
|:-----------------|:---------------------------------------------|
| $B$, $n$, $N_i$ | barangays; their number; residents of $i$ |
| $T_{ij}$, $A_j$, $\beta$, $\omega_i$ | travel time; attraction; decay; share of time away |
| $P = [p_{ij}]$, $\tilde N_j$ | residence-time matrix; people present in $j$ |
| $V_j$, $m_j$ | mosquitoes in $j$; mosquitoes per person present |
| $a, b, c, \mu_v, \nu, \gamma, \mu_h$ | transmission parameters (Table 4) |
| $\kappa$, $M$, $S$, $\mathcal{R}_0$ | two-generation constant; two-generation matrix; its symmetric form; reproduction number |
| $\mathcal{R}_i$ | local exposure number of barangay $i$ |
| $s_j$, $H_j$, $v$, $q_j$ | place share; hotspot score; top eigenvector of $S$; column $j$ of $D_N^{1/2} P$ |
| $u_j$, $\bar u_j$, $c_j$, $r$ | control at $j$; its limit; its cost; target |
| $y_i$, $z_j$ | case rate by residence; infection pressure by place |
| $x_t$, $\mu_t$, $k_t$, $h$, $S_t$ | weekly cases; baseline; reference value; threshold; CUSUM statistic |
| $\varsigma$ | season factor |


# 3. FINDINGS

## 3.0 Data and Integrity of the Results

Two kinds of evidence support the findings: mathematical proof and computation on synthetic data. The model is coded in `denguemodel.py`, and `verify_dengue.py` tests it against separately written reference code and builds the worked example of Section 3.5. The scripts ran with the seed 20261017 and saved every number below in `results.json` (Appendix F). The six barangays of Section 3.5 are invented; none of their figures describes a real barangay, school, or market in Albay.

## 3.1 General Methods

The study moved through eight steps.

**Step 1: Barangays and residents.** Barangay populations and centers were taken from the census and the landmark registers of the companion study.

**Step 2: Travel and attraction.** Travel times between barangay centers came from the timetable model of Brimbuela et al. (2026); attraction came from school enrollment, market listings, and workplaces (Appendix A).

**Step 3: Residence-time matrix.** Equations (1) and (2) produced $P$ and the daytime populations $\tilde N_j$.

**Step 4: Mosquitoes.** Mosquito numbers enter as survey indices converted to adults per resident; in the worked example they are declared values.

**Step 5: Transmission quantities.** The reproduction number, the local exposure numbers, and the place shares were computed from the symmetric matrix of Proposition 1.

**Step 6: Control.** The five strategies of Section 2.10 were computed for the same target, and the season factor was varied.

**Step 7: Places of infection and alarms.** Algorithm 2 was applied to cases by residence and Algorithm 3 to weekly counts.

**Step 8: Verification.** Section 3.3 tests every proven property against an independent implementation on random synthetic instances, and Section 3.4 reports running times.

## 3.2 Theoretical Results

**Proposition 1 (The reproduction number is a symmetric eigenvalue).** The matrix $M$ of Equation (5) is similar to

$$S = \kappa\, D_N^{1/2} P\, W P^{\top} D_N^{1/2} = \kappa \sum_{j} w_j\, q_j q_j^{\top}$$

EQNUM:(13)

::: {custom-style="Source Line"}
Source: this study (Proposition 1)
:::

which is symmetric and positive semidefinite. Hence every eigenvalue of $M$ is real and nonnegative, and $\mathcal{R}_0^2 = \lambda_{\max}(S) = \max_{x \neq 0} x^{\top} S x / x^{\top} x$.

*Proof.* Order the infected states as $(I_h, E_v, I_v)$. At the disease-free state $S_{h,i} = N_i$ and $S_{v,j} = V_j$. New infections of people come only from infectious mosquitoes, with rate matrix $A_{ij} = a b N_i p_{ij}/\tilde N_j$; new infections of mosquitoes come only from infectious people, with rate matrix $C_{jk} = a c V_j p_{kj}/\tilde N_j$. The transfer matrix is block lower triangular, with blocks $(\gamma+\mu_h) I$ for people and, for mosquitoes, diagonal blocks $(\nu + \mu_v) I$ and $\mu_v I$ with $-\nu I$ below the diagonal. Multiplying the new-infection matrix by the inverse of the transfer matrix leaves two nonzero blocks: people infected per incubating mosquito, $A\,\nu/(\mu_v(\nu+\mu_v))$, and incubating mosquitoes per infectious person, $C/(\gamma+\mu_h)$; the rows of $I_v$ are zero. A block matrix with zero diagonal blocks and off-diagonal blocks $X$ and $Y$ has spectral radius $\sqrt{\rho(XY)}$, and

$$(XY)_{ik} = \frac{\nu}{\mu_v(\nu+\mu_v)(\gamma+\mu_h)} \sum_j \frac{a b N_i p_{ij}}{\tilde N_j}\cdot\frac{a c V_j p_{kj}}{\tilde N_j} = \kappa N_i \sum_j p_{ij}\, w_j\, p_{kj} = M_{ik}$$

EQNUM:(14)

::: {custom-style="Source Line"}
Source: this study (proof of Proposition 1)
:::

so $\mathcal{R}_0 = \sqrt{\rho(M)}$. Finally $D_N^{-1/2} M D_N^{1/2} = S$, and $S = Q W Q^{\top}$ with $Q = D_N^{1/2} P$ and $W$ diagonal and nonnegative, so $x^{\top} S x = \sum_j w_j (q_j^{\top} x)^2 \ge 0$. Similar matrices share eigenvalues, and the largest eigenvalue of a symmetric matrix is the maximum of its Rayleigh quotient (Horn & Johnson, 2013). □

**Proposition 2 (Threshold; van den Driessche & Watmough, 2002).** The disease-free state of Equation (4) is locally asymptotically stable when $\mathcal{R}_0 < 1$ and unstable when $\mathcal{R}_0 > 1$.

*Proof.* The model meets the five conditions of van den Driessche and Watmough (2002): every compartment is nonnegative; new infections are nonnegative and vanish without infected individuals; transfers out of a compartment are nonnegative; transfers vanish at zero; and, without infection, people return to $S_{h,i} = N_i$ and mosquitoes to $S_{v,j} = V_j$ at the rates $\mu_h$ and $\mu_v$. Their Theorem 2 then gives the result. □

**Proposition 3 (The model stays meaningful).** Starting from nonnegative values with $S_{h,i} + I_{h,i} + R_{h,i} = N_i$, every state stays nonnegative, each barangay keeps $N_i$ residents, and the mosquitoes of each place approach $V_j$.

*Proof.* Whenever a state is zero, its derivative in Equation (4) is nonnegative, so no trajectory can leave the nonnegative orthant. Adding the three human equations gives $\frac{d}{dt}(S_{h,i}+I_{h,i}+R_{h,i}) = \mu_h (N_i - S_{h,i} - I_{h,i} - R_{h,i})$, which is zero on $N_i$. Adding the three mosquito equations gives $\dot V = \mu_v (V_j - V)$, whose solution tends to $V_j$. □

**Proposition 4 (Local exposure numbers bound the reproduction number).** For every residence-time network,

$$\min_i \mathcal{R}_i \;\le\; \mathcal{R}_0^2 \;\le\; \max_i \mathcal{R}_i$$

EQNUM:(15)

::: {custom-style="Source Line"}
Source: this study, by the Collatz-Wielandt theorem (Horn & Johnson, 2013)
:::

*Proof.* Multiply $M$ by the vector of populations: $(MN)_i = \kappa N_i \sum_j p_{ij} w_j \sum_k p_{kj} N_k = \kappa N_i \sum_j p_{ij} V_j/\tilde N_j = N_i \mathcal{R}_i$, because $\sum_k p_{kj} N_k = \tilde N_j$. For a nonnegative matrix and any positive vector $x$, the spectral radius lies between the smallest and the largest of the ratios $(Mx)_i/x_i$ (Horn & Johnson, 2013). With $x = N$ the ratios are the $\mathcal{R}_i$, and $\rho(M) = \mathcal{R}_0^2$. □

**Remark 1 (A test every barangay can run).** If the residents of every barangay meet, on average over their day, fewer mosquitoes than the threshold density $1/\kappa$, dengue cannot take hold anywhere; if all of them meet more, it surely can. The bounds need no eigenvalue: each barangay needs only its own row of $P$ and the densities of the places it visits.

**Proposition 5 (Averages understate the risk).** With $V = \sum_j V_j$ and $N = \sum_i N_i$,

$$\mathcal{R}_0^2 \;\ge\; \kappa\, \frac{V}{N}$$

EQNUM:(16)

::: {custom-style="Source Line"}
Source: this study, the place analogue of Dye and Hasibeder (1986)
:::

the Ross-Macdonald number of a province in which mosquitoes and people were spread evenly.

*Proof.* Take $x$ with entries $\sqrt{N_i}$ in the Rayleigh quotient of Proposition 1. Then $Q^{\top} x = P^{\top} N = \tilde N$, so $x^{\top} S x = \kappa \sum_j w_j \tilde N_j^2 = \kappa \sum_j V_j$ and $x^{\top} x = N$. The largest eigenvalue is at least this quotient. □

**Remark 2 (Why a provincial average is not enough).** A province can look safe on average while transmission persists in a few places. Proposition 5 says the error always runs in one direction: averaging never overstates the danger.

**Proposition 6 (Place shares add up and measure the effect of control).** (i) The shares of Definition 8 are nonnegative and add up to one. (ii) If the largest eigenvalue of $S(u)$ is simple, with unit eigenvector $v$, then

$$\frac{\partial\, \mathcal{R}_0^2(u)}{\partial u_j} = -\,\kappa\, w_j\, (q_j^{\top} v)^2 \;\le\; 0$$

EQNUM:(17)

::: {custom-style="Source Line"}
Source: this study, by the derivative of a simple eigenvalue (Overton, 1988)
:::

so at $u = 0$ the reduction in $\mathcal{R}_0^2$ per unit of control at $j$ is $s_j \mathcal{R}_0^2$, and per team-day it is the hotspot score $H_j$.

*Proof.* (i) $\mathcal{R}_0^2 = v^{\top} S v = \sum_j \kappa w_j (q_j^{\top} v)^2$ by Equation (13), so the terms divided by $\mathcal{R}_0^2$ add up to one, and each is a square times a positive number. (ii) Under control, $S(u) = \kappa \sum_j (1-u_j) w_j q_j q_j^{\top}$, so $\partial S/\partial u_j = -\kappa w_j q_j q_j^{\top}$. A simple eigenvalue is differentiable with derivative $v^{\top} (\partial S) v$ (Overton, 1988). □

**Proposition 7 (Least-cost control is a convex program).** $\mathcal{R}_0^2(u)$ is a convex function of $u$ that never increases when any $u_j$ increases. The set of plans that meet the target, $\{u : r^2 I - S(u) \succeq 0,\ 0 \le u \le \bar u\}$, is convex, and program (9) is a semidefinite program.

*Proof.* $S(u)$ is an affine function of $u$, and $\lambda_{\max}(X) = \max_{\|x\|=1} x^{\top} X x$ is a maximum of linear functions of $X$, hence convex; a convex function of an affine map is convex (Boyd & Vandenberghe, 2004). Raising $u_j$ subtracts the positive semidefinite matrix $\kappa w_j q_j q_j^{\top}$ times the increase, which cannot raise any Rayleigh quotient. Finally, $\lambda_{\max}(S(u)) \le r^2$ exactly when $r^2 I - S(u)$ is positive semidefinite, a linear matrix inequality (Vandenberghe & Boyd, 1996). □

**Proposition 8 (The certificate plan is always safe).** Every plan that satisfies the linear constraints of program (10) meets the target: $\mathcal{R}_0(u) \le r$.

*Proof.* Control changes $V_j$ to $(1-u_j)V_j$ but leaves the daytime populations $\tilde N_j$ unchanged, so Proposition 4 applies to the controlled network with $\mathcal{R}_i(u) = \kappa \sum_j p_{ij} m_j (1-u_j)$. If every $\mathcal{R}_i(u) \le r^2$, then $\mathcal{R}_0^2(u) \le \max_i \mathcal{R}_i(u) \le r^2$. □

**Remark 3 (Fast and safe, or exact).** Program (10) never yields a plan that falls short of the target, but it may spend more than necessary, because the upper bound of Proposition 4 is not always tight. Section 3.3 measures that premium.

**Proposition 9 (A certified interval for the least cost).** For every symmetric positive semidefinite matrix $Z$,

$$g(Z) = \sum_j \bar u_j \min\big\{0,\; c_j - \kappa\, w_j\, q_j^{\top} Z q_j \big\} \;-\; \mathrm{tr}\big(Z\,(r^2 I - S(0))\big)$$

EQNUM:(18)

::: {custom-style="Source Line"}
Source: this study, by Lagrangian duality for semidefinite programs (Vandenberghe & Boyd, 1996)
:::

is a lower bound on the optimal cost of program (9). Algorithm 1 therefore returns a feasible plan whose cost exceeds the optimum by at most the reported gap.

*Proof.* Let $u$ satisfy the constraints of (9). The trace of the product of two positive semidefinite matrices is nonnegative, so $\mathrm{tr}(Z(r^2 I - S(u))) \ge 0$ and $\sum_j c_j u_j \ge \sum_j c_j u_j - \mathrm{tr}(Z(r^2 I - S(u)))$. Because $r^2 I - S(u) = r^2 I - S(0) + \sum_j u_j \kappa w_j q_j q_j^{\top}$, the right side equals $\sum_j u_j (c_j - \kappa w_j q_j^{\top} Z q_j) - \mathrm{tr}(Z(r^2 I - S(0)))$, a linear function of $u$ whose minimum over the box $0 \le u \le \bar u$ is $g(Z)$. The bound holds for every feasible $u$, hence for the optimum. Algorithm 1 accepts only points at which the Cholesky factorization of $r^2 I - S(u)$ succeeds, so its plan is feasible and its cost is an upper bound. The barrier method converges to the optimum as $t$ grows (Boyd & Vandenberghe, 2004). □

**Proposition 10 (The season scales the reproduction number).** For a season factor $\varsigma$, $\mathcal{R}_0^2(u;\varsigma) = \varsigma\, \mathcal{R}_0^2(u; 1)$. Without control, dengue can take hold exactly when $\varsigma > 1/\mathcal{R}_0^2(0;1)$, and the least cost of reaching a target never decreases as $\varsigma$ grows.

*Proof.* Scaling every $V_j$ by $\varsigma$ scales $W$, and therefore $S(u)$ and its largest eigenvalue, by $\varsigma$, while $\tilde N_j$ stays the same. If $\varsigma' \ge \varsigma$, every plan that meets the target in season $\varsigma'$ meets it in season $\varsigma$, so the cheapest plan for $\varsigma'$ costs at least as much. □

**Proposition 11 (Infections can be traced to their places).** If every barangay's residents spend more than half of the biting hours at home ($p_{ii} > 1/2$), then $P$ is invertible, the rates by residence determine the pressures by place, and errors $\varepsilon$ in the rates move the recovered pressures by at most

$$\| \hat z - z \|_{\infty} \;\le\; \frac{\|\varepsilon\|_{\infty}}{\min_i \,(2 p_{ii} - 1)}$$

EQNUM:(19)

::: {custom-style="Source Line"}
Source: this study, by the bound of Varah (1975)
:::

*Proof.* Each row of $P$ sums to one, so $p_{ii} - \sum_{j \neq i} p_{ij} = 2p_{ii} - 1 > 0$: $P$ is strictly diagonally dominant and therefore invertible (Horn & Johnson, 2013). For such matrices Varah (1975) proved $\|P^{-1}\|_{\infty} \le 1/\min_i (|p_{ii}| - \sum_{j\neq i} |p_{ij}|)$. Since $\hat z - z = P^{-1}\varepsilon$, the bound follows. □

**Remark 4 (What the condition means).** In the worked example residents spend 20 to 40 percent of the biting hours away from home, so the factor in Equation (19) is at most 5: an error of one case per thousand residents in the reported rates moves an inferred pressure by at most five per thousand.

**Proposition 12 (Guarantees of the CUSUM alarm).** (i) Higher counts never delay the alarm: if $x_t \le x'_t$ for all $t$, then $S_t \le S'_t$ for all $t$. (ii) If from week $\tau$ on every count exceeds the reference value by at least $\delta > 0$, the alarm sounds no later than week

$$\tau + \lceil h/\delta \rceil - 1$$

EQNUM:(20)

::: {custom-style="Source Line"}
Source: this study (Proposition 12)
:::

(iii) If $k$ and $h$ are whole numbers and the weekly counts are independent Poisson variables with mean $\mu$, the average run length to an alarm is exactly $\big((I - Q)^{-1}\mathbf{1}\big)_0$, where $Q$ is the matrix of transitions among the states $0, \dots, h-1$, with $Q_{i0} = \Pr(X \le k - i)$ and $Q_{ij} = \Pr(X = j - i + k)$ for $j \ge 1$ (Brook & Evans, 1972).

*Proof.* (i) The map $(s, x) \mapsto \max\{0, s + x - k\}$ never decreases in either argument, and both sequences start at zero, so the claim follows by induction on $t$. (ii) From week $\tau$ on, $S_t \ge S_{t-1} + x_t - k_t \ge S_{t-1} + \delta$, so $S_{\tau + j - 1} \ge j\delta$, which reaches $h$ when $j = \lceil h/\delta \rceil$. (iii) With whole-number increments the statistic moves among whole numbers and depends only on its last value and the new count, so it is a Markov chain on $\{0, \dots, h-1\}$ with the alarm as an absorbing state; the expected number of steps to absorption from state 0 is the first entry of $(I - Q)^{-1}\mathbf{1}$. □

**Remark 5 (Reading the alarm).** Part (ii) turns a design choice into a promise: with $h$ = 12.75 and weekly counts at least two above the reference value, the alarm needs at most 7 weeks. Part (iii) prices the promise in false alarms before any season begins.

## 3.3 Software Verification

Every proven property was tested on random synthetic instances against code written separately from the model (Table 7). Instances had 2 to 20 barangays scattered over a 20-by-20-kilometer square, 500 to 8,000 residents each, 10 to 45 percent of the day away from home, and between 0.5 and 4 mosquitoes per resident; parameters were drawn at random around the values of Table 4.

::: {custom-style="Paper Caption"}
**Table 7.** Checks on the model, produced by `verify_dengue.py` against independent reference computations.
:::

| Property | How it was checked | Result |
|:----------------|:------------------------------|:-------------------------|
| Reproduction number (Prop. 1) | 300 instances (2 to 12 barangays, random parameters); Equation (5) against the spectral radius of a next-generation matrix built from finite-difference Jacobians of Equation (4) | Largest relative difference $5.3 \times 10^{-15}$ |
| Threshold (Prop. 2) | 300 instances rescaled to $\mathcal{R}_0$ between 0.7 and 1.3: sign of $\mathcal{R}_0 - 1$ against the largest real part of the eigenvalues of the linearized system; 40 two-year simulations with $\mathcal{R}_0$ = 0.8 or 1.25 | Agreement in 300 of 300; outbreak exactly when $\mathcal{R}_0 > 1$ in 40 of 40 simulations |
| Bounds (Props. 4, 5) | 500 instances with 2 to 20 barangays | No violation of either bound; ratio of $\mathcal{R}_0^2$ to its province-average value: mean 1.305, largest 2.846; network value above every isolated barangay in 5 instances |
| Shares and gradient (Prop. 6) | 300 instances with a simple largest eigenvalue and random control | Shares add to one within $2.0 \times 10^{-15}$; gradient against central differences within $1.8 \times 10^{-9}$ (relative) |
| Convexity and monotonicity (Prop. 7) | 6,000 random pairs of plans | No violation of midpoint convexity or monotonicity |
| Least-cost control (Props. 8, 9) | 40 two-barangay instances against an 801-by-801 grid; 80 instances with 3 to 8 barangays against a general nonlinear solver (SLSQP) from 12 random starts | Consistent with the grid in 40 of 40 and with SLSQP in 80 of 80; largest certified gap $9.9 \times 10^{-8}$; certificate plan never missed the target; its extra cost averaged 14.5 percent (largest 98.5) |
| Inversion (Prop. 11) | 300 noise-free instances; the same with random errors; 400 instances with about 320 Poisson-distributed cases | Exact recovery within $8.0 \times 10^{-16}$; Varah bound never exceeded; inferred shares closer to the truth than shares by residence in 373 of 400 (mean total variation 0.078 against 0.181) |
| Alarm (Prop. 12) | Average run length by Equation (iii) against 20,000 simulated runs for six designs; 10,000 sequences for the delay bound and for monotonicity | All six within the 95% interval of the simulation; no violation of the delay bound or of monotonicity |
| Solutions of Equation (4) (Prop. 3) | 30 one-year simulations; fourth-order Runge-Kutta with steps 0.8 to 0.1 days | Smallest state value 0; populations kept within $3.9 \times 10^{-15}$; observed order of accuracy 3.97 (theory: 4) |

The least-cost row deserves a comment. The general solver started from twelve points and returned plans no cheaper than the certified upper bound; in the two-barangay cases the grid, which cannot miss the region of the optimum, found no plan below the certified lower bound. The certificate row shows the price of speed: a quick linear program that is always safe but costs on average 14.5 percent more.

## 3.4 Computational Cost

::: {custom-style="Paper Caption"}
**Table 8.** Time per computation in plain Python with NumPy and SciPy (target $\mathcal{R}_0 = 0.95$ from $\mathcal{R}_0 = 1.5$).
:::

| Barangays | Reproduction number (s) | Place shares (s) | Certificate plan (s) | Least-cost plan (s) | Newton steps | Certified gap |
|-------:|----------:|--------:|---------:|---------:|-------:|--------:|
| 50 | 0.0002 | 0.0008 | 0.0048 | 0.156 | 283 | $7.9 \times 10^{-7}$ |
| 100 | 0.0008 | 0.0016 | 0.012 | 1.039 | 373 | $8.7 \times 10^{-7}$ |
| 200 | 0.0037 | 0.035 | 0.112 | 4.503 | 402 | $9.1 \times 10^{-7}$ |
| 400 | 0.042 | 0.022 | 0.244 | 17.2 | 414 | $9.3 \times 10^{-7}$ |
| 720 | 0.034 | 0.162 | 0.983 | 75.5 | 484 | $9.7 \times 10^{-7}$ |

The reproduction number and the shares for all 720 barangays of Albay take a fraction of a second. The exact least-cost plan for the whole province, with its certificate of optimality, takes about a minute; the safe certificate plan takes about one second.

## 3.5 Worked Instance D1

Instance D1 is a synthetic town of six barangays (Table 9, Figure 2). B1, the poblacion, holds the central school and the public market; B2 is a dense residential barangay; B3 lies at the edge of the center; B4 and B5 are farming barangays; and B6 is on the coast. Every number in this section belongs to this test network.

::: {custom-style="Paper Caption"}
**Table 9.** Barangays of the test network D1 (synthetic).
:::

| Barangay | Description | Residents | Households | Mosquitoes per resident | Attraction | Share of day away | Cost of full control (team-days) |
|:---------|:------------|---------:|----------:|-----------:|---------:|-------:|--------:|
| B1 | Poblacion: central school and public market | 4,000 | 976 | 5.3 | 10.0 | 0.20 | 19.52 |
| B2 | Urban residential | 6,000 | 1,463 | 1.6 | 2.0 | 0.40 | 29.26 |
| B3 | Peri-urban | 3,500 | 854 | 2.0 | 1.5 | 0.35 | 17.08 |
| B4 | Rural upland | 2,000 | 488 | 2.3 | 0.5 | 0.25 | 9.76 |
| B5 | Rural lowland (rice fields) | 1,800 | 439 | 1.8 | 0.5 | 0.30 | 8.78 |
| B6 | Coastal | 2,500 | 610 | 1.4 | 1.0 | 0.30 | 12.20 |

::: {custom-style="Figure Para"}
![](/home/user/MAP---A/research/where-people-go-dengue/paper/../code/figures/fig_d1_network.png){width=5.4in}
:::

::: {custom-style="Figure Caption"}
**Figure 2.** Test network D1. Circle size shows residents, color shows mosquitoes per person present, and arrows show the daily flows of residents between barangays (synthetic).
:::

::: {custom-style="Paper Caption"}
**Table 10.** Residence-time matrix $P$ of D1: the share of biting hours that residents of the row barangay spend in the column barangay (synthetic).
:::

| From \\ To | B1 | B2 | B3 | B4 | B5 | B6 |
|:--|---:|---:|---:|---:|---:|---:|
| B1 | 0.800 | 0.101 | 0.055 | 0.008 | 0.013 | 0.024 |
| B2 | 0.328 | 0.600 | 0.044 | 0.007 | 0.006 | 0.015 |
| B3 | 0.254 | 0.062 | 0.650 | 0.007 | 0.006 | 0.021 |
| B4 | 0.162 | 0.044 | 0.032 | 0.750 | 0.003 | 0.009 |
| B5 | 0.225 | 0.033 | 0.021 | 0.003 | 0.700 | 0.017 |
| B6 | 0.207 | 0.040 | 0.040 | 0.004 | 0.009 | 0.700 |

### 3.5.1 How Much Transmission Each Place Carries

::: {custom-style="Paper Caption"}
**Table 11.** Transmission quantities of D1 (synthetic).
:::

| Barangay | People present by day | Mosquitoes per person present | Local exposure number $\mathcal{R}_i$ | $\mathcal{R}_0$ if isolated | Share of cases by residence (%) | Share of transmission by place (%) | Hotspot score per team-day ($\times 10^{-3}$) |
|:--------|-------:|--------:|-------:|------:|-------:|----------:|--------:|
| B1 | 7,300 | 2.90 | 1.613 | 1.759 | 22.4 | 42.6 | 32.1 |
| B2 | 4,469 | 2.15 | 1.404 | 0.967 | 28.5 | 17.1 | 8.6 |
| B3 | 2,962 | 2.36 | 1.446 | 1.081 | 17.2 | 12.9 | 11.1 |
| B4 | 1,617 | 2.84 | 1.632 | 1.159 | 15.0 | 18.6 | 28.1 |
| B5 | 1,394 | 2.32 | 1.425 | 1.025 | 8.4 | 5.4 | 9.0 |
| B6 | 2,057 | 1.70 | 1.171 | 0.904 | 8.4 | 3.5 | 4.2 |

The network reproduction number is 1.214, so dengue can spread in D1. The local exposure numbers run from 1.171 to 1.632, and $\mathcal{R}_0^2$ = 1.474 lies between them, as Proposition 4 requires. Spreading the same mosquitoes evenly over the same people would give 1.204, a slight underestimate (Proposition 5).

The two percentage columns tell different stories. Ranked by where cases live, B2 comes first with 28.5 percent of cases, because it has the most residents. Ranked by where transmission happens, B1 comes first with 42.6 percent: its school and market gather people from every other barangay into the place with the most mosquitoes. Figure 3 shows the gap. A brigade sent to the barangay with the most cases would start in the wrong place.

::: {custom-style="Figure Para"}
![](/home/user/MAP---A/research/where-people-go-dengue/paper/../code/figures/fig_d1_shares.png){width=5.6in}
:::

::: {custom-style="Figure Caption"}
**Figure 3.** Shares of residents, of cases by residence, and of transmission by place in D1 (synthetic).
:::

Movement matters in a second way. If nobody left home, B1 would have $\mathcal{R}_0$ = 1.759 on its own, the highest of all, because its mosquitoes would bite only its own residents. Movement dilutes those bites over more people by day, which brings the whole network to 1.214, but it also carries the infection to every barangay whose residents visit B1.

### 3.5.2 Vector Control at Least Cost

The target is $\mathcal{R}_0 \le$ 0.95, with at most 80 percent of mosquitoes removed in any place. Table 12 compares the five strategies of Section 2.10.

::: {custom-style="Paper Caption"}
**Table 12.** Five ways to reach $\mathcal{R}_0 \le$ 0.95 in D1: the reduction of mosquitoes in each barangay, the total cost, and the reproduction number reached (synthetic).
:::

| Strategy | B1 (%) | B2 (%) | B3 (%) | B4 (%) | B5 (%) | B6 (%) | Cost (team-days) | $\mathcal{R}_0$ reached |
|:----------------|-----:|-----:|-----:|-----:|-----:|-----:|-------:|-------:|
| Uniform | 38.8 | 38.8 | 38.8 | 38.8 | 38.8 | 38.8 | 37.47 | 0.950 |
| Where cases live | 46.1 | 58.7 | 35.4 | 30.9 | 17.3 | 17.4 | 38.88 | 0.950 |
| Place shares | 69.0 | 27.7 | 20.9 | 30.1 | 8.7 | 5.7 | 29.54 | 0.950 |
| Certificate (linear program) | 80.0 | 5.0 | 21.1 | 40.0 | 21.8 | 0.0 | 26.49 | 0.924 |
| Least cost (Algorithm 1) | 80.0 | 0.0 | 10.6 | 38.9 | 15.7 | 0.0 | 22.60 | 0.950 |

The least-cost plan uses 22.60 team-days, 40 percent fewer than uniform control and 42 percent fewer than control where cases live; Algorithm 1 certified that no plan can be cheaper than 22.5965. Its shape follows the hotspot scores: it removes the most mosquitoes it can at B1, works at B4 where mosquitoes are dense and cheap to reach, and leaves B2, the barangay with the most cases, untouched. Control where cases live is the most expensive of the five, because it spends heavily in B2, where few infections actually happen. The certificate plan is safe but costs 17.2 percent more than the optimum and overshoots the target, reaching 0.924.

::: {custom-style="Paper Caption"}
**Table 13.** The season factor and the least cost of reaching the target in D1 (synthetic).
:::

| Season factor $\varsigma$ | $\mathcal{R}_0$ without control | Least cost (team-days) |
|---:|---:|---:|
| 0.6 | 0.941 | 0.00 |
| 0.8 | 1.086 | 11.91 |
| 1.0 | 1.214 | 22.60 |
| 1.2 | 1.330 | 34.86 |
| 1.4 | 1.437 | 44.33 |

Table 13 applies Proposition 10. Below a season factor of 0.68, dengue cannot take hold in D1 at all. Each rise of 0.2 in the factor adds roughly ten to twelve team-days to the bill, which tells a provincial health office how much brigade time to set aside before the rains.

### 3.5.3 Where People Got Infected

Four weeks of synthetic case reports were generated from the model's own pattern of infection and passed through Algorithm 2 (Table 14).

::: {custom-style="Paper Caption"}
**Table 14.** Cases by residence and infections by place over four weeks in D1 (synthetic).
:::

| Barangay | Cases by residence | Infections by place (model truth) | Infections by place (inferred) |
|:--|---:|---:|---:|
| B1 | 76 | 138.8 | 151.0 |
| B2 | 91 | 59.1 | 55.8 |
| B3 | 53 | 43.9 | 40.0 |
| B4 | 39 | 42.7 | 32.5 |
| B5 | 24 | 19.3 | 15.5 |
| B6 | 25 | 16.2 | 13.2 |

The residence column again points to B2. The inferred column points to B1 and comes close to the true distribution, which is unknown in practice but known here because the data are synthetic. By Proposition 11 the error of the exact inverse is at most 5 times the error of the reported rates.

### 3.5.4 Early Warning

The alarm was designed for a municipality that expects between 6 and 11 cases a week, with a seasonal peak in August. With $h$ = 12.75, a normal year triggers a false alarm with probability 0.046; the single-week rule was set to the same probability (0.050, with $z$ = 3.64). In 5,000 simulated years with an outbreak beginning in week 27, the CUSUM alarm sounded on average 4.84 weeks after the start (median 5), and the single-week rule 6.52 weeks after (median 7). Neither missed an outbreak.

::: {custom-style="Figure Para"}
![](/home/user/MAP---A/research/where-people-go-dengue/paper/../code/figures/fig_cusum.png){width=5.6in}
:::

::: {custom-style="Figure Caption"}
**Figure 4.** One simulated outbreak year in D1. Top: weekly cases, the expected count, and the single-week threshold. Bottom: the CUSUM statistic and its alarm level. In this particular year the single-week rule fired in week 32 and the CUSUM in week 34; averaged over 5,000 years, the CUSUM fired earlier (synthetic).
:::

::: {custom-style="Paper Caption"}
**Table 15.** Exact average run lengths in weeks (Proposition 12) of the CUSUM and of a single-week rule set to a false-alarm rate at least as low, before and after a rise in the weekly mean.
:::

| Weekly mean | CUSUM $k$, $h$ | CUSUM, no rise | Single-week rule, no rise | CUSUM, rise of 50% | Single-week rule, rise of 50% | CUSUM, doubling | Single-week rule, doubling |
|------:|:------|-------:|-------:|-------:|-------:|-------:|-------:|
| 2 | 3, 4 | 84.9 | 220.6 | 10.7 | 29.8 | 4.2 | 9.0 |
| 2 | 3, 6 | 412.5 | 911.8 | 19.5 | 84.0 | 6.2 | 19.6 |
| 5 | 7, 6 | 181.7 | 183.4 | 7.4 | 12.6 | 2.6 | 3.3 |
| 5 | 7, 10 | 2409.8 | 4419.8 | 13.6 | 97.5 | 4.0 | 12.0 |
| 10 | 13, 10 | 633.1 | 1429.3 | 5.3 | 18.8 | 2.0 | 2.8 |
| 10 | 13, 16 | 13148.5 | 21299.5 | 8.3 | 89.6 | 2.9 | 6.4 |

Table 15 shows the reason in exact numbers. For every design, the single-week rule was given a false-alarm rate no worse than the CUSUM's, and still the CUSUM detected a rise of one half far sooner: after 13.6 weeks instead of 97.5 in the design with a mean of 5 cases and $h$ = 10. One week seldom looks unusual on its own, but a run of weeks a little above normal accumulates.

## 3.6 Planned Experiments on the Albay Instance

The next run of the model covers all 720 barangays of Albay, using the travel times of the companion study, attractions from the school and market registers, and mosquito indices from provincial surveys. The tests and decision rules that follow were set down before any result for that instance existed.

### 3.6.1 Sensitivity Analysis

Each sweep changes one input: the share of time away from home ($\pm 10$ percentage points), the decay $\beta$ (0.03, 0.06, and 0.10 per minute), the biting rate and the mosquito lifetime ($\pm 20$ percent), the limit $\bar u$ (0.6, 0.8, 0.9), the cost per household ($\pm 25$ percent), and the CUSUM design ($\theta$ = 1.3, 1.5, 2.0).

### 3.6.2 Statistical Treatment

::: {custom-style="Paper Caption"}
**Table 16.** How each question is tested.
:::

| Question | Test or estimator | Why this test |
|:-------------------|:--------------------|:--------------------|
| (T1) Does the network reproduction number exceed the provincial average? | Ratio of Equation (5) to Equation (16) with a 95% bootstrap interval over survey households (Efron & Tibshirani, 1993) | The uncertainty comes from the mosquito survey |
| (T2) Are the places of transmission different from the places of residence? | Total variation distance between inferred shares by place and shares by residence, bootstrap interval | Compares whole distributions, not single ranks |
| (T3) Is the ranking of places stable? | Spearman's rank correlation (Spearman, 1904) of place shares across the sweeps | Asks whether the order survives, not the values |
| (T4) How much does the least-cost plan save? | Paired comparison of costs across municipalities, Wilcoxon signed-rank test (Wilcoxon, 1945) | Paired and skewed |
| (T5) Does the CUSUM warn earlier? | Retrospective alarm weeks on 2026 municipal counts against the single-week rule at equal false-alarm rates; sign test | Each municipality gives one paired outcome |

### 3.6.3 Hypotheses Fixed in Advance

* **H1.** Albay's network reproduction number is at least 10 percent higher than its provincial-average value; this holds if the whole bootstrap interval of the ratio sits above 1.10.
* **H2.** In more than half of the municipalities with ten or more barangays, the barangay with the largest share of transmission hosts a central school or a public market.
* **H3.** In at least half of the municipalities, the barangay with the most reported cases is not the barangay with the most inferred infections.
* **H4.** The least-cost plan costs at least 25 percent less than uniform control at the same target in a majority of municipalities.
* **H5.** The certificate plan costs at most 30 percent more than the least-cost plan, so that it can serve as a quick, safe plan during a surge.
* **H6.** Retrospectively on 2026 data, the CUSUM alarm sounds earlier than the single-week rule in at least 12 of the 18 municipalities.
* **H7.** The ranking of places by share is stable across the sweeps (Spearman's $\rho$ above 0.8).
* **H8.** Propositions 7 and 10 make monotonicity exact; any computed violation will be treated as a data error and the inputs checked.

### 3.6.4 Sensitivity Sweeps

Each sweep of Section 3.6.1 recomputes the reproduction number, the place shares, the five strategies, and the alarm weeks. The results will be reported with the hypotheses above.


# 4. CONCLUSIONS

## 4.1 Summary of the Findings

The central question was whether a health office could see where dengue is transmitted, decide how much control is enough and where to put it, and know when an outbreak has begun, using only open data and a laptop. The answer is yes for the mathematics: each of these tasks became a precise problem with a proven solution, and each proof survived a check against code written separately from the model. Whether the answer is also yes for Albay depends on the field data that the open-data instance will supply.

**Objective 1: the residence-time network.** Definitions 1 to 4 turned barangay populations, travel times, the pull of schools, markets, and workplaces, and mosquito indices into a matrix $P$ of biting hours. Every row of $P$ sums to one, and every entry has a public source or a declared value.

**Objective 2: the reproduction number and its bounds.** Proposition 1 wrote $\mathcal{R}_0^2$ as the largest eigenvalue of a symmetric positive semidefinite matrix, and Proposition 2 tied its threshold to the growth of infection. The formula matched a numerical next-generation matrix to within $5.3 \times 10^{-15}$ in 300 random networks. Propositions 4 and 5 then trapped $\mathcal{R}_0^2$ between the smallest and largest local exposure numbers and showed that the provincial average can only understate it; no violation appeared in 500 instances.

**Objective 3: ranking places.** Proposition 6 split $\mathcal{R}_0^2$ into place shares that add to one and showed that each share is, up to a known factor, the rate at which control at that place lowers $\mathcal{R}_0^2$. Shares and gradients agreed with finite differences in all 300 checks.

**Objective 4: least-cost control.** Because $\mathcal{R}_0^2$ is convex and never increasing in the control intensities (Proposition 7), the cheapest plan that meets a target is a convex program. Algorithm 1 solved it with a certified gap; a fine grid and a general nonlinear solver never found a cheaper feasible plan in 120 cases. The linear-program certificate of Proposition 9 always met the target and cost on average 14.5 percent more.

**Objective 5: infections traced to places.** When residents spend more than half of their biting hours at home, the residence-time matrix can be inverted, and Proposition 11 bounds the error of the inverse. In noisy synthetic data, the inferred distribution of infections was closer to the truth than the distribution of cases by residence in 373 of 400 instances.

**Objective 6: the outbreak alarm.** Proposition 12 gave the CUSUM alarm a worst-case delay and an exact average run length. The Markov-chain values fell inside the 95 percent interval of 20,000 simulated runs in every design.

**Objective 7: verification.** All twelve propositions were checked numerically against independent code, and Table 7 records no failure. On 720 barangays, the size of Albay, the reproduction number and the place shares take under a second, and the certified least-cost plan about a minute.

**Objective 8: the worked instance.** In the six-barangay test network D1, case addresses pointed to the residential barangay B2, while 42.6 percent of transmission happened in the poblacion B1 with its school and market. The least-cost plan reached $\mathcal{R}_0 \le$ 0.95 with 22.60 team-days, 40 percent below uniform control and 42 percent below control where cases live. At the same false-alarm rate, the CUSUM alarm sounded 1.7 weeks earlier on average than a single-week threshold. The eight hypotheses of Section 3.6.3 were recorded before any Albay result existed.

## 4.2 Limitations

* **(L1) The worked numbers are synthetic.** D1 is a made-up town. Its tables show that the pipeline behaves as the propositions say; they are not estimates for Legazpi, Daraga, or any real barangay.
* **(L2) Routines are fixed.** The matrix $P$ describes an average weekday. Weekends, fiestas, class suspensions, and the habit of staying home when sick all change it. School closures can be studied by recomputing $P$, but the model does not predict how people will change their routines.
* **(L3) Mosquito numbers are hard to measure.** Larval and ovitrap indices are rough proxies for adult female mosquitoes, and the conversion between them varies by place and season. The rankings depend on relative densities, which are more reliable than absolute ones, but the reproduction number itself carries the error of the survey.
* **(L4) One virus, no immunity history.** Four serotypes circulate in the Philippines, and past infections change who can be infected again. The model treats dengue as one infection in a fully susceptible population, so its reproduction number describes potential, not the course of a particular season.
* **(L5) Constant parameters.** Biting rate, incubation period, and mosquito lifetime change with temperature (Mordecai et al., 2017). The season factor scales mosquito numbers only; it does not change the other parameters within a season.
* **(L6) Control acts on numbers only.** Each method is reduced to a fraction of mosquitoes removed at a cost proportional to that fraction. Real methods differ in how long they last, how quickly mosquitoes return, and how much they cost to repeat.
* **(L7) Reporting is assumed uniform.** Assumption 5 treats reported cases as the same fraction of infections everywhere. If people in remote barangays consult less often, the inversion will understate infections there.
* **(L8) Time away above one half.** The error bound of Proposition 11 needs every barangay to keep its residents home for more than half of the biting hours. A barangay whose residents mostly commute out would weaken the bound, though the nonnegative least-squares inverse still applies.
* **(L9) A barangay is not a household.** Transmission happens between houses a few dozen meters apart (Stoddard et al., 2013). The model works at the barangay level, which matches the reporting and the brigades but averages over finer differences.
* **(L10) The alarm assumes Poisson counts.** Weekly counts that cluster more than a Poisson variable would sound false alarms more often than computed. Once past seasons are on file, the design can be tuned to them.

## 4.3 Recommendations and Next Steps

**Build the Albay instance.** The next step is the full network: the 720 barangays with their census populations, travel times from the companion study (Brimbuela et al., 2026), attraction from the DepEd masterlist and the market and business registers of each local government, and mosquito indices from the entomological surveys of the provincial and regional health offices. The hypotheses of Section 3.6.3 should then be tested exactly as written.

**Ask about daily movement.** A short school-based questionnaire on where students and their families spend the daylight hours would give a direct estimate of $P$ for a sample of barangays and test the destination-choice rule of Definition 2. Mobile phone data, where a provider releases them in aggregate form, could serve the same purpose.

**Record where cases were during the day.** The case investigation form already asks for the address. One more line, the barangay where the patient spent most daytime hours in the two weeks before illness, would allow Proposition 11 to be tested against direct reports.

**Let the parameters follow the weather.** Making the biting rate and the mosquito lifetime functions of temperature, after Mordecai et al. (2017), and linking the season factor to rainfall would turn the season scaling of Table 13 into a forecast of the control effort needed a few weeks ahead.

**Pilot the brigade allocation.** One municipality could allocate its dengue brigades for a season by the least-cost plan while a comparable municipality keeps its usual practice, with weekly case counts and ovitrap indices compared afterward. Such a trial needs the approval of the provincial health office and an ethics review.

**Challenges.** Mosquito surveys are labor-intensive and seldom cover every barangay; case data are released by municipality rather than by barangay during most of the year; and a planning tool is useful only if the people who allocate brigades trust it. Each output of the model therefore comes with the assumptions it rests on and a plain-language explanation.

## 4.4 Applications

**For households and schools.** A family can see whether its barangay or the places its members visit by day rank high in the share of transmission, and a school head can see whether the school campus is among the places that carry the most transmission, which tells the school when its own cleanup days matter most.

**For barangay health workers and dengue brigades.** The ranking per team-day tells a brigade leader where one more day of cleanup lowers transmission the most, and the least-cost plan turns a target into a schedule of team-days per barangay.

**For provincial and municipal health offices.** The office can compute the network reproduction number each month, check whether the province average hides places of high risk, convert reported cases into infections by place, and run the CUSUM alarm on weekly counts with a false-alarm rate it chose in advance. The certificate plan gives a quick, always-safe allocation during a surge, and the exact plan says how much cheaper a careful allocation can be.

**For planners.** Table 13 shows how many team-days a stronger rainy season will need, which helps the province budget brigade time and supplies before the rains rather than after the cases rise.

**Relation to the SDGs.** These uses serve target 3.3 by targeting control, target 3.d by giving an early warning with known error rates, and target 4.a by helping keep schools safe places to learn. They remain intended uses until the model is tested in the field.

**Beyond Albay.** The inputs are a census, travel times, a list of schools and markets, and mosquito surveys. Any Philippine province, or any place with *Aedes*-borne diseases such as chikungunya and Zika, could build the same model, since the mathematics does not depend on the virus.

# 5. REFERENCES

::: {custom-style="Reference"}
Bhatt, S., Gething, P. W., Brady, O. J., Messina, J. P., Farlow, A. W., Moyes, C. L., Drake, J. M., Brownstein, J. S., Hoen, A. G., Sankoh, O., Myers, M. F., George, D. B., Jaenisch, T., Wint, G. R. W., Simmons, C. P., Scott, T. W., Farrar, J. J., & Hay, S. I. (2013). The global distribution and burden of dengue. *Nature, 496*(7446), 504–507. https://doi.org/10.1038/nature12060
:::

::: {custom-style="Reference"}
Bowman, L. R., Donegan, S., & McCall, P. J. (2016). Is dengue vector control deficient in effectiveness or evidence?: Systematic review and meta-analysis. *PLOS Neglected Tropical Diseases, 10*(3), e0004551. https://doi.org/10.1371/journal.pntd.0004551
:::

::: {custom-style="Reference"}
Boyd, S., & Vandenberghe, L. (2004). *Convex optimization*. Cambridge University Press.
:::

::: {custom-style="Reference"}
Brimbuela, P. J. A., De Asis, D. J. Ll., & Shin, Y. (2026). *Right hospital, right bed, right time: A verified network model for mapping hospitals and routing patients in Albay by clinical need, live bed availability, and ability to pay* [Unpublished research paper]. Legazpi City Science High School.
:::

::: {custom-style="Reference"}
Brook, D., & Evans, D. A. (1972). An approach to the probability distribution of CUSUM run length. *Biometrika, 59*(3), 539–549. https://doi.org/10.1093/biomet/59.3.539
:::

::: {custom-style="Reference"}
Cosner, C., Beier, J. C., Cantrell, R. S., Impoinvil, D., Kapitanski, L., Potts, M. D., Troyo, A., & Ruan, S. (2009). The effects of human movement on the persistence of vector-borne diseases. *Journal of Theoretical Biology, 258*(4), 550–560. https://doi.org/10.1016/j.jtbi.2009.02.016
:::

::: {custom-style="Reference"}
Daily Tribune. (2026a, September 11). *Albay declares state of calamity as dengue cases surge*. https://tribune.net.ph/2026/09/11/albay-declares-state-of-calamity-as-dengue-cases-surge
:::

::: {custom-style="Reference"}
Daily Tribune. (2026b, September 18). *Albay dengue cases surpass 2,000, 14 deaths recorded*. https://tribune.net.ph/2026/09/18/albay-dengue-cases-surpass-2000-14-deaths-recorded
:::

::: {custom-style="Reference"}
Daily Tribune. (2026c, September 21). *Dengue cases in Albay now at 2,888*. https://tribune.net.ph/2026/09/21/dengue-cases-in-albay-now-at-2888
:::

::: {custom-style="Reference"}
Daily Tribune. (2026d, October 13). *Dengue cases continue to decline — DOH*. https://tribune.net.ph/2026/10/13/dengue-cases-continue-to-decline-doh
:::

::: {custom-style="Reference"}
Department of Education. (2021). *Masterlist of schools SY 2020–2021 based on LIS, as of January 15, 2021* [Data set].
:::

::: {custom-style="Reference"}
Diekmann, O., Heesterbeek, J. A. P., & Metz, J. A. J. (1990). On the definition and the computation of the basic reproduction ratio *R*~0~ in models for infectious diseases in heterogeneous populations. *Journal of Mathematical Biology, 28*(4), 365–382. https://doi.org/10.1007/BF00178324
:::

::: {custom-style="Reference"}
Dye, C., & Hasibeder, G. (1986). Population dynamics of mosquito-borne disease: Effects of flies which bite some people more frequently than others. *Transactions of the Royal Society of Tropical Medicine and Hygiene, 80*(1), 69–77. https://doi.org/10.1016/0035-9203(86)90199-9
:::

::: {custom-style="Reference"}
Edillo, F. E., Halasa, Y. A., Largo, F. M., Erasmo, J. N. V., Amoin, N. B., Alera, M. T. P., Yoon, I.-K., Alcantara, A. C., & Shepard, D. S. (2015). Economic cost and burden of dengue in the Philippines. *The American Journal of Tropical Medicine and Hygiene, 92*(2), 360–366. https://doi.org/10.4269/ajtmh.14-0139
:::

::: {custom-style="Reference"}
Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall.
:::

::: {custom-style="Reference"}
Esu, E., Lenhart, A., Smith, L., & Horstick, O. (2010). Effectiveness of peridomestic space spraying with insecticide on dengue transmission: Systematic review. *Tropical Medicine & International Health, 15*(5), 619–631. https://doi.org/10.1111/j.1365-3156.2010.02489.x
:::

::: {custom-style="Reference"}
Horn, R. A., & Johnson, C. R. (2013). *Matrix analysis* (2nd ed.). Cambridge University Press.
:::

::: {custom-style="Reference"}
Hussain-Alkhateeb, L., Kroeger, A., Olliaro, P., Rocklöv, J., Sewe, M. O., Tejeda, G., Benitez, D., Gill, B., Hakim, S. L., Gomes Carvalho, R., Bowman, L., & Petzold, M. (2018). Early warning and response system (EWARS) for dengue outbreaks: Recent advancements towards widespread applications in critical settings. *PLOS ONE, 13*(5), e0196811. https://doi.org/10.1371/journal.pone.0196811
:::

::: {custom-style="Reference"}
Lawson, C. L., & Hanson, R. J. (1974). *Solving least squares problems*. Prentice-Hall.
:::

::: {custom-style="Reference"}
Lucas, J. M. (1985). Counted data CUSUM's. *Technometrics, 27*(2), 129–144. https://doi.org/10.1080/00401706.1985.10488030
:::

::: {custom-style="Reference"}
Mordecai, E. A., Cohen, J. M., Evans, M. V., Gudapati, P., Johnson, L. R., Lippi, C. A., Miazgowicz, K., Murdock, C. C., Rohr, J. R., Ryan, S. J., Savage, V., Shocket, M. S., Stewart Ibarra, A., Thomas, M. B., & Weikel, D. P. (2017). Detecting the impact of temperature on transmission of Zika, dengue, and chikungunya using mechanistic models. *PLOS Neglected Tropical Diseases, 11*(4), e0005568. https://doi.org/10.1371/journal.pntd.0005568
:::

::: {custom-style="Reference"}
OpenStreetMap contributors. (2026). *OpenStreetMap* [Data set]. OpenStreetMap Foundation. https://www.openstreetmap.org
:::

::: {custom-style="Reference"}
Overton, M. L. (1988). On minimizing the maximum eigenvalue of a symmetric matrix. *SIAM Journal on Matrix Analysis and Applications, 9*(2), 256–268. https://doi.org/10.1137/0609021
:::

::: {custom-style="Reference"}
Page, E. S. (1954). Continuous inspection schemes. *Biometrika, 41*(1–2), 100–115. https://doi.org/10.1093/biomet/41.1-2.100
:::

::: {custom-style="Reference"}
Philippine Information Agency. (n.d.). [Department of Health 4S strategy against dengue]. https://pia.gov.ph/?p=74463
:::

::: {custom-style="Reference"}
Philippine Statistics Authority. (2021). *The 2020 Census of Population and Housing (2020 CPH) population counts declared official by the President* [Press release]. https://psa.gov.ph/content/2020-census-population-and-housing-2020-cph-population-counts-declared-official-president
:::

::: {custom-style="Reference"}
Republic Act No. 10173. (2012). *Data Privacy Act of 2012*. Congress of the Philippines.
:::

::: {custom-style="Reference"}
Republic Act No. 11332. (2019). *Mandatory Reporting of Notifiable Diseases and Health Events of Public Health Concern Act*. Congress of the Philippines.
:::

::: {custom-style="Reference"}
Smith, D. L., Battle, K. E., Hay, S. I., Barker, C. M., Scott, T. W., & McKenzie, F. E. (2012). Ross, Macdonald, and a theory for the dynamics and control of mosquito-transmitted pathogens. *PLOS Pathogens, 8*(4), e1002588. https://doi.org/10.1371/journal.ppat.1002588
:::

::: {custom-style="Reference"}
Spearman, C. (1904). The proof and measurement of association between two things. *The American Journal of Psychology, 15*(1), 72–101. https://doi.org/10.2307/1412159
:::

::: {custom-style="Reference"}
Stoddard, S. T., Morrison, A. C., Vazquez-Prokopec, G. M., Paz Soldan, V., Kochel, T. J., Kitron, U., Elder, J. P., & Scott, T. W. (2009). The role of human movement in the transmission of vector-borne pathogens. *PLOS Neglected Tropical Diseases, 3*(7), e481. https://doi.org/10.1371/journal.pntd.0000481
:::

::: {custom-style="Reference"}
Stoddard, S. T., Forshey, B. M., Morrison, A. C., Paz-Soldan, V. A., Vazquez-Prokopec, G. M., Astete, H., Reiner, R. C., Jr., Vilcarromero, S., Elder, J. P., Halsey, E. S., Kochel, T. J., Kitron, U., & Scott, T. W. (2013). House-to-house human movement drives dengue virus transmission. *Proceedings of the National Academy of Sciences, 110*(3), 994–999. https://doi.org/10.1073/pnas.1213349110
:::

::: {custom-style="Reference"}
Su, G. L. S. (2008). Correlation of climatic factors and dengue incidence in Metro Manila, Philippines. *Ambio, 37*(4), 292–294. https://doi.org/10.1579/0044-7447(2008)37[292:COCFAD]2.0.CO;2
:::

::: {custom-style="Reference"}
Sumi, A., Telan, E. F. O., Chagan-Yasutan, H., Piolo, M. B., Hattori, T., & Kobayashi, N. (2017). Effect of temperature, relative humidity and rainfall on dengue fever and leptospirosis infections in Manila, the Philippines. *Epidemiology and Infection, 145*(1), 78–86. https://doi.org/10.1017/S095026881600203X
:::

::: {custom-style="Reference"}
United Nations General Assembly. (2015). *Transforming our world: The 2030 Agenda for Sustainable Development* (A/RES/70/1). United Nations. https://undocs.org/A/RES/70/1
:::

::: {custom-style="Reference"}
United Nations Office for the Coordination of Humanitarian Affairs. (2019). *Philippines: Dengue outbreak, situation report no. 4 (13 August 2019)*. ReliefWeb. https://reliefweb.int/report/philippines/philippines-situation-report-4-dengue-outbreak-13-aug-2019
:::

::: {custom-style="Reference"}
van den Driessche, P., & Watmough, J. (2002). Reproduction numbers and sub-threshold endemic equilibria for compartmental models of disease transmission. *Mathematical Biosciences, 180*(1–2), 29–48. https://doi.org/10.1016/S0025-5564(02)00108-6
:::

::: {custom-style="Reference"}
Vandenberghe, L., & Boyd, S. (1996). Semidefinite programming. *SIAM Review, 38*(1), 49–95. https://doi.org/10.1137/1038003
:::

::: {custom-style="Reference"}
Varah, J. M. (1975). A lower bound for the smallest singular value of a matrix. *Linear Algebra and Its Applications, 11*(1), 3–5. https://doi.org/10.1016/0024-3795(75)90112-3
:::

::: {custom-style="Reference"}
Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin, 1*(6), 80–83. https://doi.org/10.2307/3001968
:::

::: {custom-style="Reference"}
World Health Organization. (2012). *Global strategy for dengue prevention and control 2012–2020*. World Health Organization.
:::

# APPENDIX A. REGISTER OF PUBLIC DATA SOURCES

Table A1 names the source of each model input; the remaining inputs are design values declared in Table 4.

::: {custom-style="Paper Caption"}
**Table A1.** Where each input of the model comes from.
:::

| Input | Source | Publisher | Access |
|:-------------------|:-------------------|:--------------|:----------|
| Residents $N_i$ of each barangay | 2020 Census of Population and Housing (PSA, 2021) | Philippine Statistics Authority | Published online |
| Travel times $T_{ij}$ between barangay centers | Road and transit layer of the companion study (Brimbuela et al., 2026), built on OpenStreetMap (OpenStreetMap contributors, 2026) | Legazpi City Science High School; OpenStreetMap Foundation | Released with the project; Open Database License |
| School part of the attraction $A_j$ | Masterlist of schools with enrollment (DepEd, 2021) | Department of Education | Published online |
| Market and workplace part of $A_j$ | Public market and business permit registers | City and municipal governments | On request; public summaries |
| Mosquito indices for $V_j$ | Larval and ovitrap surveys | Provincial and regional health offices | On request |
| Weekly cases by residence | Notifiable disease surveillance under Republic Act No. 11332 (2019), released as municipal counts | Department of Health; Provincial Health Office | Public bulletins; barangay counts on request |
| Share of the day away $\omega_i$ | Declared values in this paper; a school-based questionnaire is proposed in Section 4.3 | This study | Released with the project |
| Transmission parameters | Published ranges (Mordecai et al., 2017; Smith et al., 2012) | Peer-reviewed literature | Public |

# APPENDIX B. FILES OF THE DATA SET

::: {custom-style="Paper Caption"}
**Table B1.** Files of the dengue data set.
:::

| File | Contents |
|:------------|:------------------------------------------------|
| barangays.csv | Barangay code, name, municipality, residents, households, attraction, share of the day away, mosquito index and its survey date |
| travel_times.csv | Travel time in minutes between each pair of barangay centers |
| residence_time.csv | The matrix $P$ computed from Definitions 2 and 3 |
| weekly_cases.csv | Week, municipality or barangay, cases by residence, expected count |
| plans.csv | For each strategy of Section 2.10: the reduction per barangay, its cost, and the reproduction number reached |
| results.json | Every number of Chapter 3, written by `verify_dengue.py` |

# APPENDIX C. MOSQUITO INDEX AND CASE FIELDS

**From survey to density.** A survey gives a larval or ovitrap index for some households of a barangay. The model needs mosquitoes per resident, so each index is converted by a single factor that is the same for all barangays in one season. Because the place shares, the ranking, and the shape of the least-cost plan depend only on relative densities, the factor affects the reproduction number but not the order of places.

**Inclusion rule.** A barangay enters the instance only if (1) its census population is published, (2) its center lies within 200 m of the road graph, and (3) it has a mosquito index from the current or the previous season, or else the median index of its municipality, marked as imputed.

::: {custom-style="Paper Caption"}
**Table C1.** Fields of the barangay record.
:::

| Field | Kind | Meaning |
|:------------|:--------|:--------------------------------------------|
| psgc | string | Barangay code under the Philippine Standard Geographic Code |
| name | string | Name as spelled in the census |
| residents | integer | Census population $N_i$ |
| households | integer | Households, used for the cost $c_i$ |
| schools_enrolled | integer | Learners enrolled in schools located in the barangay |
| market_stalls | integer | Stalls of public markets in the barangay |
| attraction | decimal | $A_i$, combined from the two fields above and workplaces |
| away_share | decimal | $\omega_i$, share of biting hours spent away from home |
| mosquito_index | decimal | Survey index and its type (larval or ovitrap) |
| index_date, imputed | date, boolean | Survey date; whether the municipal median was used |
| source, source_date | string, date | Register and date consulted |

# APPENDIX D. FEATURES OF THE BANTA-Y APPLICATION

BANTA-Y packages the model as a web application; the same team also made MAP-A and LIGTA-S. The SDG target that a feature serves is noted in parentheses.

**Network**

1. An editable table of barangays with residents, mosquitoes per resident, share of the day away, and attraction, with the matrix $P$ shown as a heat map.

**Transmission**

2. The network reproduction number, the local exposure numbers with the bounds of Proposition 4, and the province-average value of Proposition 5 (target 3.3).
3. A bar chart of residents, cases by residence, and transmission by place, and a ranking of places per team-day (targets 3.3 and 4.a).

**Control**

4. The five strategies of Section 2.10 side by side, with the exact plan of Algorithm 1 and its certified interval (target 3.3).
5. A season slider that rescales mosquito numbers and recomputes the plan.

**Surveillance**

6. A form that turns weekly cases by residence into infections by place with the error bound of Proposition 11.
7. The CUSUM alarm with a chosen false-alarm rate, plotted against the single-week rule (target 3.d).
8. The Department of Health 4S checklist for households and schools.

**Use without a signal**

9. All computation runs in the browser and works offline once installed; data can be exported and imported as JSON or CSV.

# APPENDIX E. RISK REGISTER

The study handles no patients and no personal records; its risks come from how a health office might use the outputs (Table E1).

::: {custom-style="Paper Caption"}
**Table E1.** Risks of misuse and how they are reduced.
:::

| Risk | Likelihood | Safeguard |
|:------------------|:---------|:----------------------------------------|
| A barangay labeled a hotspot is stigmatized | Moderate | Rankings are shared with health offices, not published as lists of "dangerous" barangays; the share measures where bites happen, not who is to blame. |
| Synthetic numbers mistaken for Albay estimates | High | Every table and figure of Section 3.5 is marked synthetic, and the application labels D1 as a test network. |
| Fogging used everywhere a plan shows effort | Moderate | The plan states a reduction in mosquitoes, not a chemical; the 4S guidance limits fogging to hotspots. |
| Old mosquito surveys drive the plan | High | Each index carries its date; imputed values are flagged; Table 13 shows how the plan changes with the season. |
| Alarm ignored after false alarms | Moderate | The false-alarm rate is chosen in advance and stated with every alarm. |
| Patient addresses exposed | Low | Only weekly counts per barangay are handled, in line with the Data Privacy Act (Republic Act No. 10173, 2012). |
| Errors in the code | Moderate | All twelve propositions were checked against independent code before any result was reported (Table 7). |

# APPENDIX F. HOW TO REPRODUCE EVERY NUMBER

The model is in `denguemodel.py`, and all checks and the worked instance are in `verify_dengue.py`, both stored in the project repository. Given the fixed seed 20261017, the script performs six steps:

1. compares Equation (5) with a numerical next-generation matrix and checks the threshold, the bounds, the shares, and the gradient (Propositions 1 to 6);
2. tests convexity and monotonicity on random pairs of plans and compares Algorithm 1 with a grid and with SLSQP (Propositions 7 to 9);
3. tests the inversion, the Varah bound, the CUSUM delay bound, and the exact average run length against simulation (Propositions 11 and 12);
4. checks positivity, conservation, and the order of the Runge-Kutta solver (Proposition 3);
5. times the computations for 50 to 720 barangays; and
6. builds D1, computes Tables 9 to 15, and draws Figures 2 to 4.

Running `python3 verify_dengue.py` writes `results.json`, from which every number in Chapter 3 is filled in. All of these numbers come from synthetic inputs.

# ETHICS STATEMENT

No person took part in this study, and no mosquito was collected. The only real-world facts used are those in published reports and public registers, each cited where it is used; every other number comes from a proof, a declared parameter, or a synthetic test network built for verification.

The protocol goes to the school's Scientific Review Committee before the model touches Albay data, and the health offices that hold case and survey records will be asked for them only as counts per barangay per week. Rankings of barangays will be returned to those offices and not published as lists. The results in this paper describe a model, not the dengue situation of any real place.

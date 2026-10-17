::: {custom-style="Figure Para"}
![](<<HEADER>>){width=2.3in}
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

 

Albay declared a state of calamity over dengue in September 2026 after reported cases rose by 84 percent over the year before. Cases are logged at the patient's home address, but the day-biting *Aedes aegypti* mosquito infects people where they spend their daylight hours, at school, at the market, and at work, so cleanup brigades and spraying are often sent to the wrong barangay. A model small enough for a laptop was built to link mosquito density in each barangay to the share of the day residents spend in every other barangay. Its reproduction number is the largest eigenvalue of a symmetric matrix, which yields four tools: bounds that flag where transmission can persist, a ranking of places by their share of transmission, a least-cost allocation of brigade team-days solved as a convex program with a certified optimality gap, and an inversion that moves case counts from homes to the places of infection. A Poisson CUSUM rule gives the outbreak alarm. Twelve propositions were proven, and each was tested on synthetic instances against independently written code; the reproduction number agreed with a numerical next-generation matrix to <<V1_ERR>> in <<V1_N>> instances, and the control solver matched a fine grid and a general nonlinear solver in all <<V6_N>> cases. On a six-barangay test network, homes pointed to a residential barangay, while <<D1_SHARE_B1>> percent of transmission took place at the town center with the school and market; the least-cost plan reached the target with <<D1_COST_EXACT>> team-days, <<D1_SAVE_UNI>> percent fewer than uniform spraying and <<D1_SAVE_RES>> percent fewer than spraying where cases live. At an equal false-alarm rate, the CUSUM rule sounded on average <<D1_CUSUM_GAIN>> weeks earlier than a single-week threshold. Open data and routine case reports therefore suffice to target dengue control by place, supporting SDG 3. A pilot with barangay dengue brigades, led by the Provincial Health Office, is recommended.

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

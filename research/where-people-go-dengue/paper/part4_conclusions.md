# 4. CONCLUSIONS

## 4.1 Summary of the Findings

The central question was whether a health office could see where dengue is transmitted, decide how much control is enough and where to put it, and know when an outbreak has begun, using only open data and a laptop. The answer is yes for the mathematics: each of these tasks became a precise problem with a proven solution, and each proof survived a check against code written separately from the model. Whether the answer is also yes for Albay depends on the field data that the open-data instance will supply.

**Objective 1: the residence-time network.** Definitions 1 to 4 turned barangay populations, travel times, the pull of schools, markets, and workplaces, and mosquito indices into a matrix $P$ of biting hours. Every row of $P$ sums to one, and every entry has a public source or a declared value.

**Objective 2: the reproduction number and its bounds.** Proposition 1 wrote $\mathcal{R}_0^2$ as the largest eigenvalue of a symmetric positive semidefinite matrix, and Proposition 2 tied its threshold to the growth of infection. The formula matched a numerical next-generation matrix to within <<V1_ERR>> in <<V1_N>> random networks. Propositions 4 and 5 then trapped $\mathcal{R}_0^2$ between the smallest and largest local exposure numbers and showed that the provincial average can only understate it; no violation appeared in <<V3_N>> instances.

**Objective 3: ranking places.** Proposition 6 split $\mathcal{R}_0^2$ into place shares that add to one and showed that each share is, up to a known factor, the rate at which control at that place lowers $\mathcal{R}_0^2$. Shares and gradients agreed with finite differences in all <<V4_N>> checks.

**Objective 4: least-cost control.** Because $\mathcal{R}_0^2$ is convex and never increasing in the control intensities (Proposition 7), the cheapest plan that meets a target is a convex program. Algorithm 1 solved it with a certified gap; a fine grid and a general nonlinear solver never found a cheaper feasible plan in <<V6_N>> cases. The linear-program certificate of Proposition 9 always met the target and cost on average <<V6_PREM>> percent more.

**Objective 5: infections traced to places.** When residents spend more than half of their biting hours at home, the residence-time matrix can be inverted, and Proposition 11 bounds the error of the inverse. In noisy synthetic data, the inferred distribution of infections was closer to the truth than the distribution of cases by residence in <<V7_CLOSER>> of <<V7_NN>> instances.

**Objective 6: the outbreak alarm.** Proposition 12 gave the CUSUM alarm a worst-case delay and an exact average run length. The Markov-chain values fell inside the 95 percent interval of 20,000 simulated runs in every design.

**Objective 7: verification.** All twelve propositions were checked numerically against independent code, and Table 7 records no failure. On 720 barangays, the size of Albay, the reproduction number and the place shares take under a second, and the certified least-cost plan about a minute.

**Objective 8: the worked instance.** In the six-barangay test network D1, case addresses pointed to the residential barangay B2, while <<D1_SHARE_B1>> percent of transmission happened in the poblacion B1 with its school and market. The least-cost plan reached $\mathcal{R}_0 \le$ <<D1_TARGET>> with <<D1_COST_EXACT>> team-days, <<D1_SAVE_UNI>> percent below uniform control and <<D1_SAVE_RES>> percent below control where cases live. At the same false-alarm rate, the CUSUM alarm sounded <<D1_CUSUM_GAIN>> weeks earlier on average than a single-week threshold. The eight hypotheses of Section 3.6.3 were recorded before any Albay result existed.

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

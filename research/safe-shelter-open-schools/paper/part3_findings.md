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
| Integral, lexicographically optimal plan (Props. 1 to 3) | <<V1_N>> instances (14 to 26 road nodes, 3 to 7 origins, 3 to 8 shelters, two hazard zones); Algorithm 1 against five sequential linear programs solved with HiGHS | All five levels equal in all <<V1_N>> instances (<<V1_LEVELS>> values); no fractional flow |
| Classroom packing bound (Prop. 4) | <<V2_N>> instances that use classrooms; exact minimum from a mixed-integer program (HiGHS) | Bound held in all <<V2_N>>; packing exact in <<V2_EXACT>>; one extra classroom in <<V2_G1>> and two in <<V2_G2>> (up to <<V2_MMAX>> schools in use) |
| Time-expanded network (Prop. 6) | 60 random graphs with one origin and one shelter, horizons 0 to 60 minutes; maximum flow on $G^T$ against the linear program of Equation (15) | Agreement in all <<V3_N>> pairs (<<V3_NZ>> with positive flow) |
| Clearance time and its bound (Props. 7, 8) | <<V4_N>> instances; Algorithm 2 against a minute-by-minute scan | Same $T^*$ in all <<V4_N>>; bound never violated; bound over $T^*$ averaged <<V4_LBMEAN>> (lowest <<V4_LBMIN>>); <<V4_BIS>> maximum flows per bisection against <<V4_SCAN>> per scan |
| Monotonicity (Props. 5, 9) | 120 instances: a random road closed, a shelter added, nested alert scenarios | No violation in <<V5_CT>> clearance checks after a closure, <<V5_CR>> classroom checks after a closure, <<V5_AR>> after an added shelter, <<V5_AT>> clearance checks after an added shelter, or <<V5_AL>> alert-level checks |
| Submodularity of coverage (Prop. 10) | 80 instances (40 road networks, 40 built with overlapping coverage), 60 random triples each | No violation in <<V6_N>> checks of diminishing returns |
| Greedy siting (Prop. 10) | The same 80 instances, $k = 1$ to 4, against exhaustive search over all sets | Worst ratio <<V7_MIN>>, mean <<V7_MEAN>>, optimal in <<V7_OPT>> of <<V7_N>> cases; guaranteed 0.632 |

Two rows deserve comment. The packing row shows that the bound of Proposition 4 is not merely safe but nearly tight in practice: in the <<V2_GAPCASES>> instances where packing missed the exact minimum, the exact program regrouped evacuees between schools so that each school filled whole rooms. The clearance row shows the value of bisection: on the same instances, a minute-by-minute scan needed about five times as many maximum-flow computations.

## 3.4 Computational Cost

::: {custom-style="Paper Caption"}
**Table 8.** Time to compute the school-preserving plan (Algorithm 1, plain Python, network simplex, fastest of five runs).
:::

| Road nodes | Origins | Shelters | Road arcs | Evacuees | Time (s) |
|---------:|--------:|--------:|---------:|---------:|--------:|
<<TAB_PLAN>>

::: {custom-style="Paper Caption"}
**Table 9.** Size of the time-expanded network and time for one maximum flow (40 road nodes, 6 origins, 6 shelters, fastest of five runs).
:::

| Horizon (min) | Vertices | Arcs | Time per maximum flow (s) |
|---------:|---------:|---------:|---------:|
<<TAB_EXP>>

Albay has 720 barangays, and the largest row of Table 8, with 160 origin clusters and 120 shelters, already exceeds the evacuation of the whole Permanent and Extended Danger Zones of Mayon. The time-expanded network grows linearly with the horizon, as Proposition 7 predicts, and a clearance time of four hours costs about half a second per maximum flow, or a few seconds for the whole bisection.

## 3.5 Worked Instance E1

Instance E1 is a compact synthetic volcano on which a reader can follow each stage of the pipeline by hand (Figure 2). A ring road runs eight kilometers from the summit; five towns lie outside it, joined to the ring and to each other by highways; six barangay clusters lie inside or near the danger zones; and two lahar channels run down the southern flank, crossing seven road segments, each crossing a bridge. One minute is one time step; barangay roads carry 20 persons per minute at 15 kilometers per hour, the ring 30 persons per minute at 30 kilometers per hour, and highways 40. All figures are invented for the test; the names of the towns are only positions on the compass.

::: {custom-style="Figure Para"}
![](<<FIG_MAP>>){width=5.2in}
:::

::: {custom-style="Figure Caption"}
**Figure 2.** Instance E1: a synthetic volcano with six barangay clusters (red), six shelters in five towns (blue), the six-kilometer Permanent Danger Zone, the seven-kilometer Extended Danger Zone on the southern flank, and two lahar channels (brown lines) whose bridges are marked A1 to A4 and B1 to B3.
:::

::: {custom-style="Paper Caption"}
**Table 10.** Origins of E1 (synthetic).
:::

| Origin | Zone | Distance from summit (km) | Population | Vulnerable | Nearest shelter, minutes |
|:---|:---|---:|---:|---:|:-------|
<<TAB_ORIG>>

::: {custom-style="Paper Caption"}
**Table 11.** Shelters of E1 with capacities from Equation (3) (synthetic).
:::

| Shelter | Kind | Floor area for tiers 0 or 1 (m²) | Tier 0 | Tier 1 | Classrooms | Tier 2 | Accessible | Learners per room |
|:------------|:-------|--------:|-----:|-----:|----------:|-----:|:----------|--------:|
<<TAB_SHEL>>

The non-school shelters hold <<E1_CAP0>> persons, the school open spaces <<E1_CAP1>>, and the <<E1_ROOMS>> classrooms <<E1_CAP2>>, for <<E1_CAPT>> in all. SCH3 is a two-storey school without a ramp, so vulnerable evacuees may not be placed there.

### 3.5.1 Shelter Plans on E1

Table 12 compares the three plans of Section 2.11 in the three scenarios of Table 4.

::: {custom-style="Paper Caption"}
**Table 12.** Shelter plans on E1 by scenario. "Time-only" minimizes travel after placing everyone; "school-preserving" is Algorithm 1 (synthetic instance).
:::

| Scenario and plan | Evacuees | Placed | In non-school space | In school open space | In classrooms | Classrooms closed | Learners displaced | Mean trip (min) |
|:------------|--------:|-------:|-------:|-------:|----------:|----------:|---------:|------:|
<<TAB_PLANS>>

Three effects stand out. The first is capacity: if every barangay simply went to its nearest shelter site, <<E1_OVER_AL3>> evacuees would arrive at full sites at Alert Level 3, <<E1_OVER_AL4>> at Alert Level 4, and <<E1_OVER_AL4L>> in the compound scenario. The second is the classroom saving at Alert Level 3: both optimal plans shelter all <<E1_D_AL3>> evacuees and all <<E1_V_AL3>> vulnerable residents, but the time-only plan fills the nearby classrooms of SCH2 and SCH3 while the gymnasiums and halls farther away stay part-empty. The school-preserving plan fills every non-school space and school open space first and closes <<E1_ROOMS_LEX>> classrooms instead of <<E1_ROOMS_BLIND>>, sparing <<E1_LEARN_SAVED>> learners, at a cost of <<E1_EXTRA_MIN>> minutes of average travel. The third is saturation: at Alert Level 4 the shelters are <<E1_UTIL_AL4>> percent full, and the two plans almost coincide, because nearly every classroom is needed whatever the plan. When the shelter network itself is too small, only new shelters help (Section 3.5.4).

::: {custom-style="Paper Caption"}
**Table 13.** Who goes where under the school-preserving plan at Alert Level 3 (synthetic instance).
:::

| Origin | Shelter | Space | Persons |
|:---|:---|:----------|---:|
<<TAB_ASSIGN>>

The plan sends part of O1 past the nearby two-storey school to the covered court of EC3 and fills the school open spaces of SCH1 and SCH2 from O3. Only the <<E1_ROOM_PERSONS_LEX>> persons who cannot fit anywhere else go to classrooms, all in SCH3 and packed into <<E1_ROOMS_LEX>> rooms. By Proposition 4 with $m = 1$, no plan that shelters everyone could close fewer.

### 3.5.2 Classrooms and Learners

The classroom count turns into lost schooling. With the average class sizes of Table 11, the time-only plan at Alert Level 3 displaces <<E1_LEARN_BLIND>> learners and the school-preserving plan <<E1_LEARN_LEX>>. If the stay lasts the fifteen days that DepEd guidance allows for medium- and long-term displacement, the difference is <<E1_LD_SAVED>> learner-days of face-to-face classes kept, or <<E1_CD_SAVED>> classroom-days.

### 3.5.3 Evacuation over Time and the Lahar Bridges

::: {custom-style="Paper Caption"}
**Table 14.** Clearance time of the school-preserving plan and the lower bound of Proposition 8 (synthetic instance).
:::

| Scenario | Persons moved | Clearance time $T^*$ (min) | Lower bound (min) | Bound over $T^*$ |
|:----|---:|---:|---:|---:|
<<TAB_CLEAR>>

::: {custom-style="Figure Para"}
![](<<FIG_ARR>>){width=5.6in}
:::

::: {custom-style="Figure Caption"}
**Figure 3.** Evacuees inside shelters, $F(T)$, against minutes after the order to evacuate, for the three scenarios of E1 (synthetic instance).
:::

At Alert Level 3 the last evacuee is sheltered after <<E1_T_AL3>> minutes. <<E1_AL4_SENTENCE>> Figure 3 shows the shape behind these numbers: nobody arrives until the shortest trips end, then the curve climbs at the rate the busiest roads allow and flattens as the last, longest trips finish.

::: {custom-style="Paper Caption"}
**Table 15.** Closure of lahar bridges at Alert Level 4: with the plan held fixed (Definition 12) and with a new plan for the damaged network (synthetic instance).
:::

| Bridges closed | Clearance, plan held fixed (min) | Evacuees who cannot be sheltered | Classrooms closed | Clearance, new plan (min) | Mean trip, new plan (min) |
|:---------|---:|---:|---:|---:|---:|
<<TAB_CLOSE>>

Closed one at a time, the seven bridges barely matter: six leave the clearance time at <<E1_T_AL4>> minutes and the seventh, A4, adds one minute. The network has alternatives for every single crossing. A lahar, however, closes all the bridges over its channel at once. Losing channel A adds <<E1_DELTA_A>> minutes, and losing channel B adds <<E1_DELTA_B>>. Losing both cuts the southern pocket, the ring between the two channels with O3, O4, and the central school SCH1, from every other shelter: <<E1_TRAPPED>> residents can no longer be sheltered at all, and the plan held fixed can never finish. The model therefore gives a concrete warning that no single-bridge analysis would give: O3 and O4 must be evacuated before lahar-producing rain, or the pocket needs a shelter of its own.

### 3.5.4 Where to Build Ligtas Pinoy Centers on E1

The compound scenario is the hardest test for the shelter network: <<E1_D_AL4L>> evacuees, <<E1_TRAPPED>> of them unplaceable. Five candidate sites, one in each town, were offered with planned capacities from floor plans of 875 to 1,400 square meters, and coverage was measured with a 30-minute standard. Without new centers, <<E1_PHI0>> evacuees can be sheltered outside classrooms within that standard. Single sites would add <<E1_SINGLE>> evacuees.

::: {custom-style="Paper Caption"}
**Table 16.** Greedy choice of Ligtas Pinoy Center sites in the compound scenario, against exhaustive search, and the plan recomputed with the chosen centers (synthetic instance). $k$ is the number of sites built, rooms are classrooms; towns: TS south, TNE northeast, TSW southwest.
:::

| $k$ | Greedy choice | Gain $f(S_g)$ | Best choice | Best gain | Not sheltered | Persons in rooms | Rooms closed | Learners displaced | Clearance (min) |
|:----|:--------|-----:|:--------|-----:|---------:|----------:|-----------:|----------:|-----------:|
<<TAB_SITE>>

The greedy rule found the best set for every $k$. Its first choice, the south town, is inside the cut-off pocket, and it shelters <<E1_POCKET_SAVED>> of the <<E1_TRAPPED>> residents who had nowhere to go. The second and third choices cut the persons in classrooms from <<E1_SIT_ROOM0>> to <<E1_SIT_ROOM2>> and then <<E1_SIT_ROOM3>>, closing <<E1_SIT_K2_ROOMS>> and then <<E1_SIT_K3_ROOMS>> classrooms instead of <<E1_SIT_K0_ROOMS>>. The southeast city gains nothing: its existing shelters already cover everyone who can reach it within half an hour.

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

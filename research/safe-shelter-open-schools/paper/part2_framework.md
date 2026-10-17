# 2. FRAMEWORK

Figure 1 shows the three layers of the framework. Sections 2.1 to 2.5 set out the data layer: hazard scenarios, the residents who must leave, the roads they travel, and the shelters able to receive them. Sections 2.6 and 2.7 form the planning layer, which assigns each evacuee to a shelter. Sections 2.8 to 2.10 make up the time and siting layer, which estimates how long the evacuation lasts, identifies the bridges that matter, and chooses sites for new evacuation centers.

::: {custom-style="Figure Para"}
![](<<FIG_FRAMEWORK>>){width=6.3in}
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

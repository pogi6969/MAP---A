# 2. FRAMEWORK

The model is built in three layers (Figure 1). The movement layer (Sections 2.1 and 2.2) records where the residents of each barangay spend their daylight hours. The transmission layer (Sections 2.3 to 2.5) adds mosquitoes, writes the equations of infection, and extracts the reproduction number and its parts. The decision layer (Sections 2.6 to 2.9) turns those quantities into a control plan, a map of infection places, and an outbreak alarm.

::: {custom-style="Figure Para"}
![](<<FIG_FRAMEWORK>>){width=6.3in}
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
| $\kappa$ | two-generation constant of Equation (5) | <<KAPPA>> |

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

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

**Remark 5 (Reading the alarm).** Part (ii) turns a design choice into a promise: with $h$ = <<D1_H>> and weekly counts at least two above the reference value, the alarm needs at most <<D1_DELAYBOUND>> weeks. Part (iii) prices the promise in false alarms before any season begins.

## 3.3 Software Verification

Every proven property was tested on random synthetic instances against code written separately from the model (Table 7). Instances had 2 to 20 barangays scattered over a 20-by-20-kilometer square, 500 to 8,000 residents each, 10 to 45 percent of the day away from home, and between 0.5 and 4 mosquitoes per resident; parameters were drawn at random around the values of Table 4.

::: {custom-style="Paper Caption"}
**Table 7.** Checks on the model, produced by `verify_dengue.py` against independent reference computations.
:::

| Property | How it was checked | Result |
|:----------------|:------------------------------|:-------------------------|
| Reproduction number (Prop. 1) | <<V1_N>> instances (2 to 12 barangays, random parameters); Equation (5) against the spectral radius of a next-generation matrix built from finite-difference Jacobians of Equation (4) | Largest relative difference <<V1_ERR>> |
| Threshold (Prop. 2) | <<V2_JN>> instances rescaled to $\mathcal{R}_0$ between 0.7 and 1.3: sign of $\mathcal{R}_0 - 1$ against the largest real part of the eigenvalues of the linearized system; <<V2_SN>> two-year simulations with $\mathcal{R}_0$ = 0.8 or 1.25 | Agreement in <<V2_JA>> of <<V2_JN>>; outbreak exactly when $\mathcal{R}_0 > 1$ in <<V2_SA>> of <<V2_SN>> simulations |
| Bounds (Props. 4, 5) | <<V3_N>> instances with 2 to 20 barangays | No violation of either bound; ratio of $\mathcal{R}_0^2$ to its province-average value: mean <<V3_HETMEAN>>, largest <<V3_HETMAX>>; network value above every isolated barangay in <<V3_ABOVE>> instances |
| Shares and gradient (Prop. 6) | <<V4_N>> instances with a simple largest eigenvalue and random control | Shares add to one within <<V4_SHERR>>; gradient against central differences within <<V4_GERR>> (relative) |
| Convexity and monotonicity (Prop. 7) | <<V5_N>> random pairs of plans | No violation of midpoint convexity or monotonicity |
| Least-cost control (Props. 8, 9) | <<V6_GN>> two-barangay instances against an 801-by-801 grid; <<V6_SN>> instances with 3 to 8 barangays against a general nonlinear solver (SLSQP) from 12 random starts | Consistent with the grid in <<V6_GOK>> of <<V6_GN>> and with SLSQP in <<V6_SOK>> of <<V6_SN>>; largest certified gap <<V6_GAP>>; certificate plan never missed the target; its extra cost averaged <<V6_PREM>> percent (largest <<V6_PREMMAX>>) |
| Inversion (Prop. 11) | <<V7_EN>> noise-free instances; the same with random errors; <<V7_NN>> instances with about 320 Poisson-distributed cases | Exact recovery within <<V7_ERR>>; Varah bound never exceeded; inferred shares closer to the truth than shares by residence in <<V7_CLOSER>> of <<V7_NN>> (mean total variation <<V7_TVI>> against <<V7_TVN>>) |
| Alarm (Prop. 12) | Average run length by Equation (iii) against 20,000 simulated runs for six designs; <<V8_DN>> sequences for the delay bound and for monotonicity | All six within the 95% interval of the simulation; no violation of the delay bound or of monotonicity |
| Solutions of Equation (4) (Prop. 3) | 30 one-year simulations; fourth-order Runge-Kutta with steps 0.8 to 0.1 days | Smallest state value <<V9_MIN>>; populations kept within <<V9_CONS>>; observed order of accuracy <<V9_ORDER>> (theory: 4) |

The least-cost row deserves a comment. The general solver started from twelve points and returned plans no cheaper than the certified upper bound; in the two-barangay cases the grid, which cannot miss the region of the optimum, found no plan below the certified lower bound. The certificate row shows the price of speed: a quick linear program that is always safe but costs on average <<V6_PREM>> percent more.

## 3.4 Computational Cost

::: {custom-style="Paper Caption"}
**Table 8.** Time per computation in plain Python with NumPy and SciPy (target $\mathcal{R}_0 = 0.95$ from $\mathcal{R}_0 = 1.5$).
:::

| Barangays | Reproduction number (s) | Place shares (s) | Certificate plan (s) | Least-cost plan (s) | Newton steps | Certified gap |
|-------:|----------:|--------:|---------:|---------:|-------:|--------:|
<<TAB_TIME>>

The reproduction number and the shares for all 720 barangays of Albay take a fraction of a second. The exact least-cost plan for the whole province, with its certificate of optimality, takes about a minute; the safe certificate plan takes about one second.

## 3.5 Worked Instance D1

Instance D1 is a synthetic town of six barangays (Table 9, Figure 2). B1, the poblacion, holds the central school and the public market; B2 is a dense residential barangay; B3 lies at the edge of the center; B4 and B5 are farming barangays; and B6 is on the coast. Every number in this section belongs to this test network.

::: {custom-style="Paper Caption"}
**Table 9.** Barangays of the test network D1 (synthetic).
:::

| Barangay | Description | Residents | Households | Mosquitoes per resident | Attraction | Share of day away | Cost of full control (team-days) |
|:---------|:------------|---------:|----------:|-----------:|---------:|-------:|--------:|
<<TAB_BRGY>>

::: {custom-style="Figure Para"}
![](<<FIG_NET>>){width=5.4in}
:::

::: {custom-style="Figure Caption"}
**Figure 2.** Test network D1. Circle size shows residents, color shows mosquitoes per person present, and arrows show the daily flows of residents between barangays (synthetic).
:::

::: {custom-style="Paper Caption"}
**Table 10.** Residence-time matrix $P$ of D1: the share of biting hours that residents of the row barangay spend in the column barangay (synthetic).
:::

| From \\ To | B1 | B2 | B3 | B4 | B5 | B6 |
|:--|---:|---:|---:|---:|---:|---:|
<<TAB_P>>

### 3.5.1 How Much Transmission Each Place Carries

::: {custom-style="Paper Caption"}
**Table 11.** Transmission quantities of D1 (synthetic).
:::

| Barangay | People present by day | Mosquitoes per person present | Local exposure number $\mathcal{R}_i$ | $\mathcal{R}_0$ if isolated | Share of cases by residence (%) | Share of transmission by place (%) | Hotspot score per team-day ($\times 10^{-3}$) |
|:--------|-------:|--------:|-------:|------:|-------:|----------:|--------:|
<<TAB_TRANS>>

The network reproduction number is <<D1_R0>>, so dengue can spread in D1. The local exposure numbers run from <<D1_RMIN>> to <<D1_RMAX>>, and $\mathcal{R}_0^2$ = <<D1_R0SQ>> lies between them, as Proposition 4 requires. Spreading the same mosquitoes evenly over the same people would give <<D1_R0HOM>>, a slight underestimate (Proposition 5).

The two percentage columns tell different stories. Ranked by where cases live, B2 comes first with <<D1_CASE_B2>> percent of cases, because it has the most residents. Ranked by where transmission happens, B1 comes first with <<D1_SHARE_B1>> percent: its school and market gather people from every other barangay into the place with the most mosquitoes. Figure 3 shows the gap. A brigade sent to the barangay with the most cases would start in the wrong place.

::: {custom-style="Figure Para"}
![](<<FIG_SHARES>>){width=5.6in}
:::

::: {custom-style="Figure Caption"}
**Figure 3.** Shares of residents, of cases by residence, and of transmission by place in D1 (synthetic).
:::

Movement matters in a second way. If nobody left home, B1 would have $\mathcal{R}_0$ = <<D1_ISO_B1>> on its own, the highest of all, because its mosquitoes would bite only its own residents. Movement dilutes those bites over more people by day, which brings the whole network to <<D1_R0>>, but it also carries the infection to every barangay whose residents visit B1.

### 3.5.2 Vector Control at Least Cost

The target is $\mathcal{R}_0 \le$ <<D1_TARGET>>, with at most 80 percent of mosquitoes removed in any place. Table 12 compares the five strategies of Section 2.10.

::: {custom-style="Paper Caption"}
**Table 12.** Five ways to reach $\mathcal{R}_0 \le$ <<D1_TARGET>> in D1: the reduction of mosquitoes in each barangay, the total cost, and the reproduction number reached (synthetic).
:::

| Strategy | B1 (%) | B2 (%) | B3 (%) | B4 (%) | B5 (%) | B6 (%) | Cost (team-days) | $\mathcal{R}_0$ reached |
|:----------------|-----:|-----:|-----:|-----:|-----:|-----:|-------:|-------:|
<<TAB_STRAT>>

The least-cost plan uses <<D1_COST_EXACT>> team-days, <<D1_SAVE_UNI>> percent fewer than uniform control and <<D1_SAVE_RES>> percent fewer than control where cases live; Algorithm 1 certified that no plan can be cheaper than <<D1_LOWER>>. Its shape follows the hotspot scores: it removes the most mosquitoes it can at B1, works at B4 where mosquitoes are dense and cheap to reach, and leaves B2, the barangay with the most cases, untouched. Control where cases live is the most expensive of the five, because it spends heavily in B2, where few infections actually happen. The certificate plan is safe but costs <<D1_CERT_PREM>> percent more than the optimum and overshoots the target, reaching <<D1_CERT_R0>>.

::: {custom-style="Paper Caption"}
**Table 13.** The season factor and the least cost of reaching the target in D1 (synthetic).
:::

| Season factor $\varsigma$ | $\mathcal{R}_0$ without control | Least cost (team-days) |
|---:|---:|---:|
<<TAB_SEASON>>

Table 13 applies Proposition 10. Below a season factor of <<D1_SFAC_THRESH>>, dengue cannot take hold in D1 at all. Each rise of 0.2 in the factor adds roughly ten to twelve team-days to the bill, which tells a provincial health office how much brigade time to set aside before the rains.

### 3.5.3 Where People Got Infected

Four weeks of synthetic case reports were generated from the model's own pattern of infection and passed through Algorithm 2 (Table 14).

::: {custom-style="Paper Caption"}
**Table 14.** Cases by residence and infections by place over four weeks in D1 (synthetic).
:::

| Barangay | Cases by residence | Infections by place (model truth) | Infections by place (inferred) |
|:--|---:|---:|---:|
<<TAB_INV>>

The residence column again points to B2. The inferred column points to B1 and comes close to the true distribution, which is unknown in practice but known here because the data are synthetic. By Proposition 11 the error of the exact inverse is at most <<D1_VARAH>> times the error of the reported rates.

### 3.5.4 Early Warning

The alarm was designed for a municipality that expects between 6 and 11 cases a week, with a seasonal peak in August. With $h$ = <<D1_H>>, a normal year triggers a false alarm with probability <<D1_FA_C>>; the single-week rule was set to the same probability (<<D1_FA_T>>, with $z$ = <<D1_Z>>). In 5,000 simulated years with an outbreak beginning in week <<D1_ONSET>>, the CUSUM alarm sounded on average <<D1_DELAY_C>> weeks after the start (median <<D1_MED_C>>), and the single-week rule <<D1_DELAY_T>> weeks after (median <<D1_MED_T>>). Neither missed an outbreak.

::: {custom-style="Figure Para"}
![](<<FIG_CUSUM>>){width=5.6in}
:::

::: {custom-style="Figure Caption"}
**Figure 4.** One simulated outbreak year in D1. Top: weekly cases, the expected count, and the single-week threshold. Bottom: the CUSUM statistic and its alarm level. In this particular year the single-week rule fired in week <<D1_ALARM_T>> and the CUSUM in week <<D1_ALARM_C>>; averaged over 5,000 years, the CUSUM fired earlier (synthetic).
:::

::: {custom-style="Paper Caption"}
**Table 15.** Exact average run lengths in weeks (Proposition 12) of the CUSUM and of a single-week rule set to a false-alarm rate at least as low, before and after a rise in the weekly mean.
:::

| Weekly mean | CUSUM $k$, $h$ | CUSUM, no rise | Single-week rule, no rise | CUSUM, rise of 50% | Single-week rule, rise of 50% | CUSUM, doubling | Single-week rule, doubling |
|------:|:------|-------:|-------:|-------:|-------:|-------:|-------:|
<<TAB_ARL>>

Table 15 shows the reason in exact numbers. For every design, the single-week rule was given a false-alarm rate no worse than the CUSUM's, and still the CUSUM detected a rise of one half far sooner: after <<D1_ARL_EX_C>> weeks instead of <<D1_ARL_EX_T>> in the design with a mean of 5 cases and $h$ = 10. One week seldom looks unusual on its own, but a run of weeks a little above normal accumulates.

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

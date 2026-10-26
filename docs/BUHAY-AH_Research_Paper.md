# BUHAY-AH: A Budget-to-Blueprint Design Generator, Standards-Based Quantity Take-Off, and Hybrid Machine Learning System for Start Quotations and Over-Budget Detection in Public Buildings, Bridges, Airports and Seaports

**Enrique Miguel C. Buban**

Lead Researcher

Mathematics and Computational Science 2026

# ABSTRACT

Padded prices in public infrastructure cost communities classrooms, clinic beds and safe crossings, while machine-learning screens learn only from past prices and cannot say what a project should cost. This study developed BUHAY-AH, a system that designs a public building or bridge from a requirement or a budget, performs a standards-based quantity take-off under NSCP 2015, DPWH specifications and AASHTO LRFD, and prices it with DPWH pay items into a lean start quotation, a standard fair estimate and a ceiling. A design generator composes 55 reusable space modules into 41 building and 13 bridge templates, and a budget-to-design search returns the Pareto-efficient designs that fit a budget. Multiple Linear Regression, XGBoost, Isolation Forest and SHAP are combined with the over-budget ratio into a risk index. On a 300-project simulated benchmark of Bicol buildings and bridges with 36 injected overpricing cases, the standard estimate reached a mean absolute percentage error of 5.21% for buildings and 7.67% for bridges. XGBoost outperformed regression on bridges (MAPE 19.18% vs. 65.65%), and the risk index flagged 94.4% of padded contracts (AUC = 0.987) against 27.8% for an Isolation Forest alone. Budget-to-design searches finished in a median of 3.6 ms, all 152 space-standard checks passed, and allowing multi-storey designs added up to 10 classrooms per school budget. Extended to hospitals, airport, seaport and jeepney, UV Express and bus terminals, runways and piers on a 180-project benchmark, the standard estimate reached 6.40% error and the standards rule caught 95.5% of padded contracts. BUHAY-AH runs as a mobile application and website.

***Keywords:*** **Construction Cost Estimation, Generative Design, Budget Optimization, Quantity Take-Off, Over-Budget Detection, XGBoost, SHAP, Airports, Seaports, Hospitals, Transport Terminals**

# TABLE OF CONTENTS

[ABSTRACT i](#abstract)

[TABLE OF CONTENTS ii](#table-of-contents)

[LIST OF FIGURES iv](#list-of-figures)

[LIST OF TABLES vi](#list-of-tables)

[LIST OF EQUATIONS vii](#list-of-equations)

[LIST OF APPENDICES xii](#list-of-appendices)

[INTRODUCTION 1](#introduction)

[Background of the Study 1](#background-of-the-study)

[Research Gap and Rationale 4](#research-gap-and-rationale)

[Objective of the Study 6](#objective-of-the-study)

[Significance of the Study 7](#significance-of-the-study)

[Scope and Delimitation 8](#scope-and-delimitation)

[Definition of Terms 10](#definition-of-terms)

[FRAMEWORK 13](#framework)

[Theoretical Framework 13](#theoretical-framework)

[Conceptual Framework 15](#conceptual-framework)

[Mathematical Framework 16](#mathematical-framework)

[Plan Acquisition and Variable Extraction 17](#plan-acquisition-and-variable-extraction)

[Design Generation and Budget-to-Design Optimization 19](#design-generation-and-budget-to-design-optimization)

[Standards Codification and Price Book 22](#standards-codification-and-price-book)

[Quantity Take-Off and Quotation Engine 23](#quantity-take-off-and-quotation-engine)

[Extension to Hospitals, Transport Terminals, Airfields and Ports 52](#extension-to-hospitals-transport-terminals-airfields-and-ports)

[Simulated Benchmark Dataset (SBD-300) 27](#simulated-benchmark-dataset-sbd-300)

[Model Development 28](#model-development)

[Model Validation 30](#model-validation)

[3D Visualization 31](#3d-visualization)

[App and Website Development 31](#app-and-website-development)

[FINDINGS 32](#findings)

[Plan Variables and Derived Indicators Extracted from Building and Bridge Plans 32](#plan-variables-and-derived-indicators-extracted-from-building-and-bridge-plans)

- a.) [Physical Properties 33](#a-physical-properties)
- b.) [Structural System and Foundation 34](#b-structural-system-and-foundation)
- c.) [Location, Price Year and Project Budget 34](#c-location-price-year-and-project-budget)

[Generation of Designs from Requirements and Budgets 35](#generation-of-designs-from-requirements-and-budgets)

- a.) [Modular Design Library 35](#a-modular-design-library)
- b.) [Budget-to-Design Optimization 38](#b-budget-to-design-optimization)
- c.) [Compliance and Bridge Type Selection 39](#c-compliance-and-bridge-type-selection)

[Accuracy of the Standards-Based Quantity Take-Off Engine 41](#accuracy-of-the-standards-based-quantity-take-off-engine)

- a.) [Lean Start Quotation, Standard Fair Estimate and Ceiling 41](#a-lean-start-quotation-standard-fair-estimate-and-ceiling)
- b.) [Accuracy against Fair Awarded Costs 42](#b-accuracy-against-fair-awarded-costs)

[Development of Machine Learning Models to Predict Construction Cost 44](#development-of-machine-learning-models-to-predict-construction-cost)

- a.) [Multiple Linear Regression 44](#a-multiple-linear-regression)
- b.) [Extreme Gradient Boosting 47](#b-extreme-gradient-boosting)

[Detection of Over-Budgeted Contracts 50](#detection-of-over-budgeted-contracts)

[Extension to Hospitals, Transport Terminals, Airfields and Ports 52](#extension-to-hospitals-transport-terminals-airfields-and-ports-1)

- a.) [Design Templates and Space Standards 52](#a-design-templates-and-space-standards)
- b.) [Accuracy of the Standard Estimate 56](#b-accuracy-of-the-standard-estimate)
- c.) [Detection by the Standards-Based Rule 56](#c-detection-by-the-standards-based-rule)

[Deployment of BUHAY-AH as a Mobile Application and Download Website 57](#deployment-of-buhay-ah-as-a-mobile-application-and-download-website)

- a.) [Mobile Application with Design Studio 57](#a-mobile-application-with-design-studio)
- b.) [Download Website 68](#b-download-website)
- c.) [Floor Plans, Parametric 3D Visualization and SHAP Explanations 70](#c-floor-plans-parametric-3d-visualization-and-shap-explanations)

[CONCLUSION 72](#conclusion)

[RECOMMENDATIONS 73](#recommendations)

[REFERENCES 75](#references)

[APPENDICES 75](#appendices)

# LIST OF FIGURES

Figure 1. Theoretical Paradigm 14

Figure 2. Conceptual Paradigm 16

Figure 3. Methodological Paradigm 17

Figure 4. Model Integration Framework 30

Figure 5. System Architecture of BUHAY-AH 32

Figure 6. Generated Ground Floor Plan of a 2-Storey 6-Classroom School Building 36

Figure 7. Generated Ground Floor Plan of a 25-Bed Community Hospital 36

Figure 8. Generated Plan of an Evacuation Center for 200 Persons 37

Figure 9. Generated Plan of a 100-Stall Public Market 37

Figure 10. Budget-to-Design Frontier for School Buildings by Storey Limit 39

Figure 11. Generated Elevation of a Three-Span RCDG Bridge (3 × 20 m) 40

Figure 12. Generated Elevation of a 45 m Steel Truss Bridge 41

Figure 13. Distribution of the Over-Budget Ratio for Injected and Non-Injected Projects 43

Figure 14. Global SHAP Values of the XGBoost Building Model 49

Figure 15. Global SHAP Values of the XGBoost Bridge Model 49

Figure 16. ROC Curves of the Screening Signals, All 300 Projects 51

Figure 17. Generated Ground Floor of a 100-Bed Level 2 Hospital 53

Figure 18. Integrated Land Transport Terminal with Jeepney, UV Express and Bus Bays 54

Figure 19. Generated Plan of a 1,200 × 30 m Turboprop Runway 55

Figure 20. Generated Section of a 60 × 15 m RoRo Pier on PC Spun Piles 55

Figure 21. Accuracy and Detection by Extension Class (SBD-EXT) 57

Figure 22. Home Screen of the BUHAY-AH Application 57

Figure 23. Design Studio with the Template Library 58

Figure 24. Design Editor with Floor Plan, Spaces, Standards Checks and 3D Model 59

Figure 25. Design from a Budget 60

Figure 26. Bridge Designer Comparing Superstructures for a 45 m Gap 61

Figure 27. Quote Screen with the Three Quotation Tiers and the ABC 62

Figure 28. Bill of Quantities Generated from the Plan 63

Figure 29. Plan Panel after Importing the Sample DXF Floor Plan 64

Figure 30. Check Screen Screening a Padded Contract 65

Figure 31. Line-Item Check of a Contractor's Bill of Quantities 66

Figure 32. Library Screen with Reference Plans, Saved Designs and the Unit Price Book 67

Figure 33. Download Website of BUHAY-AH 68

Figure 34. Live Budget-to-Design Demonstration on the Website 69

Figure 35. Download Section of the Website 70

Figure 36. Parametric 3D Model of a 2-Storey 4-Classroom School Building 70

Figure 37. Parametric 3D Model of a Three-Span RCDG Bridge 71

Figure 38. Parametric 3D Model of a 50 m Steel Truss Bridge 71

# LIST OF TABLES

Table 1. Plan Variables Extracted by BUHAY-AH 18

Table 2. Location Factors and Yearly Cost Index 18

Table 3. Space Module Library of the Design Generator 21

Table 4. Selected Pay Items and Direct Unit Costs in the BUHAY-AH Price Book 22

Table 5. Indirect Cost Brackets under DPWH D.O. 197 s. 2016 and D.O. 30 s. 2025 23

Table 6. Quotation Tier Settings 25

Table 7. Simulation Parameters of the SBD-300 Benchmark 27

Table 8. XGBoost Hyperparameter Search and Selected Values 28

Table 9. Descriptive Statistics of the Physical Properties of Buildings (n = 160) 33

Table 10. Descriptive Statistics of the Physical Properties of Bridges (n = 140) 33

Table 11. Structural System and Foundation Composition of the Benchmark 34

Table 12. Project Budget Characteristics of the Benchmark 34

Table 13. Design Template Library of BUHAY-AH 35

Table 14. Budget-to-Design Results (Lean Start Quotation, Albay 2025, Lot ≤ 60 m) 38

Table 15. Bridge Designs Recommended by Gap Length (Two Lanes) 39

Table 16. Quotations of the Reference Plans (Albay, 2025 Prices) 41

Table 17. Accuracy of the Standards-Based Estimate against Fair Awarded Costs 42

Table 18. Variance Inflation Factor of the Building Predictors 44

Table 19. Variance Inflation Factor of the Bridge Predictors, Full and Reduced Models 44

Table 20. Ordinary Least Squares Results for Buildings 45

Table 21. Ordinary Least Squares Results for Bridges 45

Table 22. Performance of the Multiple Linear Regression Models under LOOCV 46

Table 23. XGBoost Feature Importance (Gain Share) 47

Table 24. Performance of the XGBoost Models under LOOCV 47

Table 25. Comparison of Multiple Linear Regression and XGBoost 48

Table 26. Detection Performance against Injected Overpricing 50

Table 27. Highest-Risk Contracts Flagged by BUHAY-AH 51

Table 28. Extension Design Templates (Albay, 2025 Prices) 52

Table 29. Airfield and Port Templates 55

Table 30. Accuracy and Standards-Based Detection on SBD-EXT 56

# LIST OF EQUATIONS

This section lists the numbered equations of the study in the order they appear. Each entry gives the name of the formula, the section where it is defined, and how it is used in the model or in the BUHAY-AH application.

**Equation 1. Building Footprint from Space Modules** (Design Generation and Budget-to-Design Optimization)

Eq. 1

Gives the length, width and floor area of a generated design from its space modules; used by the design studio and the budget search.

**Equation 2. Design Capacity** (Design Generation and Budget-to-Design Optimization)

Eq. 2

Counts classrooms, beds, staff, persons, stalls, passengers or bays of a design; the objective of budget-to-design.

**Equation 3. Budget-to-Design Integer Program** (Design Generation and Budget-to-Design Optimization)

Eq. 3

Chooses the largest capacity whose quotation fits the budget, lot and storey limits; solved by exhaustive enumeration.

**Equation 4. Pareto Dominance** (Design Generation and Budget-to-Design Optimization)

Eq. 4

Removes designs beaten on both capacity and cost, so the app shows only efficient options.

**Equation 5. Bridge Type and Span Selection** (Design Generation and Budget-to-Design Optimization)

Eq. 5

Picks the cheapest superstructure and span count for a gap; used by the bridge designer.

**Equation 6. Isolated Footing Size** (Quantity Take-Off and Quotation Engine)

Eq. 6

Sizes each footing from the column load and soil bearing; feeds the concrete, rebar and excavation items.

**Equation 7. Reinforcing Steel Mass** (Quantity Take-Off and Quotation Engine)

Eq. 7

Turns concrete volumes into kilograms of reinforcing steel by element and tier.

**Equation 8. Estimated Direct Cost** (Quantity Take-Off and Quotation Engine)

Eq. 8

Sums every pay-item quantity times its unit cost, location factor and year index; the direct cost of the plan.

**Equation 9. Approved Budget for the Contract** (Quantity Take-Off and Quotation Engine)

Eq. 9

Adds OCM, profit and 5% VAT to the direct cost; gives the lean, standard and ceiling quotations.

**Equation 10. Over-Budget Ratio** (Quantity Take-Off and Quotation Engine)

Eq. 10

Divides the contract amount by the standard estimate; the main over-budget signal.

**Equation 11. Terminal Site Pavement and Canopy** (Extension to Hospitals, Transport Terminals, Airfields and Ports)

Eq. 11

Gives the PCCP area and loading canopy of a jeepney, UV Express or bus terminal from its bays.

**Equation 12. Airfield Pavement Quantities and Lights** (Extension to Hospitals, Transport Terminals, Airfields and Ports)

Eq. 12

Gives the PCC, base and subbase volumes and the number of edge, threshold and end lights of a runway or taxiway.

**Equation 13. Pier Piles, Pile Length and Fenders** (Extension to Hospitals, Transport Terminals, Airfields and Ports)

Eq. 13

Gives the pile length, number of piles and number of fenders of an open-type pier or

wharf.

**Equation 14. Over-Budget Risk Index for Extension Types** (Extension to Hospitals, Transport Terminals, Airfields and Ports)

Eq. 14

Risk index used for hospitals, terminals, airfields and ports, where only the standards-based signal is available.

**Equation 15. Simulated Awarded Cost** (Simulated Benchmark Dataset (SBD-300))

Eq. 15

Generates the awarded amounts of the simulated benchmarks with bid noise and injected overpricing.

**Equation 16. Multiple Linear Regression Formula** (Model Development)

Eq. 16

The interpretable cost model fitted on SBD-300 buildings and bridges.

**Equation 17. Variance Inflation Factor** (Model Development)

Eq. 17

Screens predictors for multicollinearity before the regression is fitted.

**Equation 18. XGBoost Additive Model and Regularized Objective** (Model Development)

Eq. 18

The gradient-boosted cost model and its regularized training objective.

**Equation 19. Isolation Forest Anomaly Score** (Model Development)

Eq. 19

Scores how unusual a contract is from its features, residual and over-budget ratio.

**Equation 20. SHAP Additive Feature Attribution** (Model Development)

Eq. 20

Splits each XGBoost prediction into feature contributions shown in the Check screen.

**Equation 21. BUHAY-AH Risk Index** (Model Development)

Eq. 21

Combines the three signals into the BUHAY-AH Risk Index; 30 or more is flagged.

**Equation 22. BUHAY-AH Risk Index Component Scores** (Model Development)

Scales and clips the over-budget, model and isolation signals to 0–1.

**Equation 23. Root Mean Square Error** (Model Validation)

Typical prediction error in pesos under LOOCV.

Eq. 22

Eq. 23

**Equation 24. Coefficient of Determination** (Model Validation)

Share of cost variance explained by a model or estimate.

**Equation 25. Mean Absolute Percentage Error** (Model Validation)

Average percentage error; compares small and large projects fairly.

**Equation 26. Precision, Recall and F1-Score** (Model Validation)

Detection metrics against the injected overpricing labels.

Eq. 24

Eq. 25

Eq. 26

# LIST OF APPENDICES

[Appendix A. Sample Records of the Simulated Benchmark Dataset (SBD-300) 75](#appendix-a-sample-records-of-the-simulated-benchmark-dataset-sbd-300)

Appendix B. BUHAY-AH Unit Price Book 77

Appendix C. Bill of Quantities of a 2-Storey 4-Classroom School Building 79

Appendix D. Cost Summary of a Three-Span RCDG Bridge 80

Appendix E. Snippets of Methodology (Quantity Take-Off Engine) 81

Appendix F. Snippets of Methodology (Model Training) 82

[Appendix G. Multiple Linear Regression: Actual vs. Predicted Cost 83](#appendix-g-multiple-linear-regression-actual-vs-predicted-cost)

[Appendix H. Extreme Gradient Boosting: Actual vs. Predicted Cost 84](#appendix-h-extreme-gradient-boosting-actual-vs-predicted-cost)

[Appendix I. Isolation Forest: Cost Residual vs. Anomaly Score 85](#appendix-i-isolation-forest-cost-residual-vs-anomaly-score)

[Appendix J. User Guide of the BUHAY-AH Application 86](#appendix-j-user-guide-of-the-buhay-ah-application)

[Appendix K. Design Template Library 87](#appendix-k-design-template-library)

[Appendix L. Research Plan 89](#appendix-l-research-plan)

[Appendix M. Risk and Safety Assessment 90](#appendix-m-risk-and-safety-assessment)

[Appendix N. Algorithms and Code Availability 91](#appendix-n-algorithms-and-code-availability)

[Appendix O. Additional References Cited 92](#appendix-o-additional-references-cited)

# INTRODUCTION

# Background of the Study

A building can pass inspection on paper and still cost the public far more than it should. Across the world, construction is consistently ranked among the sectors most exposed to corruption, and the Infrastructure Transparency Initiative estimates that 10% to 30% of investment in publicly funded infrastructure is lost to corruption, mismanagement and inefficiency (CoST, n.d.; Kenny, 2007). Large, one-off public projects are especially vulnerable because the client, the designer and the contractor hold very different information about what the work really requires (Locatelli et al., 2017), and cost estimates for public works are often shaped by strategic misrepresentation rather than honest error (Flyvbjerg et al., 2002). For this reason, procurement oversight has moved toward red-flag indicators that can be computed from contract data at scale instead of case by case (Fazekas & Tóth, 2016; OECD, 2016).

The Philippines shows the same pattern. Its score in the 2025 Corruption Perceptions Index fell to 32 out of 100, ranking 120th of 182 countries and the lowest since the current scoring method was adopted (Transparency International, 2026; Philstar, 2026). The decline followed a year dominated by public works. In August 2025 the President reported that flood-control projects implemented from July 2022 to May 2025 totalled ₱545.64 billion and that about 20% of this amount went to only 15 contractors (DZRH News, 2025; Philippine Center for Investigative Journalism \[PCIJ], 2025). Executive Order No. 94, s. 2025 then created the Independent Commission for Infrastructure to investigate anomalies and misuse of funds in flood-control and other infrastructure projects (Interaksyon, 2025). Overpricing does not always come from hidden deals; sometimes it sits in the arithmetic of the budget itself. In its 2022 audit of Cebu City, the Commission on Audit found the Cebu City Medical Center building overstated by about ₱62.64 million, partly because value-added tax was computed at

12% instead of the 5% prescribed by DPWH Department Order No. 197, s. 2016 (Cebu Daily News, 2023).

Buildings and bridges carry a particular weight in this problem. School buildings, health stations and evacuation centers are the facilities communities rely on during typhoons, and bridges are the links that keep them reachable. When the ₱1.225-billion Cabagan–Santa Maria Bridge in Isabela partially collapsed on 27 February 2025, less than a month after its official completion, investigators were asked to look into possible corruption alongside questions of design and overloading (Philstar, 2025). For buildings, every peso of padding is a classroom or a clinic room that is not built. Yet the estimate behind every public project, the program of works and the Detailed Unit Price Analysis that produce the Approved Budget for the Contract (ABC), is prepared project by project inside the implementing office, and outside reviewers such as local officials, auditors, journalists and citizens rarely have the means to rebuild an estimate from the plans.

Bicol Region V faces these concerns directly. The region lies in NSCP Seismic Zone 4 and in the path of frequent typhoons, so its public works program builds many school buildings, evacuation centers, health facilities and bridges. Earlier work on Bicol road contracts documented Commission on Audit findings on DPWH-Bicol projects worth ₱13 billion with lapses, and a 2025 Senate hearing that questioned farm-to-market road projects priced 68% above benchmark (Buban, 2026). These findings show that cost checks against an independent estimate are needed, but that they currently happen late, one project at a time, and mostly after funds have been released.

The same need reaches beyond schools and bridges. Hospitals funded under the Universal Health Care Act (Republic Act No. 11223), airport passenger terminals and runways, seaport terminals, piers and RoRo ramps, and the jeepney, UV Express and bus terminals required by the Public Utility Vehicle Modernization Program (Department of

Transportation \[DOTr], 2017) are among the largest facilities a region builds. Bicol has a new international airport in Daraga, RoRo ports such as Matnog that link Luzon to the Visayas, and growing provincial hospitals, yet no open tool prices them from their plans.

Machine learning has opened a way to screen many contracts at once. Regression has long been used for early cost estimates of construction projects (Mahamid, 2011), and recent reviews show tree ensembles and other parametric models becoming the standard tools for construction cost prediction (Elmousalami, 2020). Larocque et al. (2025) applied explainable machine learning to 11,646 road contracts, while Coffie and Cudjoe (2024) paired Extreme Gradient Boosting (XGBoost) with Shapley additive explanations (SHAP) to predict construction cost overruns. For anomaly detection, Isolation Forest isolates unusual records without requiring labelled fraud cases (Liu et al., 2008). Locally, the CORA system combined Multiple Linear Regression, XGBoost and Isolation Forest on 90 completed DPWH road contracts in Bicol, reaching an R2 of 0.8723 and a MAPE of 29.20% and flagging three contracts for review (Buban, 2026).

These tools, however, share one blind spot: they learn what similar projects *have* cost, not what a project *should* cost. If past prices are padded, the model learns the padding. They also cannot give a contractor, a local government or a citizen a defensible starting price for a new building or bridge. Cost engineering has long answered the second question with bottom-up, "should-cost" estimates built from quantities and unit rates (U.S. Government Accountability Office \[GAO], 2020), and the DPWH already prices projects this way through its pay items and Detailed Unit Price Analysis. What is missing is an independent, open tool that does this from the plan, under the same standards, and then uses machine learning as a second opinion rather than as the only reference.

A second need goes further back. Many barangays, schools and municipalities do not yet have plans when they ask for a facility; they have a need, such as eight more classrooms

or a place for 300 evacuees, and a budget. Today the design and its price are prepared by the same offices that later award the contract, so the requesting community has no independent sense of what its money should buy.

To close these gaps, this study develops BUHAY-AH (Buildings-and-Bridges Unit-cost Hybrid Analytics and Yardstick for Accountable and Honest infrastructure). Given a requirement or a budget, BUHAY-AH composes a schematic design from reusable space modules sized to DepEd, DOH, National Building Code and DSWD norms, and searches storey counts and capacities for the largest design whose quotation fits the budget. Given a design or an existing plan, it performs a parametric quantity take-off following the National Structural Code of the Philippines (NSCP) 2015, the DPWH Standard Specifications, the AASHTO LRFD Bridge Design Specifications and the National Building Code, prices the bill of quantities with DPWH pay items, and builds an ABC in three tiers: a lean start quotation, a standard fair estimate and a ceiling. When a contract amount is entered, the system compares it with the ceiling, with an XGBoost estimate learned from past projects and with an Isolation Forest score, and combines the three into the BUHAY-AH Risk Index. The name *buhay*, Filipino for "life", reflects both the research brought to life as a working application and the lives that depend on honest public infrastructure. Like CORA, BUHAY-AH is a screening layer: a flag calls for review and is never treated as proof of wrongdoing.

# Research Gap and Rationale

Five gaps motivate this study. First, there is a **scope gap**. Local cost-screening research has focused on roads, and CORA itself recommended extending the approach to buildings, bridges and other project types (Buban, 2026). Buildings and bridges have very different cost structures from pavements: vertical structural frames, masonry and finishes, mechanical, electrical, plumbing and fire protection works, piles, girders and substructures. A road model cannot price them.

Second, there is a **reference gap**. Data-driven models are top-down. They estimate cost from what comparable contracts were awarded for, so they are only as clean as their training data and they cannot produce an itemized quotation. Bottom-up estimates based on standards are the professional norm for fair pricing (GAO, 2020), but no open tool in the Philippines generates one from a plan and puts it beside a machine-learning check.

Third, there is a **validation gap**. Anomaly detectors in procurement are rarely tested against cases whose truth is known. CORA could report which contracts Isolation Forest flagged but not how many padded contracts it missed, and it recommended validating the flags (Buban, 2026). Without known positives, precision and recall cannot be measured.

Fourth, there is a **design gap**. Cost tools assume that a plan already exists. Communities that only know what they need and how much they have cannot obtain an independent starting design and price, and no local study has treated the choice of storeys and capacity under a budget as an optimization problem that can be solved exactly.

Fifth, there is an **access gap**. Most models stay in notebooks or desktop dashboards. The people closest to a project, such as barangay and municipal officials, school heads, auditors and reporters, need a tool on their phones that works with a need, a budget, a plan or a contract amount and that explains its answer in plain terms.

BUHAY-AH addresses these gaps by (1) covering public buildings, hospitals, transport terminals, bridges, airfield pavements and port structures, (2) pairing a standards-based yardstick with machine learning so that each checks the other, (3) validating detection on a benchmark in which overpricing was injected deliberately and is therefore known, (4) generating designs from requirements and budgets through exhaustive constrained search, and (5) delivering the system as an installable mobile application, an Android package and a download website.

# Objective of the Study

This study aimed to develop BUHAY-AH, a budget-to-blueprint design generator, standards-based quantity take-off and hybrid machine-learning system that produces start quotations and detects over-budgeted public buildings, bridges, airports and seaports in Bicol Region V. Specifically, it sought to answer the following research questions:

1. What plan variables and derived indicators can be extracted from building and bridge plans and engineering standards to estimate construction cost, in terms of:

(a) physical properties; (b) structural system and foundation; and (c) location and price year?

2. How can schematic designs of public buildings and bridges be generated from a requirement or a budget, in terms of: (a) a modular design library; (b) budget-to-design optimization; and (c) compliance with space and design standards?
3. How accurately does the standards-based quantity take-off engine estimate the construction cost of public buildings and bridges, in terms of: (a) the lean start quotation, standard fair estimate and ceiling; and (b) the mean absolute percentage error and coefficient of determination against fair awarded costs?
4. How do (a) Multiple Linear Regression and (b) Extreme Gradient Boosting perform in predicting the construction cost of buildings and bridges, in terms of R2, root mean square error and mean absolute percentage error under leave-one-out cross-validation?
5. How effectively do (a) the over-budget ratio, (b) the XGBoost cost residual, (c) the Isolation Forest, and (d) the hybrid BUHAY-AH Risk Index detect over-budgeted contracts, in terms of precision, recall, F1-score and area under the ROC curve?

6. How can the design generator and the standards-based engine be extended to hospitals, airport and seaport passenger terminals, jeepney, UV Express and bus terminals, airfield pavements and port structures, in terms of: (a) design templates and space standards; (b) accuracy of the standard estimate; and (c) detection of over-budgeted contracts by the standards-based rule?
7. How can the system be deployed as (a) a mobile application with a design studio,

(b) a download website, and (c) an explainable interface with floor plans, parametric 3D models and SHAP explanations?

# Significance of the Study

This study supports transparent and accountable spending on public buildings and bridges in Bicol by giving anyone with a need, a budget or a plan an itemized, standards-based design and price, and a fast way to see whether a contract amount is defensible. It extends its benefits to the following:

**DPWH and Implementing Offices.** District engineering offices can cross-check programs of works and ABCs against an independent take-off before bidding, and catch errors such as wrong markups or VAT rates early.

**Government Auditing and Investigating Bodies.** The Commission on Audit, the Office of the Ombudsman and the Independent Commission for Infrastructure can rank contracts by risk and focus field inspections on the projects that need them most.

**Local Government Units, DepEd and DOH Facility Owners.** Offices that request school buildings, health stations and evacuation centers obtain a starting design and quotation from their requirement or budget, plan their requests, and question estimates that exceed the ceiling.

**DOH, DOTr, CAAP, PPA and Transport Cooperatives.** Agencies and cooperatives that build hospitals, airports, seaports and PUV terminals get a design, a price and a ceiling for each project.

**Contractors.** Honest contractors gain a public reference that rewards fair bids and helps them defend their pricing.

**Filipino Taxpayers, Civil Society and Media.** Citizens and journalists can check a project on their phones, see the bill of quantities behind a price and see what a given budget should build.

**SDG 16.5, 16.6 and 16.10 Alignment.** The system targets corruption and bribery in public contracting, supports effective, accountable and transparent institutions, and widens public access to cost information (United Nations, 2015).

**SDG 9.1 and 11.5 Alignment.** Fair pricing protects the quality of resilient infrastructure and of the facilities that reduce disaster losses in a typhoon- and earthquake-prone region.

**SDG 12.7 and 4.a Alignment.** The lean, code-compliant start quotation supports sustainable public procurement under Republic Act No. 12009 and stretches school-building funds to more classrooms.

**Academe and Future Researchers.** The study contributes a reproducible pipeline, a benchmark with known overpricing and an open price book that future work can validate with actual contract records and extend to other project types.

# Scope and Delimitation

This study covers public buildings and bridges in the six provinces of Bicol Region V (Albay, Camarines Norte, Camarines Sur, Catanduanes, Masbate and Sorsogon) with price years from 2022 to 2026. Buildings include school buildings, government offices, health facilities, multi-purpose halls and evacuation centers, dormitories and public markets and

covered courts built as reinforced-concrete frames of up to six storeys; taller buildings are priced indicatively. Bridges include reinforced-concrete box culverts, reinforced-concrete deck girder (RCDG), prestressed concrete girder (PSCG) and steel truss bridges on spread footings, driven precast piles or bored piles. The extension covers DOH Level 1 to 3 hospitals, airport and seaport passenger terminals, land transport terminals for jeepneys, UV Express vans and buses, rigid runway, taxiway and apron pavements, and open-type piers and wharves on piles with causeways and RoRo ramps.

Air-traffic, navigation, medical and baggage equipment beyond the allowances, breakwater design, roads (covered by CORA), flood-control structures, water supply systems, land acquisition, right-of-way, design and supervision fees, furniture and equipment are excluded. Unit costs are indicative direct costs for 2025 based in Albay, adjusted by province location factors and a yearly cost index, and are meant to be replaced by the implementing office's current Detailed Unit Price Analysis or regional price data. Plan input accepts dimensions, reference plans and two-dimensional DXF outlines; building information models and scanned drawings are not parsed. Generated designs are schematic: they fix the spaces, footprint, storeys and structural grid needed for estimating, and must be developed and signed by licensed architects and engineers before construction.

Because machine-readable plans and itemized bills of quantities for awarded DPWH buildings and bridges are not publicly available in bulk, the models were trained and the detectors validated on a 300-project simulated benchmark (SBD-300). Each simulated project carries hidden site and market variation that the plan-level estimate cannot see, and 12% of projects carry injected overpricing whose size is known. The reported accuracy and detection figures therefore describe performance under the stated simulation assumptions and must be re-validated on actual contracts before operational use. The extension types are outside the training data of the models and are screened by the standards-based rule on a separate 180-

project benchmark (SBD-EXT). Lastly, BUHAY-AH is a screening tool: it does not replace the Commission on Audit, the Office of the Ombudsman, the Independent Commission for Infrastructure or any official audit procedure, and a flag is not evidence of irregularity, error or fraud.

# Definition of Terms

The following terms are defined conceptually and operationally to ensure a common understanding of the key concepts used in this study:

***Approved Budget for the Contract (ABC).*** The ceiling price a procuring entity sets for a contract. In this study, it is the estimated direct cost plus OCM, profit and VAT computed under DPWH D.O. 197 s. 2016 and D.O. 30 s. 2025, produced for each quotation tier.

***Anomaly Score.*** A value from 0 to 1 produced by the Isolation Forest; the higher the score, the easier a contract is to isolate from the others and the more unusual it is.

***BUHAY-AH Risk Index (BRI).*** A score from 0 to 100 that combines the over-budget ratio, the XGBoost cost residual and the anomaly score. A BRI of 30 or more is a high-risk flag; 20 to 30 calls for review.

***Ceiling Estimate.*** The highest price that can still be defended for a plan, computed with upper-bound reinforcement, premium finishes and a scope contingency. Amounts above it are flagged as over budget.

***Budget-to-Design Optimization.*** The search for the largest design of a facility whose quotation fits a budget, solved by evaluating every combination of storeys and capacity and keeping the Pareto-efficient designs.

***Design Module.*** A reusable space, such as a 7 × 9 m classroom, a six-bed ward or a hall bay for 20 persons, with a width, depth, category and capacity, from which designs are composed.

***Design Template.*** A saved program of design modules, storeys and layout for a typical facility; one of 41 building and 13 bridge designs in the library, which users can edit and combine.

***Detailed Unit Price Analysis (DUPA).*** The DPWH breakdown of the material, labor and equipment cost of one unit of a pay item. The BUHAY-AH price book holds the resulting direct unit costs.

***Estimated Direct Cost (EDC).*** The sum of all pay-item quantities times their unit costs, adjusted for location and price year, before indirect costs.

***Extreme Gradient Boosting (XGBoost).*** A gradient-boosted tree algorithm used as the primary data-driven cost model, trained on the logarithm of awarded cost from plan features (Chen & Guestrin, 2016).

***Isolation Forest.*** An unsupervised algorithm that isolates records through random splits and scores unusual records by their short average path length, without labelled examples (Liu et al., 2008).

***Lean Start Quotation.*** The lowest code-compliant price of a plan, computed with code-minimum reinforcement and basic finishes while keeping all NSCP, DPWH and PD 1096 requirements; the recommended starting price.

***Leave-One-Out Cross-Validation (LOOCV).*** A validation method in which each project is predicted by a model trained on all other projects, used here to measure prediction error on unseen projects.

***Multiple Linear Regression (MLR).*** A statistical model that expresses awarded cost as a weighted sum of plan features; the interpretable baseline of this study.

***Over-Budget Ratio (OBR).*** The contract amount divided by the BUHAY-AH standard fair estimate. A ratio of 1.00 means the contract equals the standard estimate.

***Parametric 3D Visualization.*** A 3D model generated directly from the plan variables and the engine's geometry, tinted by the screening result.

***Plan (Blueprint).*** The architectural and engineering drawings of a building or bridge. Operationally, the set of plan variables in Table 1, entered by the user, taken from a reference plan or read from a DXF file.

***Price Book.*** The table of DPWH pay items and their direct unit costs used by the engine, editable by the user.

***Pareto-Efficient Design.*** A design that no other design beats on both capacity and

cost.

***Progressive Web Application (PWA).*** A web application that can be installed on a phone or computer and works offline; the form in which BUHAY-AH is delivered.

***Quantity Take-Off (QTO).*** The measurement of work quantities, such as cubic meters of concrete and kilograms of reinforcing steel, from a plan. In BUHAY-AH it is computed parametrically from the plan variables using engineering standards.

***Reference Plan.*** One of 19 typical configurations of DPWH-implemented buildings and bridges stored in the application as a starting point, the "previous plans" library.

***SHAP (SHapley Additive exPlanations).*** A method that splits each model prediction into the contributions of its input features, shown in the application as the reasons behind the expected cost (Lundberg & Lee, 2017).

***Schematic Design.*** A design that fixes the spaces, footprint, storeys and structural grid needed for estimating, drawn as floor plans or elevations; it is not a construction drawing.

***Simulated Benchmark Dataset (SBD-300).*** The 300 simulated projects (160 buildings, 140 bridges) used to train and validate the models, with known true costs and 36 injected overpricing cases.

***Standard Fair Estimate.*** The ABC of a plan computed with typical DPWH design intensities and standard finishes; the reference for the over-budget ratio.

# FRAMEWORK

# Theoretical Framework

The theoretical framework rests on five theories that explain how a fair price can be established, how deviations from it arise, how the best design can be chosen under a budget, how a model can learn expected cost from data, and how its predictions can be explained. Each contributes a component of BUHAY-AH.

***Agency Theory***, formulated by Jensen and Meckling (1976), describes the relationship between a principal who delegates work and an agent whose interests and information differ. In public construction, the public and the oversight bodies are the principals, while implementing offices and contractors are the agents who know more about the true quantities and costs. The resulting information asymmetry is what padding exploits. In this study, the gap between a contract amount and an independent standards-based estimate, the over-budget ratio, is the measurable form of that asymmetry, and a large gap triggers review rather than accusation.

***Should-Cost (Engineering Cost Estimating) Theory*** holds that a fair price for a defined scope can be built bottom-up from the quantities of work and the unit cost of each item, plus justified indirect costs (GAO, 2020). Flyvbjerg et al. (2002) showed that public works estimates drift from such fundamentals when incentives reward misrepresentation. In this study, the theory grounds the quantity take-off engine: quantities come from the plan through NSCP, DPWH and AASHTO rules, and the ABC follows the DPWH indirect-cost structure, producing the lean, standard and ceiling tiers that serve as the yardstick.

***Optimization Theory*** studies how to choose the best decision from a set of feasible ones. When there are several objectives, such as more classrooms and lower cost, a decision

is Pareto-efficient if no other decision is at least as good on every objective and better on one (Pareto, 1906); choosing integer quantities such as storeys and rooms is a problem of combinatorial optimization (Nemhauser & Wolsey, 1988). In this study, budget-to-design is written as a constrained integer program, solved exactly by enumerating the discrete design space, and reported as the set of Pareto-efficient designs.

***Statistical Learning Theory***, developed by Vapnik (1998), treats prediction as learning a function from a finite sample and judges it by its error on unseen cases. It guides the data-driven layer: Multiple Linear Regression serves as an interpretable baseline, XGBoost learns non-linear patterns, and leave-one-out cross-validation measures generalization error. Isolation Forest applies the same learning view to anomalies, which are few and different and therefore easy to isolate (Liu et al., 2008).

***Cooperative Game Theory*** provides the Shapley value, which divides a coalition's payout among its members in proportion to their contribution (Shapley, 1953). Lundberg and Lee (2017) adapted it into SHAP, where each feature is a player and the predicted cost is the payout. In this study, SHAP shows auditors which plan features drove the expected cost of a project, so that a flag can be explained. Together these theories support the development of BUHAY-AH, as shown in Figure 1.

# Figure 1.

*Theoretical Paradigm*

# Conceptual Framework

This study was anchored on the Input-Process-Output-Feedback model, which shows how needs, budgets, plans, standards and data are transformed into designs, quotations and flags. The model fits the study because it makes explicit which inputs come from the plan, which from the standards and which from historical data, and how the outputs are fed back to improve the system.

The **input** consists of a requirement (classrooms, beds, staff, persons or stalls) or a budget when no blueprint exists, and of building and bridge plans, whether templates, reference plans, DXF floor plans or dimensions typed by the user; the plan variables they contain; the DPWH pay items and unit costs in the BUHAY-AH price book; the engineering standards that turn plans into quantities; and the contract amounts of past projects used to train the models.

The **process** begins with design generation, which lays out reusable space modules into a schematic plan and, for a budget, searches storeys and capacities for the best design that fits. The parametric quantity take-off then converts plan variables into concrete, reinforcing steel, formwork, masonry, roofing, finishes, piles and girders. Quantities are priced into an estimated direct cost and an ABC in three tiers. In parallel, Multiple Linear Regression and XGBoost estimate the expected cost from past projects, Isolation Forest scores how unusual a contract is, SHAP explains the expected cost, and the BUHAY-AH Risk Index combines the signals.

The **output** includes schematic floor plans, bridge elevations and 3D models; the lean start quotation, standard fair estimate and ceiling with a full bill of quantities; over-budget flags with their risk index, drivers and line-item variances; validated accuracy and detection metrics; and the deployed mobile application, Android package, offline package and

download website. The **feedback** loop returns residuals, confirmed flags, user updates to the price book and saved checks to refine the price book, thresholds and models.

# Figure 2.

*Conceptual Paradigm*

# Mathematical Framework

This study used a quantitative developmental research design combined with a simulation-based computational experiment, the approach of the Mathematics and Computational Science: the problem was expressed as mathematical models and solved with algorithms whose accuracy was measured. Four kinds of mathematics carry the study: a deterministic parametric cost model (quantity take-off and ABC), combinatorial optimization (budget-to-design), statistical and machine-learning models (regression, gradient boosting, isolation and Shapley values), and Monte Carlo simulation (the benchmark with known overpricing). The developmental part designed and built the design generator, the quantity take-off engine, the hybrid models and the application. The experimental part generated a benchmark of 300 projects in which the true cost and the presence and size of overpricing are known, so that estimation accuracy and detection performance could be measured directly. Model performance was measured through leave-one-out cross-validation (LOOCV) and reported as R2, RMSE and MAPE, while detection was reported as precision, recall, F1-score

and the area under the ROC curve (AUC). The study involved no human participants, animals or hazardous materials; all computation ran on an ordinary laptop and in a web browser.

The system was developed in Python 3 with pandas, NumPy, scikit-learn, statsmodels, XGBoost, SHAP and matplotlib (Pedregosa et al., 2011; Seabold & Perktold, 2010; Chen & Guestrin, 2016; Lundberg & Lee, 2017), and in JavaScript for the application. The methods are as follows: Plan Acquisition and Design Generation, Standards Codification, Quantity Take-Off and Quotation, Simulated Benchmark Generation, Model Development, Model Validation, Explanation and Risk Scoring, and App and Website Development.

# Figure 3.

*Methodological Paradigm*

# Plan Acquisition and Variable Extraction

BUHAY-AH accepts a plan through four routes. A user can generate one from a requirement or a budget (next section); start from one of the design templates or the 19 reference plans, which are typical configurations of DPWH-implemented facilities such as one- to four-storey school buildings, health stations, evacuation centers, offices, markets, box culverts and girder and truss bridges; import a floor plan in DXF format; or type the dimensions. For DXF files, the largest closed polyline is read as the building outline, its area is computed with the shoelace formula and its perimeter from the vertex distances, and lines on layers named like WALL or PARTITION are measured as interior walls, halved when

walls are drawn with two lines. Drawing units are read from the $INSUNITS header or inferred from the drawing extent. Table 1 lists the plan variables used.

# Table 1.

*Plan Variables Extracted by BUHAY-AH*

| **VARIABLE** | **ASSET** | **UNIT** | **SOURCE IN PLAN** |
| --- | --- | --- | --- |
| *Length, width, footprint, perimeter* | Building | m, mZ | Floor plan / DXF outline |
| *Number of storeys, floor-to-floor height* | Building | –, m | Sections, elevations |
| *Column spacing (both directions)* | Building | m | Structural grid |
| *Facility type, roof system* | Building | category | Title block, roof framing plan |
| *Allowable soil bearing, seismic zone* | Building | kPa, zone | Geotechnical report, NSCP map |
| *Interior wall length* | Building | m | Floor plan / DXF wall layers |
| *Total length, number of spans* | Bridge | m, – | General plan and elevation |
| *Carriageway and sidewalk widths* | Bridge | m | Typical deck section |
| *Pier and abutment heights* | Bridge | m | Substructure details |
| *Superstructure and foundation type, pile length* | Bridge | category, m | General notes, pile schedule |
| *Province and price year* | Both | category, year | Project location, program year |

Derived indicators were then computed. For buildings, gross floor area (GFA) is footprint area times the number of storeys and the structural span is the larger bay dimension. For bridges, deck width is the carriageway plus both sidewalks plus 0.60 m of railing and curb, deck area is total length times deck width, and span length is total length divided by the number of spans. Categorical systems were encoded as ordinal indices: facility type by MEPF intensity (evacuation center 1 to health facility 6), superstructure by structural complexity (box culvert 1 to steel truss 4) and foundation by depth (spread footing 1 to bored pile 3). A location factor captures freight and barge premiums on island provinces, and a cost index brings each price year to 2025 levels (Table 2).

# Table 2.

*Location Factors and Yearly Cost Index*

| **PROVINCE** | **LOCATION FACTOR** | **PRICE YEAR** | **COST INDEX** |
| --- | --- | --- | --- |
| *Albay (base)* | 1.00 | 2022 | 0.90 |
| *Camarines Sur* | 1.00 | 2023 | 0.94 |
| *Camarines Norte* | 1.03 | 2024 | 0.97 |
| *Sorsogon* | 1.03 | 2025 (base) | 1.00 |
| *Masbate* | 1.10 | 2026 | 1.03 |

*Catanduanes* 1.12 – –

# Design Generation and Budget-to-Design Optimization

When no blueprint exists, BUHAY-AH builds one. The design generator holds 55 reusable space modules, each with a width along the building, a depth, a category and the capacity it adds (Table 3). Module sizes follow the national norms that govern each facility: the 7 × 9 m (63 mZ) classroom of the DepEd Educational Facilities Manual (Department of Education, 2010), consultation rooms, wards and delivery rooms after the DOH planning guidelines (Department of Health, 2016), open offices of six workstations, evacuation hall bays that give 3.5 mZ of covered living space per person (Sphere Association, 2018), and market bays of six to twelve stalls.

A requirement is first turned into a program, the list of spaces the facility needs. For a school of *k* classrooms the program holds *k* classrooms and a toilet block on every floor, and adds a principal's office and clinic from six classrooms, a faculty room and library from ten, and science and ICT laboratories from sixteen. Health facilities group beds into six-bed wards, two-bed labor rooms and isolation rooms; offices group staff into six-person open offices; evacuation centers use one hall bay per twenty persons. The spaces are then distributed over *N* floors with a greedy longest-first rule: the largest module goes to the floor with the shortest run, and spaces that must be reached from the street (offices, clinics, kitchens, stall bays) stay on the ground floor. One stair is added per floor, two when a floor is longer than 30 m so that every floor has two exits (RA 9514). Rooms are placed in rows in one of three layouts: single-loaded (one row facing an open corridor, as in DepEd schools), double-loaded (two rows on a central corridor, as in clinics and offices) or open (one to three rows without a corridor, as in halls and markets). The footprint follows from the rows:

Eq. 1

where *wi* is the width of module *i*, the maximum runs over floors *f* and rows *r*, *nr* is the number of rows, *d* the row depth and *c* the corridor width. The capacity of a design is the sum of its modules' capacities:

Eq. 2

The column grid is set by the module rhythm (4.5 m bays for schools, 5 to 6 m for other buildings), so every generated design yields the plan variables of Table 1 and goes straight into the quantity take-off. Any design, including one saved by the user, can be added to another as a wing: its modules are appended to the program and the layout is regenerated.

For a budget *B*, the best design is the solution of a constrained integer program over capacity *k* and storeys *N*:

Eq. 3

where *τ* is the price basis (lean start quotation or standard estimate), *Lmax* is the longest building the lot allows and *Nmax* the storey limit. Because support rooms enter at thresholds and a second stair appears beyond 30 m, cost is not monotonic in *k*, so bisection could skip feasible designs. The solver therefore enumerates every point of the discrete grid and prices each design with the full take-off, which guarantees the optimum. With at most 150 capacity steps and five storey counts, the search costs O(|K| · Nmax · TQTO) evaluations at about 0.1 ms each. The results are filtered to the Pareto-efficient set:

Eq. 4

so the user sees, for example, the largest school the budget can buy and the cheapest design of each smaller size, but never a design that another beats on both capacity and cost. Algorithm 1 summarizes the procedure.

# Algorithm 1.

*Budget-to-Design Search*

input : usage u, budget B, price basis τ, storey limit Nmax, lot length Lmax

output: Pareto-efficient designs that fit B options ← ∅

for N ← 1 to Nmax do best ← none

for k ← kmin(u) to kmax(u) step Δk(u) do program ← PROGRAM(u, k, N)

rules

design stairs, grid

q (Algorithm 2)

← LAYOUT(program, N)

← QUOTE(design.plan)

▹ spaces from DepEd/DOH/NBC/DSWD

▹ greedy longest-first, rows,

▹ quantity take-off + ABC

if q\[τ] ≤ B and design.L ≤ Lmax and (best = none or k > best.k) then best ← (k, N, design, q)

if best ≠ none then options ← options ∪ {best}

return { x ∈ options : no y ∈ options with κ(y) ≥ κ(x), ABC(y) ≤ ABC(x), y ≠ x }

For bridges, the designer tries every superstructure whose economic span range fits the gap *G*: box culverts for spans of 1.5 to 4.5 m, RC deck girders for 8 to 25 m, prestressed girders for 24 to 40 m and steel trusses for 40 to 90 m, each at up to three span arrangements. Each option is priced with the bridge take-off and the cheapest is recommended:

Eq. 5

Every generated design is also checked against space and safety rules: classrooms of 63 mZ, corridors of at least 1.12 m (RA 9514), one or two stairs per floor as above, a toilet block with PWD cubicles on each floor (BP 344), at least 3.5 mZ of living space per evacuee, and windows of at least 10% of floor area (PD 1096). Table 3 lists the module library.

# Table 3.

*Space Module Library of the Design Generator*

| **GROUP** | **SPACE MODULES** | **TYPICAL SIZE** | **NORM** |
| --- | --- | --- | --- |
| *Learning* | Classroom, kindergarten, science and ICT laboratories, library, TVL workshop, faculty, admin, clinic, guidance, toilets | 9.0 × 7.0 m (63 mZ) | DepEd (2010) |
| *Health* | Consultation, treatment, 6-bed ward, labor, isolation, delivery, laboratory, pharmacy, dental, nurse station, waiting, toilets | 3.5–7.0 × 5.0 m | DOH (2016) |
| *Civic & office* | Open office (6 staff), private office, session hall, conference, records, lobby, custodial facility, pantry, toilets | 3.0–12.0 × 6.0 m | PD 1096 |
| *Evacuation & assembly* | Hall bay (20 persons), stage, communal kitchen, showers, women & child-friendly space, triage, relief storage | 4.0–8.0 × 12.0 m | Sphere (2018) |
| *Market* | Wet bay (12 stalls), dry bay (10), eatery bay (6), office, loading, toilets | 4.0–6.0 × 12.0 m | PD 1096 |
| *Living* | Dorm room (8 beds), staff quarters, toilet & bath, lounge, warden, laundry | 3.0–6.0 × 5.0 m | PD 1096 |
| *Court & circulation* | Playing court 28 × 15 m with run-off, bleachers, stair | 32 × 20 m; 3.5 m stair | RA 9514 |

# Standards Codification and Price Book

The engineering standards were codified as take-off rules, and the unit costs as a price book keyed to DPWH pay items: Volume III (2019) item numbers for building works, adopted through D.O. No. 42, s. 2021, and Volume II (2013) item numbers for bridge works. Each rate is a direct cost covering materials, labor and equipment for Bicol in 2025, and every rate can be edited in the application so that implementing offices can load their own Detailed Unit Price Analysis. Table 4 shows selected entries; the full price book is in Appendix B.

# Table 4.

*Selected Pay Items and Direct Unit Costs in the BUHAY-AH Price Book*

| **PAY ITEM** | **DESCRIPTION** | **UNIT** | **RATE (₱)** |
| --- | --- | --- | --- |
| 900 (1)c | Structural concrete, fc′ 20.7 MPa (3000 psi), 28 days | m3 | 7,900 |
| 902 (1) | Reinforcing steel bars, deformed, Gr. 40/60, incl. tie wire | kg | 82 |
| 903 (2) | Formworks and falseworks | mZ | 850 |
| 1046 (3) | CHB masonry 150 mm, reinforced & grouted (exterior) | mZ | 1,080 |
| 1046 (2) | CHB masonry 100 mm (partitions) | mZ | 880 |
| 1027 (1) | Cement plaster finish | mZ | 360 |
| 1047 (3) | Structural steel trusses & purlins, fabricated & installed | kg | 140 |
| 1013 (2) | Pre-painted long-span metal roofing 0.50 mm, incl. accessories | mZ | 760 |
| 1018 (2) | Ceramic floor tiles 600 × 600 mm | mZ | 1,180 |
| 1008 (1) | Aluminum-framed glass windows | mZ | 6,200 |
| 1010 | Doors complete with jamb & hardware | set | 13,500 |
| 803 (1)a | Structure excavation, common soil | m3 | 380 |
| 405 (1)a | Structural concrete Class A — deck & girders, incl. forms | m3 | 13,500 |
| 405 (1)b | Structural concrete Class A — abutments, piers, walls, incl. forms | m3 | 11,200 |
| 405 (1)c | Structural concrete Class A — footings, pile caps, approach slabs | m3 | 9,400 |
| 404 (1) | Reinforcing steel Gr. 60, incl. tie wire | kg | 84 |
| 406 (1)b | Precast PSC girder AASHTO Type IV — supply, fabricate, launch | m | 42,000 |
| 403 (1) | Structural steel, fabricated, painted & erected | kg | 210 |
| 400 (11) | Precast RC piles 450 × 450 mm, furnished & driven | m | 11,500 |
| 400 (17) | Bored piles 1.0 m Ø, drilling incl. temporary casing | m | 28,000 |
| 412 (1) | Elastomeric bearing pads | pc | 16,500 |
| 505 (2) | Grouted riprap, Class A (slope protection) | m3 | 3,100 |

Indirect costs follow DPWH Department Order No. 197, s. 2016, whose overhead, contingencies and miscellaneous (OCM) and profit percentages are carried into D.O. No. 30,

s. 2025 for estimates from 2026. Both are applied as a share of the estimated direct cost

(EDC) by bracket, and value-added tax is 5% of the sum of EDC, OCM and profit (Table 5). BUHAY-AH also uses these caps to check submitted ABCs for excessive markups or a wrong VAT rate.

# Table 5.

*Indirect Cost Brackets under DPWH D.O. 197 s. 2016 and D.O. 30 s. 2025*

| **ESTIMATED DIRECT COST** | **OCM** | **PROFIT** | **TOTAL MARKUP** |
| --- | --- | --- | --- |
| *Up to ₱5 million* | 15% | 10% | 25% |
| *Above ₱5 million up to ₱50 million* | 12% | 8% | 20% |
| *Above ₱50 million up to ₱150 million* | 10% | 8% | 18% |
| *Above ₱150 million* | 8% | 8% | 16% |
| *Value-added tax* | 5% of (EDC + OCM +<br>profit) |  |  |

# Quantity Take-Off and Quotation Engine

For buildings, the engine lays out the column grid from the plan dimensions and bay spacing and sizes the reinforced-concrete frame from the number of storeys. Columns are 300 mm square for up to two storeys, the NSCP 2015 minimum for special moment frames (Section 418.7.2.1), 400 mm for three to four storeys and 500 mm for five to six. Beam depth is the larger of 0.40 m and span/12, slabs are 125 mm for short spans up to 4.5 m and 150 mm beyond, and isolated footings are sized from the service load on each column and the allowable soil bearing:

Eq. 6

where *α* = 0.75 accounts for edge and corner columns, *sx* and *sy* are the bay dimensions, *N* is the number of storeys, *w* is the service load per floor (10.0 to 13.0 kPa by facility type) and *qa* is the allowable bearing pressure. Reinforcing steel is computed from element volumes and intensities:

Eq. 7

where *ρe* is the reinforcement intensity of element *e* in kg/m3 (footings 90, columns 220, beams 190, slabs 100, stairs 100 at the standard tier), *Ve* is the concrete volume, *ζ* is 1.00 for Seismic Zone 4 and 0.88 for Zone 2, and *τ* is the tier factor in Table 6. Masonry, plaster, painting, ceilings and floor finishes follow from wall and floor areas, window area is kept at no less than 10% of floor area as required for natural light by PD 1096, roof steel is taken as 14 + 0.6*W* kg per mZ of footprint plus 5.5 kg/mZ of purlins, and electrical, plumbing, fire protection and mechanical works are priced as allowances per mZ of GFA by facility type, with sprinklers required for buildings of three or more storeys and for health facilities, markets and dormitories under RA 9514.

For bridges, deck slabs are 200 mm (220 mm on steel trusses). RCDG girders are spaced at about 2.1 m with depth of the larger of 0.90 m and span/13 + 0.10 m. PSCG girders are spaced at about 2.4 m and selected by span: AASHTO Type III up to 24 m, Type IV up to 32 m and bulb-tee BT-1600 beyond. Steel truss weight is (55 + 4.2*S*) kg per mZ of deck for span *S*. Abutment stems are 0.50 + 0.06*H* m thick on footings 0.55*H* + 1.2 m wide for height *H*, piers have two or three circular columns of 1.0 to 1.2 m diameter under a coping, and pile counts follow the pile-cap footprint at 1.2 m spacing for 450 mm driven piles and 3.0 to 3.5 m for 1.0 m bored piles. Bearings, expansion joints, railings, approach slabs, slope protection, approach pavement, mobilization, occupational safety and health, traffic management and testing complete the bill of quantities.

Every quantity *Qi* is multiplied by its unit rate *ri* and by the location and year factors to give the estimated direct cost, which is then marked up into the ABC:

Eq. 8

Eq. 9

where *o* and *π* are the OCM and profit rates of the EDC bracket and *v* is the 5% VAT rate. The engine runs three times per plan with the tier settings in Table 6. The lean tier is the **start quotation**: it keeps every code requirement but uses code-minimum reinforcement and basic finishes. The ceiling tier is the highest price that can still be defended for the scope.

# Table 6.

*Quotation Tier Settings*

| **SETTING** | **LEAN (START QUOTATION)** | **STANDARD (FAIR ESTIMATE)** | **CEILING** |
| --- | --- | --- | --- |
| *Reinforcement factor τ* | 0.80 | 1.00 | 1.25 |
| *Structural steel factor* | 0.92 | 1.00 | 1.15 |
| *Floor finish* | Cement topping | Ceramic tiles | Porcelain / granite |
| *MEPF allowance factor* | 0.85 | 1.00 | 1.25 |
| *Mobilization / OSH* | 1.0% / 1.0% | 1.2% / 1.5% | 1.5% / 2.0% |
| *Scope contingency* | – | – | 8% of works |

A contract amount is compared with the standard estimate through the over-budget

ratio:

Eq. 10

An OBR above 1.10 marks a contract for review, and an amount above the ceiling marks it as an over-budget flag. Algorithm 2 summarizes the engine.

# Algorithm 2.

*Quantity Take-Off and Approved Budget for the Contract*

input : plan variables p, tier τ ∈ {lean, standard, ceiling}, price book r, province, year

output: bill of quantities, EDC, ABC

grid ← BAYS(p.length, p.width, p.bayX, p.bayY); sizes ← NSCP_SIZING(p.storeys, spans) for each element e ∈ {footings, columns, beams, slabs, stairs, walls, roof, finishes, MEPF} do

V_e ← VOLUME_OR_AREA(e, grid, sizes) parametric rules

M_e ← τ.rebar · ζ · ρ_e · V_e

mass

add (pay item, Q_e, r_e · λ_loc · λ_yr) to BOQ EDC ← Σ Q_i · r_i · λ_loc · λ_yr

(o, π) ← BRACKET(EDC); ABC ← EDC · (1 + o + π) · (1 + v)

markups

return BOQ, EDC, ABC

▹ NSCP / DPWH / AASHTO

▹ reinforcing steel

▹ estimated direct cost

▹ D.O. 197 / D.O. 30

# Extension to Hospitals, Transport Terminals, Airfields and Ports

The design generator was extended with 51 new space modules and six usages: hospitals whose service level grows with size under DOH A.O. 2012-0012 (Level 2 adds ICU and NICU; Level 3 adds dialysis and more operating rooms) on 2.44 m patient corridors (Department of Health, 2016); airport terminals sized by peak-hour passengers (PHP) to at least 14 mZ per PHP (International Air Transport Association \[IATA], 2019); seaport terminals with 1.5 mZ per seated passenger; and jeepney, UV Express and bus terminals whose loading bays follow the design vehicles of AASHTO (2018). Hospitals add medical gases, standby power and bed elevators; terminals add curtain walls, baggage handling and site works. The terminal site area is:

Eq. 11

where *nm* bays of mode *m* have width *wm*, stall depth *dm*, aisle share *am*, holding share *hm* and canopy depth *cm*. Runways, taxiways and aprons follow ICAO Annex 14 widths (International Civil Aviation Organization \[ICAO], 2022) with rigid sections from FAA AC 150/5320-6G (Federal Aviation Administration \[FAA], 2021):

Eq. 12

Open-type piers and wharves stand on bents of piles every *b* m, with pile length from water depth *D*, deck level *zd* and embedment *e*, and fenders every 12 m of berth face *f* (Overseas Coastal Area Development Institute of Japan \[OCDI], 2009; PIANC, 2002):

Eq. 13

Because the models were trained only on SBD-300, the extension types are screened by the standards-based signal:

Eq. 14

SBD-EXT, a 180-project benchmark built with the same hidden variation, bid noise and 12% injected overpricing as SBD-300 (22 injected cases), measures accuracy and detection for the six classes.

# Simulated Benchmark Dataset (SBD-300)

To measure accuracy and detection against a known truth, a benchmark of 160 buildings and 140 bridges was generated with a fixed random seed. Plans were sampled from realistic ranges for each facility and bridge type (Table 7), provinces were weighted toward the larger provinces, award years were drawn from 2022 to 2025, and each project received a hidden reality the plan does not show: unit prices per cost category varied log-normally with a 7% standard deviation, reinforcement intensity by ±10%, concrete by ±6%, formwork by

±8%, earthworks by +5% ± 15%, MEPF by ±10%, and pile lengths by a factor of 0.95 to 1.35 reflecting geotechnical surprises. The true cost was priced by the same engine with these hidden adjustments, and the awarded amount was:

Eq. 15

where *η* represents bid competition and *μ* is the markup. For 88% of projects *μ* = 1 except for 4% aggressive low bids (*μ* = 0.78 to 0.88). For the remaining 12%, 36 projects in all, overpricing was injected: half moderate (*μ* = 1.20 to 1.40) and half severe (*μ* = 1.40 to 2.10). The plan seen by the estimator is the declared plan, so the benchmark tests whether the yardstick and the models can see through realistic noise.

# Table 7.

*Simulation Parameters of the SBD-300 Benchmark*

| **ELEMENT** | **BUILDINGS (n = 160)** | **BRIDGES (n = 140)** |
| --- | --- | --- |
| *Types* | School 40%, office 14%, health 12%,<br>evacuation 16%, dormitory 6%, market<br>12% | Box culvert 18%, RCDG 42%, PSCG<br>30%, steel truss 10% |
| *Size* | 1–4 storeys; 2–5 classrooms; 10–50 m long | 1–5 spans; 2–70 m spans; 4.0–13.4 m carriageway |
| *Hidden price variation* | log-normal, σ = 0.07 per cost category | log-normal, σ = 0.07 per cost category |
| *Hidden quantity variation* | rebar ±10%, concrete ±6%, MEPF ±10% | rebar ±10%, concrete ±6%, piles ×0.95–<br>1.35 |

|  |  |  |
| --- | --- | --- |
| *Bid competition* | eη, η ~ N(−0.02, 0.045Z) | eη, η ~ N(−0.02, 0.045Z) |
| *Injected overpricing* | 20 projects | 16 projects |

# Model Development

The machine-learning layer was built separately for buildings and bridges and chained so that each stage fed the next. Multiple Linear Regression served as the interpretable baseline:

Eq. 16

where *yi* is the awarded cost of project *i*, *xik* is its *k*-th predictor, *βk* the coefficients and *εi* the error. Multicollinearity was checked with the variance inflation factor, and the composite variable (deck area or footprint) and then the predictor with the highest VIF were removed until all VIFs fell at or below the conventional threshold of 10 (Kutner et al., 2004; O'Brien, 2007):

Eq. 17

Extreme Gradient Boosting served as the primary cost model. It adds regression trees that each correct the previous ones and penalizes tree complexity (Chen & Guestrin, 2016):

Eq. 18

The model was trained on the natural logarithm of cost so that small culverts and large bridges carry comparable weight, and tuned by randomized search over 40 settings of tree depth, number of trees, learning rate, L1 and L2 penalties, minimum child weight, row subsampling and column subsampling, scored by five-fold MAPE (Table 8).

# Table 8.

*XGBoost Hyperparameter Search and Selected Values*

| **HYPERPARAMETER** | **SEARCH SPACE** | **SELECTED (BUILDINGS)** | **SELECTED (BRIDGES)** |
| --- | --- | --- | --- |
| max_depth | 2, 3, 4, 5 | 2 | 2 |

|  |  |  |  |
| --- | --- | --- | --- |
| n_estimators | 100–400 | 300 | 300 |
| learning_rate | 0.02–0.10 | 0.05 | 0.05 |
| reg_alpha | 0–2.0 | 0.2 | 0.2 |
| reg_lambda | 0.5–3.0 | 3.0 | 3.0 |
| min_child_weight | 1, 2, 3, 5 | 5 | 5 |
| subsample | 0.7–1.0 | 0.7 | 0.7 |
| colsample_bytree | 0.6–1.0 | 0.9 | 0.9 |

Isolation Forest then screened for unusual contracts. Its inputs were the standardized plan features, the XGBoost residual ln(actual / predicted) and the log over-budget ratio, with 200 trees and a contamination of 0.10. Each record receives an anomaly score from its average path length (Liu et al., 2008):

Eq. 19

where *E*\[*h*(*x*)] is the average path length of record *x* across trees, *c*(*n*) is the average path length of an unsuccessful search in a tree of *n* records and *H* is the harmonic number. As in CORA, a statistically unusual contract was reported only if its cost was also above both the model and the standards-based estimates. SHAP values were computed on the final XGBoost model with the exact tree path-dependent algorithm (Lundberg et al., 2018), so that each prediction splits into a base value and feature contributions:

Eq. 20

Finally, the three signals were combined into the BUHAY-AH Risk Index, which weights the standards-based evidence most heavily because it does not depend on past prices:

Eq. 21

Eq. 22

where \[·]₀¹ clips a value to the range 0 to 1, *C* is the contract amount, *Ĉ* is the XGBoost expected cost and *s* is the anomaly score. A BRI of 30 or more is a high-risk flag and 20 to 30 marks a contract for review. Figure 4 shows how the components fit together.

# Figure 4.

*Model Integration Framework*

Algorithm 3 gives the screening of one contract as it runs in the application.

# Algorithm 3.

*BUHAY-AH Screening of a Contract Amount*

input : plan p, contract amount C, trained models (MLR, XGBoost, Isolation Forest) output: risk index BRI, status, explanation

q ← QUOTE(p) ▹ Algorithm 2: lean, standard, ceiling

OBR ← C / q.standard ▹ over-budget ratio

Ĉ ← exp(XGBOOST(features(p))); φ ← TREESHAP(features(p))

SHAP values

s ← ISOLATION_SCORE(\[features(p), ln(C/Ĉ), ln OBR]) score

BRI ← 100 · (0.5 S_OBR + 0.3 S_ML + 0.2 S_ISO)

Index

▹ expected cost and

▹ isolation anomaly

▹ BUHAY-AH Risk

status ← red if BRI ≥ 30 or C > q.ceiling; amber if BRI ≥ 20; green otherwise return BRI, status, φ, primary driver = argmax_j |z_j|

# Model Validation

Given the moderate sample sizes, a single train-test split would give an unstable estimate, so leave-one-out cross-validation was used for both regression models (Molinaro et al., 2005): each project was held out once and predicted by a model trained on all the others. Three metrics evaluated cost prediction. RMSE gives the typical error in pesos, R2 gives the share of variance explained, and MAPE expresses error as a percentage of each project's cost so that culverts and long bridges can be compared:

Eq. 23

Eq. 24

Eq. 25

Detection was evaluated against the injected labels with precision, recall and the F1-score, and threshold-free performance with the area under the ROC curve:

Eq. 26

Four screening rules were compared: the standards-based rule (amount above the ceiling), the model residual rule (amount more than 1.25 times the XGBoost LOOCV prediction), the CORA-style Isolation Forest flag, and the BUHAY-AH Risk Index at 30.

# 3D Visualization

Each plan is rendered as a parametric 3D model built directly from the geometry the engine computes rather than from generic shapes, following the logic of parametric BIM dashboards. Buildings show the column grid, slabs, walls with window bands and the gable or flat roof; bridges show the deck, girder lines or truss panels, piers, abutments, railings, approaches and the waterway. The renderer uses an orthographic projection with flat shading on a 2D canvas so that it runs on low-end phones without a graphics library, and the model is tinted green, amber or red by the screening result.

# App and Website Development

The system was delivered as a progressive web application with five screens (Home, Design, Quote, Check and Library) that can be installed on Android, iOS and desktop and works offline after the first load. The cost engine is a single JavaScript file shared by the application and the Python research pipeline, so the app and the paper produce the same

numbers. The trained XGBoost trees and the Isolation Forest were exported to JSON and evaluated in the browser, with exact TreeSHAP ported from the reference implementation; parity tests against Python matched XGBoost predictions within 1×10⁻⁵ in log cost, Isolation Forest scores to machine precision and SHAP values within 2×10⁻⁷. An Android package is

built automatically from the same files with Capacitor through GitHub Actions, an offline ZIP package runs from a local folder, and a download website with a live budget-to-design demonstration is published from the same repository. Plans, saved checks and price-book edits stay on the user's device.

# Figure 5.

*System Architecture of BUHAY-AH*

# FINDINGS

This section presents the results of the study in the order of the research questions, from the plan variables and the accuracy of the standards-based engine to the machine-learning models, the detection benchmark and the deployed system.

# Plan Variables and Derived Indicators Extracted from Building and Bridge Plans

The first research question identified the variables that can be read from plans and standards and used to estimate cost. Nine variables describe each building and eleven describe each bridge (Table 1), grouped into physical properties, structural system and foundation, and location and price year.

# a.) Physical Properties

**Table 9.**

*Descriptive Statistics of the Physical Properties of Buildings (n = 160)*

| **VARIABLE** | **xG** | **SD** | **MIN** | **25%** | **50%** | **75%** | **MAX** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| *Gross Floor Area (m²)* | 672.33 | 373.44 | 116.58 | 383.30 | 614.88 | 873.00 | 1,991 |
| *Footprint Area (m²)* | 381.30 | 204.00 | 116.58 | 253.17 | 349.05 | 425.56 | 1,380 |
| *Storeys* | 1.89 | 0.89 | 1.00 | 1.00 | 2.00 | 2.00 | 4.00 |
| *Structural Span (m)* | 6.26 | 1.64 | 3.67 | 4.84 | 5.82 | 7.09 | 10.20 |
| *Floor Height (m)* | 3.67 | 0.73 | 2.91 | 3.19 | 3.33 | 4.07 | 5.88 |

Table 9 shows that gross floor area averaged 672.3 mZ and ranged from 116.6 mZ to 1,990.8 mZ, with a median of 614.9 mZ. Because the mean is above the median, the distribution is right-skewed: most projects are one- and two-storey facilities, with a few large multi-storey buildings and markets. Storeys ranged from 1 to 4, structural spans from 3.67 m to 10.20 m, and floor heights from 2.91 m to 5.88 m, the tallest belonging to evacuation centers and markets.

# Table 10.

*Descriptive Statistics of the Physical Properties of Bridges (n = 140)*

| **VARIABLE** | **xG** | **SD** | **MIN** | **25%** | **50%** | **75%** | **MAX** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| *Total Length (m)* | 40.86 | 38.88 | 2.00 | 12.25 | 31.20 | 53.90 | 189.50 |
| *Deck Width (m)* | 8.79 | 1.94 | 4.60 | 7.92 | 8.80 | 9.70 | 16.40 |
| *Deck Area (m²)* | 369.79 | 357.08 | 9.20 | 110.62 | 261.90 | 551.20 | 1,684 |
| *Span Length (m)* | 20.57 | 15.60 | 2.00 | 9.62 | 16.05 | 31.48 | 68.90 |
| *Pier Height (m)* | 3.94 | 3.89 | 0.00 | 0.00 | 4.71 | 6.53 | 11.53 |
| *Abutment Height (m)* | 5.31 | 1.56 | 2.03 | 4.05 | 5.42 | 6.72 | 7.99 |

For bridges (Table 10), total length averaged 40.9 m but ranged from 2.0 m for single-cell culverts to 189.5 m, and deck area from 9.2 mZ to 1,684.2 mZ. The standard deviation of length is close to its mean, so bridge size varies far more than building size, which later explains why bridges were harder to model. Deck width was more uniform, with half of the bridges between 7.92 m and 9.70 m, reflecting the standard two-lane carriageway.

# b.) Structural System and Foundation

**Table 11.**

*Structural System and Foundation Composition of the Benchmark*

| **CATEGORY** | **COUNT** | **SHARE** |
| --- | --- | --- |
| *School buildings* | 67 | 41.9% |
| *Multi-purpose / evacuation centers* | 22 | 13.8% |
| *Government offices* | 19 | 11.9% |
| *Health facilities* | 22 | 13.8% |
| *Public markets* | 20 | 12.5% |
| *Dormitories* | 10 | 6.2% |
| *RCDG bridges* | 70 | 50.0% |
| *PSCG bridges* | 31 | 22.1% |
| *RC box culverts* | 24 | 17.1% |
| *Steel truss bridges* | 15 | 10.7% |
| *Bridges on spread footings / driven piles / bored piles* | 42 / 55 / 43 | – |

Table 11 summarizes the structural systems. School buildings made up the largest building group, consistent with the classroom program, and 9 buildings used reinforced-concrete roof decks instead of steel trusses. Among bridges, RCDG and PSCG girders dominated; most piled bridges used bored piles, which carry the largest geotechnical uncertainty in the benchmark.

# c.) Location, Price Year and Project Budget

**Table 12.**

*Project Budget Characteristics of the Benchmark*

| **ITEM** | **BUILDINGS** | **BRIDGES** |
| --- | --- | --- |
| *Dependent variable* | Awarded contract cost (₱) | Awarded contract cost (₱) |
| *Range* | ₱5.37 million – ₱56.77 million | ₱1.00 million – ₱179.23 million |
| *Median* | ₱16.54 million | ₱36.66 million |
| *Total value* | ₱3,002.53 million | ₱6,290.43 million |
| *Provinces / years* | 6 provinces / 2022–2025 | 6 provinces / 2022–2025 |
| *Sample* | 160 projects | 140 projects |

Table 12 shows the budgets. Building contracts ranged from ₱5.37 million to ₱56.77 million, about 11 times, while bridge contracts ranged from ₱1.00 million to ₱179.23 million, about 180 times. This wide range is why the study reports MAPE, which expresses error relative to each project's cost, alongside RMSE in pesos.

# Generation of Designs from Requirements and Budgets

The second research question examined whether BUHAY-AH can produce usable schematic designs when no blueprint exists, from a design library, from a budget, and within space and design standards.

# a.) Modular Design Library

**Table 13.**

*Design Template Library of BUHAY-AH*

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **GROUP** | **TEMPLAT ES** | **STOREY S** | **GFA (m²)** | **START QUOTATION (₱M)** | **STANDARD**<br>**₱/m²** |
| *Schools, libraries, child development* | 16 | 1–4 | 214–2,489 | 5.97–52.38 | 24,451–30,796 |
| *Health facilities* | 6 | 1–2 | 149–744 | 5.17–19.52 | 32,069–41,634 |
| *Civic and office buildings* | 5 | 1–3 | 288–1,793 | 7.83–37.74 | 25,628–32,413 |
| *Evacuation centers and halls* | 6 | 1–2 | 300–3,024 | 7.92–59.04 | 22,265–30,176 |
| *Public markets* | 3 | 1–2 | 528–2,184 | 13.78–45.65 | 24,302–29,979 |
| *Dormitories and quarters* | 3 | 1–3 | 282–612 | 7.81–14.82 | 28,029–31,825 |
| *Covered courts* | 2 | 1–1 | 900–1,060 | 13.70–15.83 | 16,413–16,730 |
| *Bridges and culverts* | 13 | – | – | 1.73–132.71 | 232,584–<br>1,437,490 /m |

Table 13 summarizes the 41 building and 13 bridge templates generated from the 55 space modules; Appendix K lists each one. They range from a 149 mZ barangay health station to a 3,024 mZ multi-storey facility. The 2-storey 6-classroom school building, for example, comes out 38.5 m long and 9.5 m wide with 732 mZ of floor area, a lean start quotation of

₱16.25 million and a standard estimate of ₱18.77 million, about ₱3.13 million per classroom. Standard costs per mZ fall as buildings grow and stack, because roofs, foundations, toilets and stairs are shared by more floor area, a pattern the take-off reproduces without any fitted coefficient.

# Figure 6.

*Generated Ground Floor Plan of a 2-Storey 6-Classroom School Building*

# Figure 7.

*Generated Ground Floor Plan of a 25-Bed Community Hospital*

Figures 6 and 7 show two generated plans with their structural grid, room labels and areas, and overall dimensions. The school places 7 × 9 m classrooms in one row along an open 2.5 m corridor with a stair and a toilet block; the hospital places consultation, treatment, laboratory and waiting areas on a double-loaded 2.4 m corridor on the ground floor and its wards upstairs, giving 25 beds. Figures 8 and 9 show an open-plan evacuation center and a public market, folded into parallel rows so that neither exceeds 48 m per row.

# Figure 8.

*Generated Plan of an Evacuation Center for 200 Persons*

# Figure 9.

*Generated Plan of a 100-Stall Public Market*

# b.) Budget-to-Design Optimization

**Table 14.**

*Budget-to-Design Results (Lean Start Quotation, Albay 2025, Lot ≤ 60 m)*

| **FACILITY** | **BUDGET (₱M)** | **LARGEST DESIGN** | **START (₱M)** | **USED** | **OPTIONS** | **EVALUAT ED** | **ms** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| School building | 10 | 4 classrooms, 1 st. | 9.82 | 98% | 2 | 21 | 2.2 |
| School building | 25 | 9 classrooms, 2 st. | 23.45 | 94% | 3 | 54 | 4.8 |
| School building | 50 | 15 classrooms, 4 st. | 45.58 | 91% | 4 | 130 | 13.3 |
| School building | 80 | 15 classrooms, 4 st. | 45.58 | 57% | 4 | 154 | 9.4 |
| Health facility | 10 | 6 beds, 1 st. | 9.49 | 95% | 1 | 65 | 3.4 |
| Health facility | 25 | 48 beds, 2 st. | 24.98 | 100% | 3 | 398 | 23.5 |
| Health facility | 50 | 150 beds, 3 st. | 47.80 | 96% | 4 | 604 | 37.1 |
| Health facility | 80 | 150 beds, 3 st. | 47.80 | 60% | 3 | 604 | 24.0 |
| Government office | 10 | 18 staff, 1 st. | 8.85 | 89% | 1 | 27 | 1.0 |
| Government office | 25 | 60 staff, 1 st. | 21.29 | 85% | 1 | 90 | 3.2 |
| Government office | 50 | 168 staff, 3 st. | 49.55 | 99% | 3 | 199 | 8.7 |
| Government office | 80 | 258 staff, 4 st. | 66.60 | 83% | 4 | 200 | 10.4 |
| Evacuation center | 10 | none fits | – | – | 0 | 12 | 0.5 |
| Evacuation center | 25 | 200 persons, 1 st. | 24.57 | 98% | 2 | 34 | 2.7 |
| Evacuation center | 50 | 480 persons, 2 st. | 48.34 | 97% | 1 | 79 | 2.7 |
| Evacuation center | 80 | 860 persons, 2 st. | 79.37 | 99% | 2 | 131 | 5.1 |
| Public market | 10 | none fits | – | – | 0 | 10 | 0.2 |
| Public market | 25 | 100 stalls, 1 st. | 24.73 | 99% | 2 | 32 | 0.9 |
| Public market | 50 | 220 stalls, 2 st. | 49.91 | 100% | 2 | 77 | 2.0 |
| Public market | 80 | 420 stalls, 2 st. | 77.84 | 97% | 2 | 98 | 3.1 |
| Dormitory | 10 | 56 beds, 1 st. | 9.06 | 91% | 2 | 62 | 1.7 |
| Dormitory | 25 | 216 beds, 3 st. | 24.85 | 99% | 3 | 169 | 5.9 |
| Dormitory | 50 | 456 beds, 4 st. | 48.48 | 97% | 4 | 240 | 9.7 |
| Dormitory | 80 | 480 beds, 4 st. | 52.00 | 65% | 4 | 240 | 7.5 |

Table 14 reports 24 budget scenarios. In 18 of the 22 feasible cases the largest design used 85% or more of the budget; the cases with lower use are those where a limit binds before the money runs out. A ₱80 million school budget, for instance, buys 15 classrooms in a 4-storey building that already fills the 60 m lot at the four-storey DepEd limit, so the solver shows that the extra money should fund a second building rather than a padded one. Where even the smallest design costs more than the budget, as for a ₱10 million evacuation center or market, the solver says so instead of returning an under-scoped design. Each search evaluated at most 604 complete designs and finished in 37 ms or less, with a median of 3.6 ms for a full school search, fast enough to run on a phone as the user moves a budget slider.

# Figure 10.

*Budget-to-Design Frontier for School Buildings by Storey Limit*

Figure 10 plots the frontier for school buildings. With one storey the 60 m lot caps the building at five classrooms, so extra money buys nothing; allowing two, three and four storeys lifts the frontier step by step. Across budgets from ₱6 million to ₱80 million, allowing up to four storeys gave an average of 6.4 and up to 10 more classrooms than a single-storey policy for the same money. The steps are the integer nature of the problem: a classroom is added only when the next whole module, with its share of stairs and toilets, fits the budget.

# c.) Compliance and Bridge Type Selection

All 41 building templates passed all 152 applicable checks: classroom size, corridor width, stairs and exits per floor, toilets with PWD cubicles on every floor, evacuation living space and natural light. Because the checks run on every generated design, a user who removes a stair or a toilet block sees the warning at once.

# Table 15.

*Bridge Designs Recommended by Gap Length (Two Lanes)*

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **GAP**<br>**(m)** | **LOWEST-COST DESIGN** | **SPANS** | **STANDARD (₱M)** | **₱000 / m** | **RUNNER-UP (₱M)** |
| *6* | RC box culvert | 2 × 3.0 m | 3.33 | 555 | RC box culvert (3 spans), 3.39 |
| *12* | RC box culvert | 4 × 3.0 m | 5.60 | 467 | RC box culvert (5 spans), 5.66 |
| *20* | RC deck girder (RCDG) | 1 × 20.0 m | 21.79 | 1,089 | RC deck girder (RCDG) (2 spans), |

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | 25.24 |
| *30* | RC deck girder (RCDG) | 2 × 15.0 m | 27.82 | 927 | RC deck girder (RCDG) (3 spans), 31.88 |
| *45* | RC deck girder (RCDG) | 2 × 22.5 m | 33.70 | 749 | RC deck girder (RCDG) (3 spans), 35.74 |
| *60* | RC deck girder (RCDG) | 3 × 20.0 m | 41.43 | 690 | RC deck girder (RCDG) (4 spans), 43.67 |
| *90* | RC deck girder (RCDG) | 4 × 22.5 m | 55.43 | 616 | RC deck girder (RCDG) (5 spans), 57.35 |
| *120* | RC deck girder (RCDG) | 5 × 24.0 m | 68.28 | 569 | RC deck girder (RCDG) (6 spans), 69.71 |

Table 15 shows the bridge designer across gaps of 6 to 120 m. Box culverts were cheapest up to 12 m. Beyond that, multi-span RC deck girders were the lowest-cost option at every gap in this price book, because an extra pier costs less than prestressed or steel superstructure; the cost per meter fell from about ₱1,089 thousand for a 20 m crossing to

₱569 thousand for 120 m as abutment costs are shared. In practice, river hydraulics, debris during typhoons and navigation may require fewer piers and longer spans, so the designer lists every option with its price and lets the engineer choose; the price of that choice then becomes visible to the public.

# Figure 11.

*Generated Elevation of a Three-Span RCDG Bridge (3 × 20 m)*

# Figure 12.

*Generated Elevation of a 45 m Steel Truss Bridge*

# Accuracy of the Standards-Based Quantity Take-Off Engine

The third research question examined how well the engine prices buildings and bridges from their plans. Table 16 lists the three tiers for the 19 reference plans, priced for Albay at 2025 levels.

# a.) Lean Start Quotation, Standard Fair Estimate and Ceiling

**Table 16.**

*Quotations of the Reference Plans (Albay, 2025 Prices)*

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **REFERENCE PLAN** | **LEAN** | **STANDARD** | **CEILING** | **STANDARD /**<br>**m²** | **LEAN SAVING** |
| *1-storey 2-classroom school building* | ₱4.63M | ₱5.31M | ₱6.41M | ₱32,797/mZ | 12.9% |
| *2-storey 4-classroom school building* | ₱7.88M | ₱9.10M | ₱11.49M | ₱26,612/mZ | 13.5% |
| *3-storey 9-classroom school building* | ₱17.28M | ₱20.03M | ₱25.37M | ₱26,036/mZ | 13.7% |
| *4-storey 12-classroom school building* | ₱29.08M | ₱33.80M | ₱42.89M | ₱24,709/mZ | 14.0% |
| *Barangay health station* | ₱3.07M | ₱3.66M | ₱4.63M | ₱45,711/mZ | 16.0% |
| *2-storey rural health unit / birthing facility* | ₱12.83M | ₱15.66M | ₱20.08M | ₱32,634/mZ | 18.1% |
| *Multi-purpose evacuation center, 600 m²* | ₱14.00M | ₱16.13M | ₱20.34M | ₱26,884/mZ | 13.2% |
| *2-storey municipal office building* | ₱15.03M | ₱18.20M | ₱23.21M | ₱27,076/mZ | 17.4% |
| *3-storey provincial office building* | ₱38.16M | ₱46.87M | ₱60.09M | ₱24,109/mZ | 18.6% |
| *Public market, 1-storey* | ₱23.49M | ₱27.13M | ₱34.42M | ₱28,258/mZ | 13.4% |
| *3-storey dormitory* | ₱24.51M | ₱28.47M | ₱36.23M | ₱26,358/mZ | 13.9% |
| *Single-cell RC box culvert 3.0 × 3.0 m* | ₱1.73M | ₱1.87M | ₱2.20M | ₱62,874/mZ | 7.2% |
| *Double-barrel RC box culvert 2 × (3.0 × 2.5 m)* | ₱2.48M | ₱2.68M | ₱3.16M | ₱46,990/mZ | 7.4% |
| *Single-lane farm-to-market RCDG bridge 1 × 12 m* | ₱5.78M | ₱6.22M | ₱7.19M | ₱92,518/mZ | 7.1% |
| *Two-lane RCDG bridge 1 × 18 m* | ₱18.39M | ₱19.41M | ₱22.64M | ₱122,561/mZ | 5.3% |
| *Two-lane RCDG bridge 3 × 20 m* | ₱39.07M | ₱42.04M | ₱50.12M | ₱79,615/mZ | 7.1% |
| *Two-lane PSCG bridge 2 × 30 m (AASHTO Type IV)* | ₱56.28M | ₱59.00M | ₱67.09M | ₱105,735/mZ | 4.6% |
| *Two-lane PSCG bridge 4 × 35 m* | ₱119.21M | ₱124.62M | ₱143.72M | ₱95,712/mZ | 4.3% |
| *Two-lane steel truss bridge 1 × 50 m* | ₱62.19M | ₱65.79M | ₱79.88M | ₱149,527/mZ | 5.5% |

For buildings, the standard estimate ranged from ₱24,109 to ₱45,711 per mZ of gross floor area, with the smallest buildings, such as the barangay health station, costing most per mZ because fixed items like septic tanks, ramps and plumbing are spread over less floor area. The 2-storey 4-classroom school building came to ₱9.10 million, or about ₱2.28 million per classroom, and its lean start quotation was ₱7.88 million. For multi-span bridges, the standard estimate ranged from ₱0.70M to ₱1.32M per linear meter, rising from RCDG to PSCG to steel truss as spans lengthen. The lean saving was larger for buildings (12% to 19%) than for bridges (4% to 8%), because buildings carry finishes and MEPF allowances that can be specified leanly, whereas a bridge's cost is dominated by structural quantities that the codes already fix. Appendix C shows the full bill of quantities of the 2-storey 4-classroom school building.

# b.) Accuracy against Fair Awarded Costs

**Table 17.**

*Accuracy of the Standards-Based Estimate against Fair Awarded Costs*

| **MEASURE (NON-INJECTED PROJECTS)** | **BUILDINGS (n = 140)** | **BRIDGES (n = 124)** |
| --- | --- | --- |
| *MAPE, standard estimate* | 5.21% | 7.67% |
| *R², standard estimate* | 0.9799 | 0.9801 |
| *RMSE, standard estimate* | ₱1,229,130 | ₱5,160,512 |
| *MAPE, XGBoost (LOOCV)* | 11.82% | 17.24% |
| *Lean start quotation ≤ awarded cost* | 94.3% | 81.5% |
| *Awarded cost ≤ ceiling* | 100.0% | 88.7% |
| *Mean lean saving vs. standard* | 14.4% | 5.9% |

Table 17 compares the standard estimate with the awarded cost of the projects without injected overpricing. The engine reached a MAPE of 5.21% for buildings and 7.67% for bridges, with R2 of 0.9799 and 0.9801. This is less than half the error of the XGBoost model on the same projects (11.82% and 17.24%), showing the value of pricing from the plan instead of from comparable contracts. The lean start quotation stayed at or below the fair awarded cost for 94.3% of buildings and 81.5% of bridges, so it behaves as an efficient floor, and the ceiling covered 100.0% of fair building contracts and 88.7% of fair bridge contracts.

The lower bridge coverage comes from hidden pile lengths of up to 35% beyond the plan: a bridge whose piles must go deeper than designed can legitimately exceed the plan-based ceiling. This agrees with the long-standing observation that ground conditions are the largest source of cost uncertainty in substructures and shows why geotechnical data should accompany a bridge check.

Because the benchmark was generated with the same engine plus hidden variation, these figures measure how robust the plan-level estimate is to unseen site and market conditions of the stated size, not its accuracy on actual DPWH contracts, which remains to be validated (see Recommendations).

# Figure 13.

*Distribution of the Over-Budget Ratio for Injected and Non-Injected Projects*

Figure 13 shows the over-budget ratio of all 300 projects. Fair projects cluster around 1.0, while injected projects sit to the right of the review line, most of them beyond the ceiling. The overlap between the two groups is small for buildings and larger for bridges, which anticipates the detection results.

# Development of Machine Learning Models to Predict Construction Cost

The fourth research question compared Multiple Linear Regression and XGBoost as data-driven predictors of awarded cost, trained on all 300 benchmark projects including the padded ones, as an auditor would face in practice.

# a.) Multiple Linear Regression

**Table 18.**

*Variance Inflation Factor of the Building Predictors*

| **FEATURE** | **VIF** |
| --- | --- |
| *Gross Floor Area* | 7.4348 |
| *Footprint Area* | 5.7900 |
| *Number of Storeys* | 5.8024 |
| *Structural Span* | 1.0707 |
| *Floor Height* | 1.9786 |
| *Facility Type Index* | 1.3686 |
| *RC Roof Deck* | 1.1039 |
| *Location Factor* | 1.0522 |
| *Cost Index (Year)* | 1.0741 |

Table 18 shows that all building predictors stayed below the threshold of 10. Gross floor area (7.43), number of storeys (5.80) and footprint area (5.79) were the most correlated, as expected since gross floor area is footprint times storeys, but their overlap was moderate because footprints vary widely at every storey count. No predictor was removed.

# Table 19.

*Variance Inflation Factor of the Bridge Predictors, Full and Reduced Models*

| **FEATURE** | **VIF (FULL MODEL)** | **VIF (REDUCED MODEL)** |
| --- | --- | --- |
| *Total Length* | 44.4445 | 3.4172 |
| *Deck Width* | 2.3229 | 1.0743 |
| *Deck Area* | 44.3983 | removed |
| *Span Length* | 10.4170 | 2.9914 |
| *Pier Height* | 1.8396 | 1.8395 |
| *Abutment Height* | 1.4483 | 1.3780 |
| *Superstructure Type Index* | 12.1095 | removed |
| *Foundation Type Index* | 3.5079 | 3.3669 |
| *Pile Length* | 2.5744 | 2.5213 |
| *Location Factor* | 1.1048 | 1.0836 |
| *Cost Index (Year)* | 1.0237 | 1.0115 |

For bridges (Table 19), total length (44.44) and deck area (44.40) showed severe multicollinearity, structurally expected because deck area is total length times deck width, the same pattern CORA found between road length and pavement area (Buban, 2026). Superstructure type (12.11) was also collinear with span length because span determines the girder system. Removing Deck Area and Superstructure Type Index brought every VIF to

3.42 or below.

# Table 20.

*Ordinary Least Squares Results for Buildings*

| **VARIABLE** | **COEFFICIENT** | **STD. ERROR** | **t** | **P > \|t\|** | **[0.025** | **0.975]** |
| --- | --- | --- | --- | --- | --- | --- |
| *Constant* | -46,114,581 | 11,702,924 | -3.940 | <0.001* | -69,238,450 | -22,990,711 |
| *Gross Floor Area* | 20,379 | 2,347 | 8.683 | <0.001* | 15,741 | 25,016 |
| *Footprint Area* | 8,496 | 3,791 | 2.241 | 0.027* | 1,004 | 15,988 |
| *Number of Storeys* | 1,260,755 | 865,717 | 1.456 | 0.147 | -449,820 | 2,971,330 |
| *Structural Span* | 126,306 | 202,355 | 0.624 | 0.533 | -273,529 | 526,140 |
| *Floor Height* | 234,911 | 622,591 | 0.377 | 0.706 | -995,270 | 1,465,091 |
| *Facility Type Index* | 463,310 | 226,326 | 2.047 | 0.042* | 16,112 | 910,508 |
| *RC Roof Deck* | 1,403,944 | 1,461,220 | 0.961 | 0.338 | -1,483,289 | 4,291,178 |
| *Location Factor* | 18,028,194 | 7,380,574 | 2.443 | 0.016* | 3,444,878 | 32,611,510 |
| *Cost Index (Year)* | 25,035,073 | 9,020,962 | 2.775 | 0.006* | 7,210,505 | 42,859,641 |

Table 20 presents the building model (R2 = 0.8449, adjusted R2 = 0.8356, F = 90.79, p

< 0.001). Gross floor area was the strongest predictor (t = 8.683): holding the others constant, each additional mZ adds about ₱20,379 to the contract. Significant predictors at the 5% level were Gross Floor Area, Footprint Area, Facility Type Index, Location Factor, Cost Index (Year). Storeys, span, floor height and roof type were not significant once floor area was included, so their signs should not be read as independent effects. The large negative constant has no physical meaning on its own, since a building with zero floor area lies outside the data.

# Table 21.

*Ordinary Least Squares Results for Bridges*

| **VARIABLE** | **COEFFICIENT** | **STD. ERROR** | **t** | **P > \|t\|** | **[0.025** | **0.975]** |
| --- | --- | --- | --- | --- | --- | --- |
| *Constant* | -141,342,353 | 39,111,477 | -3.614 | <0.001* | -218,719,732 | -63,964,973 |
| *Total Length* | 630,763 | 53,583 | 11.772 | <0.001* | 524,756 | 736,769 |
| *Deck Width* | 2,545,124 | 602,620 | 4.223 | <0.001* | 1,352,912 | 3,737,336 |
| *Span Length* | 274,632 | 124,921 | 2.198 | 0.030* | 27,491 | 521,773 |

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| *Pier Height* | -2,613 | 393,175 | -0.007 | 0.995 | -780,463 | 775,237 |
| *Abutment Height* | 1,313,775 | 849,695 | 1.546 | 0.124 | -367,246 | 2,994,795 |
| *Foundation Type Index* | 8,727,086 | 2,644,518 | 3.300 | 0.001* | 3,495,222 | 13,958,949 |
| *Pile Length* | 340,928 | 171,104 | 1.993 | 0.048* | 2,419 | 679,437 |
| *Location Factor* | 71,540,128 | 24,680,609 | 2.899 | 0.004* | 22,712,494 | 120,367,761 |
| *Cost Index (Year)* | 30,119,933 | 30,007,182 | 1.004 | 0.317 | -29,245,688 | 89,485,553 |

Table 21 presents the reduced bridge model (R2 = 0.8866, adjusted R2 = 0.8787, F = 112.91, p < 0.001). Total length (t = 11.772) and deck width (t = 4.223) were the strongest predictors: each additional meter of length adds about ₱630,763 and each meter of width about ₱2,545,124. Foundation type, pile length, span length and location were also significant, while pier height and price year were not.

Substituting the coefficients into the general model gives the reduced working equations, rounded to four significant digits:

***Costbuilding = 20,380 GFA + 8,496 Footprint + 1,261,000 Storeys + 126,300 Span + 234,900***

***FloorHeight + 463,300 Type + 1,404,000 RoofRC + 18,030,000 Location + 25,040,000***

***Year − 46,110,000***

***Costbridge = 630,800 Length + 2,545,000 Width + 274,600 Span − 2,613 PierHeight + 1,314,000 AbutmentHeight + 8,727,000 Foundation + 340,900 PileLength + 71,540,000***

***Location + 30,120,000 Year − 141,300,000***

# Table 22.

*Performance of the Multiple Linear Regression Models under LOOCV*

| **METRIC (LOOCV)** | **BUILDINGS** | **BRIDGES** |
| --- | --- | --- |
| *R-squared* | 0.8112 | 0.8640 |
| *Root Mean Square Error* | ₱4,330,581 | ₱14,021,603 |
| *Mean Absolute Percentage Error* | 13.43% | 65.65% |

Under LOOCV (Table 22), the building model reached an R2 of 0.8112 with a MAPE of 13.43%, within the 13% to 31% range Mahamid (2011) reported for regression models of construction cost. The bridge model explained a similar share of variance (R2 = 0.8640) but its MAPE rose to 65.65%. The linear model fits the large bridges that dominate the variance but badly over-predicts small culverts, where a few million pesos of error is a large

percentage; the negative intercept even pushes some small culverts toward zero or below. Linear regression is therefore a fair baseline for buildings but not for bridges.

# b.) Extreme Gradient Boosting

**Table 23.**

*XGBoost Feature Importance (Gain Share)*

|  |  |  |  |
| --- | --- | --- | --- |
| **FEATURE** | **IMPORTANCE (BUILDINGS)** | **FEATURE** | **IMPORTANCE (BRIDGES)** |
| *Gross Floor Area* | 0.3937 | Superstructure Type Index | 0.8570 |
| *Number of Storeys* | 0.3848 | Foundation Type Index | 0.0428 |
| *Footprint Area* | 0.1010 | Total Length | 0.0383 |
| *Cost Index (Year)* | 0.0264 | Pile Length | 0.0232 |
| *Location Factor* | 0.0260 | Deck Area | 0.0171 |
| *Floor Height* | 0.0210 | Span Length | 0.0145 |
| *Facility Type Index* | 0.0189 | Deck Width | 0.0024 |
| *Structural Span* | 0.0175 | Cost Index (Year) | 0.0015 |
| *RC Roof Deck* | 0.0107 | Abutment Height | 0.0015 |
|  |  | Location Factor | 0.0009 |
|  |  | Pier Height | 0.0007 |

Table 23 shows the share of total gain contributed by each feature. For buildings, gross floor area (0.3937) and storeys (0.3848) account for about 78% of the model's splitting gain. For bridges, superstructure type dominates (0.8570): once the tree knows whether a crossing is a culvert, an RCDG, a PSCG or a truss, most of the cost level is set, and length, foundation and pile length refine it. The tree model thus retains the superstructure type that the linear model had to drop because of collinearity.

# Table 24.

*Performance of the XGBoost Models under LOOCV*

**METRIC (LOOCV) BUILDINGS BRIDGES**

| *R-squared* | 0.7874 | 0.8630 |
| --- | --- | --- |
| *Root Mean Square Error* | ₱4,594,791 | ₱14,070,696 |
| *Mean Absolute Percentage Error* | 13.94% | 19.18% |

Table 24 shows that XGBoost reduced the bridge MAPE from 65.65% to 19.18%, a 71% reduction, with a nearly identical R2 (0.8630). Training on log cost and splitting by superstructure type let it price culverts and long bridges on their own terms. For buildings,

however, XGBoost (MAPE 13.94%, R2 = 0.7874) did slightly worse than linear regression, because building cost in this benchmark is close to linear in floor area and a tree ensemble approximates a straight line with steps. This differs from CORA, where XGBoost outperformed regression on every metric for roads (Buban, 2026), and it supports Elmousalami's (2020) observation that the best model depends on the cost structure of the asset.

# Table 25.

*Comparison of Multiple Linear Regression and XGBoost*

| **ASPECT** | **MULTIPLE LINEAR REGRESSION** | **EXTREME GRADIENT BOOSTING** |
| --- | --- | --- |
| *Buildings: R² / MAPE* | 0.8112 / 13.43% | 0.7874 / 13.94% |
| *Bridges: R² / MAPE* | 0.8640 / 65.65% | 0.8630 / 19.18% |
| *Collinear predictors* | Must be removed (deck area, superstructure) | Retained |
| *Small vs. large projects* | Errors grow on small projects | Log target balances sizes |
| *Explanation* | Coefficients and p-values | SHAP values per project |
| *Role in BUHAY-AH* | Interpretable baseline | Primary expected cost and residual |

Figures 14 and 15 show how each feature drives the XGBoost predictions. Each dot is one project; its position is the SHAP value on the log-cost scale and its color the feature value.

# Figure 14.

*Global SHAP Values of the XGBoost Building Model*

# Figure 15.

*Global SHAP Values of the XGBoost Bridge Model*

For buildings, gross floor area dominates (mean |SHAP| = 0.343 in log cost), far above storeys (0.058) and location (0.035); high floor areas push cost up and small ones pull it down. For bridges the picture is broader: deck area (0.301), pile length (0.257), total length (0.223) and foundation type (0.163) all matter. SHAP also reveals what gain importance

hides: although superstructure type wins most splits, the per-project contributions are spread across size and foundation, which is exactly what an auditor needs to explain a single price. These explanations are shown for every checked project in the application.

# Detection of Over-Budgeted Contracts

The fifth research question measured how well each screening rule finds the 36 contracts with injected overpricing. Table 26 reports the results per asset class and for all 300 projects.

# Table 26.

*Detection Performance against Injected Overpricing*

| **SCOPE AND RULE** | **PRECISIO N** | **RECALL** | **F1** | **AUC** | **TP / FP / FN** |
| --- | --- | --- | --- | --- | --- |
| *Buildings: standards-based rule (above ceiling)* | 1.000 | 0.750 | 0.857 | 1.000 | 15 / 0 / 5 |
| *Buildings: XGBoost residual (> 1.25 × predicted)* | 0.929 | 0.650 | 0.765 | 0.972 | 13 / 1 / 7 |
| *Buildings: Isolation Forest (CORA-style)* | 0.750 | 0.300 | 0.429 | 0.802 | 6 / 2 / 14 |
| *Buildings: BUHAY-AH Risk Index (≥ 30)* | 0.905 | 0.950 | 0.927 | 0.999 | 19 / 2 / 1 |
| *Bridges: standards-based rule (above ceiling)* | 0.517 | 0.938 | 0.667 | 0.982 | 15 / 14 / 1 |
| *Bridges: XGBoost residual (> 1.25 × predicted)* | 0.550 | 0.688 | 0.611 | 0.939 | 11 / 9 / 5 |
| *Bridges: Isolation Forest (CORA-style)* | 0.400 | 0.250 | 0.308 | 0.646 | 4 / 6 / 12 |
| *Bridges: BUHAY-AH Risk Index (≥ 30)* | 0.469 | 0.938 | 0.625 | 0.972 | 15 / 17 / 1 |
| *All projects: standards-based rule (above ceiling)* | 0.682 | 0.833 | 0.750 | 0.994 | 30 / 14 / 6 |
| *All projects: XGBoost residual (> 1.25 × predicted)* | 0.706 | 0.667 | 0.686 | 0.955 | 24 / 10 / 12 |
| *All projects: Isolation Forest (CORA-style)* | 0.556 | 0.278 | 0.370 | 0.731 | 10 / 8 / 26 |
| *All projects: BUHAY-AH Risk Index (≥ 30)* | 0.642 | 0.944 | 0.764 | 0.987 | 34 / 19 / 2 |

Across all projects, the BUHAY-AH Risk Index caught 34 of 36 padded contracts (recall 0.944) with 19 false alarms, for the highest F1-score (0.764). The standards-based rule alone was the strongest single signal: its continuous ratio reached the highest AUC (0.994) and its ceiling rule had good precision (0.682) but missed 6 contracts whose padding stayed under the ceiling. The XGBoost residual rule found 66.7% of the cases; because it learns from prices that include padding, part of the overpricing becomes "normal" to it. The CORA-style Isolation Forest found only 27.8% (AUC 0.731): a padded contract for an ordinary building is not unusual in its plan features, so isolation alone cannot see it. This answers the validation gap that CORA left open and shows why a standards-based reference is needed.

By asset class, buildings were screened almost perfectly (BRI F1 = 0.927, recall 0.950). Bridges kept a high recall (0.938) but lower precision (0.469), because fair bridges with deeper-than-planned piles look over budget against a plan-based estimate. A sensitivity check found that the F1-maximizing threshold is about 24 for buildings (F1 = 0.952) and 58 for bridges (F1 = 0.839), which suggests class-specific thresholds once real data are available. Recall was 90% for moderate and 100% for severe building cases, and 88% and 100% for bridges.

# Figure 16.

*ROC Curves of the Screening Signals, All 300 Projects*

# Table 27.

*Highest-Risk Contracts Flagged by BUHAY-AH*

| **ID** | **PROJECT** | **AWARDED** | **OBR** | **BRI** | **PRIMARY DRIVER** | **INJECTE D** |
| --- | --- | --- | --- | --- | --- | --- |
| SIM-B-143 | 3-storey government office building | ₱56.77M | 1.89 | 97.4 | RC Roof Deck (0/1) | Yes |
| SIM-B-024 | 1-storey public market | ₱48.81M | 1.59 | 97.3 | Footprint Area (mZ) | Yes |
| SIM-B-110 | 2-storey dormitory | ₱24.65M | 1.80 | 93.4 | Over-Budget Ratio (vs. QTO) | Yes |
| SIM-B-035 | 2-storey multi-purpose / evacuation center | ₱46.62M | 1.49 | 91.2 | Floor-to-Floor Height (m) | Yes |
| SIM-B-044 | 1-storey school building | ₱11.04M | 2.00 | 91.1 | Over-Budget Ratio (vs. QTO) | Yes |
| SIM-R-032 | RCDG bridge, 8.4 m (1 span) | ₱16.58M | 1.97 | 95.3 | XGBoost Cost Residual | Yes |
| SIM-R-129 | RCDG bridge, 41.9 m (2 spans) | ₱59.43M | 2.20 | 93.8 | Over-Budget Ratio (vs. QTO) | Yes |

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| SIM-R-049 | RCDG bridge, 12.6 m (1 span) | ₱64.28M | 1.99 | 90.6 | Over-Budget Ratio (vs. QTO) | Yes |
| SIM-R-125 | RCDG bridge, 63.9 m (3 spans) | ₱119.10M | 1.95 | 90.2 | Over-Budget Ratio (vs. QTO) | Yes |
| SIM-R-030 | RCDG bridge, 17.8 m (1 span) | ₱49.07M | 1.97 | 88.1 | Over-Budget Ratio (vs. QTO) | Yes |

Table 27 lists the five highest-risk buildings and bridges. All were injected cases, with over-budget ratios from about 1.5 to 2.2. The primary driver, the input with the largest standardized deviation, was most often the over-budget ratio itself or the XGBoost residual, and occasionally an unusual plan feature such as a reinforced concrete roof deck or a large footprint, which tells a reviewer where to look first. In pesos, the flagged contracts exceeded their ceilings by ₱339.62 million and their standard estimates by ₱656.05 million, against

₱517.25 million of padding injected in total. These amounts illustrate the scale a screening tool can bring to attention; they are not findings about any real contract.

# Extension to Hospitals, Transport Terminals, Airfields and Ports

The sixth research question tested whether the same engine and generator extend to the largest public facilities.

# a.) Design Templates and Space Standards

**Table 28.**

*Extension Design Templates (Albay, 2025 Prices)*

| **DESIGN** | **ST.** | **L × W (m)** | **CAPACITY** | **START** | **STANDAR D** |
| --- | --- | --- | --- | --- | --- |
| Level 1 hospital, 25 beds (2-storey) | 2 | 51.5 × 14.4 | 25 beds | ₱51.01M | ₱64.21M |
| Level 1 hospital, 50 beds (3-storey) | 3 | 50.5 × 14.4 | 50 beds | ₱68.47M | ₱88.57M |
| Level 2 hospital, 100 beds (4-storey) | 4 | 62.5 × 14.4 | 100 beds | ₱112.68M | ₱145.94M |
| Level 3 hospital, 200 beds (5-storey) | 5 | 74.5 × 14.4 | 200 beds | ₱165.27M | ₱210.96M |
| Community airport terminal, 150 peak-hour passengers | 1 | 41.0 × 80.0 | 160 pax | ₱115.64M | ₱145.76M |
| Principal airport terminal, 400 peak-hour passengers (2-storey) | 2 | 43.5 × 80.0 | 400 pax | ₱235.14M | ₱298.31M |
| International airport terminal, 1,000 peak-hour passengers (2-storey) | 2 | 92.5 × 80.0 | 1040 pax | ₱502.32M | ₱635.39M |
| Seaport passenger terminal, 120 passengers | 1 | 31.0 × 30.0 | 120 pax | ₱28.65M | ₱35.10M |
| Seaport passenger terminal, 360 passengers | 1 | 48.0 × 30.0 | 360 pax | ₱45.49M | ₱55.42M |
| Seaport passenger terminal, 900 passengers (2-storey) | 2 | 59.5 × 30.0 | 960 pax | ₱103.18M | ₱126.67M |
| Jeepney terminal, 20 loading bays | 1 | 35.0 × 20.0 | 20 bays | ₱28.08M | ₱31.14M |
| UV Express terminal, 15 loading bays | 1 | 31.0 × 20.0 | 15 bays | ₱20.45M | ₱22.98M |
| Bus terminal, 12 sawtooth bays | 1 | 55.0 × 20.0 | 12 bays | ₱37.12M | ₱41.47M |
| Integrated land transport terminal: 8 bus + 16 jeepney<br>+ 12 UV Express bays (2-storey) | 2 | 56.5 × 20.0 | 36 bays | ₱64.62M | ₱72.68M |

Table 28 lists the 14 new building templates; all 58 of their 58 checks passed, bringing the library to 55 building, 13 bridge, 7 airfield and 5 port designs with 210 of 210 checks passed. A 100-bed Level 2 hospital came to about ₱40,000 per mZ, airport terminals to about ₱44,000 per mZ, and a 20-bay jeepney terminal to about ₱1.6 million per bay.

# Figure 17.

*Generated Ground Floor of a 100-Bed Level 2 Hospital*

# Figure 18.

*Integrated Land Transport Terminal with Jeepney, UV Express and Bus Bays*

# Figure 19.

*Generated Plan of a 1,200 × 30 m Turboprop Runway*

# Figure 20.

*Generated Section of a 60 × 15 m RoRo Pier on PC Spun Piles*

# Table 29.

*Airfield and Port Templates*

| **DESIGN** | **START** | **STANDARD** | **CEILING** | **PER UNIT** |
| --- | --- | --- | --- | --- |
| Runway 800 × 23 m (small aircraft, PCC) | ₱111.87M | ₱117.12M | ₱134.89M | ₱6,365 / mZ pavement |
| Runway 1,200 × 30 m (turboprop, PCC) | ₱240.15M | ₱249.30M | ₱283.25M | ₱6,925 / mZ pavement |
| Runway extension 400 × 30 m (turboprop) | ₱86.32M | ₱90.32M | ₱103.91M | ₱7,526 / mZ pavement |
| Runway 2,100 × 45 m (A320 / B737, PCC) | ₱755.51M | ₱778.63M | ₱874.56M | ₱8,240 / mZ pavement |
| Parallel taxiway 600 × 15 m (turboprop) | ₱73.57M | ₱77.22M | ₱89.26M | ₱8,579 / mZ pavement |
| Apron, 4 turboprop stands (120 × 80 m) | ₱61.74M | ₱63.60M | ₱73.27M | ₱6,625 / mZ pavement |
| Apron, 3 jet stands (150 × 90 m) | ₱103.38M | ₱107.71M | ₱123.00M | ₱7,978 / mZ pavement |
| Passenger jetty 30 × 6 m (PC spun piles) | ₱27.53M | ₱30.40M | ₱37.30M | ₱168,902 / mZ deck |
| Fishport pier 40 × 8 m with 80 m causeway | ₱65.73M | ₱70.01M | ₱82.20M | ₱218,791 / mZ deck |
| RoRo pier 60 × 15 m with ramp (PC spun piles) | ₱108.31M | ₱116.14M | ₱136.92M | ₱129,042 / mZ deck |
| Marginal wharf 100 × 20 m (steel pipe piles) | ₱302.48M | ₱315.00M | ₱357.79M | ₱157,498 / mZ deck |
| Wharf extension 50 × 20 m (steel pipe piles) | ₱160.83M | ₱167.56M | ₱187.15M | ₱167,557 / mZ deck |

Budget-to-design also works for the new usages: ₱150 million buys a 185-beds hospital (doh level 1–3) in 4 storeys; ₱300 million buys a 300-beds hospital (doh level 1–3)

in 5 storeys; ₱300 million buys a 500-passengers airport passenger terminal in 2 storeys; ₱60 million buys a 480-passengers seaport passenger terminal in 1 storey; ₱40 million buys a 12-bus bays bus terminal in 1 storey. Each search took a median of 2.9 ms.

# b.) Accuracy of the Standard Estimate

**Table 30.**

*Accuracy and Standards-Based Detection on SBD-EXT*

| **CLASS** | **n** | **MAPE** | **R²** | **LEAN ≤ AWARD** | **CEILING COVERS** | **PREC.** | **RECAL L** | **F1** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| *Hospitals* | 30 | 8.30% | 0.8992 | 100.0% | 100.0% | 1.000 | 1.000 | 1.000 |
| *Airport terminals* | 20 | 6.17% | 0.9748 | 100.0% | 100.0% | 1.000 | 1.000 | 1.000 |
| *Seaport terminals* | 20 | 7.09% | 0.9216 | 94.4% | 100.0% | 1.000 | 1.000 | 1.000 |
| *Land transport terminals* | 40 | 4.50% | 0.9733 | 100.0% | 100.0% | 1.000 | 0.833 | 0.909 |
| *Airfield pavements* | 35 | 5.43% | 0.9858 | 62.1% | 96.6% | 0.857 | 1.000 | 0.923 |
| *Port structures* | 35 | 7.50% | 0.9527 | 87.5% | 81.2% | 0.333 | 1.000 | 0.500 |
| *All extension projects* | 180 | 6.40% | 0.9863 | 89.9% | 95.6% | 0.750 | 0.955 | 0.840 |

Against fair awarded costs, the standard estimate reached a MAPE of 6.40% and R2 = 0.9863 across the extension, from 4.50% for land transport terminals to 8.30% for hospitals, whose mechanical and medical systems vary most. The lean start quotation was at or below the fair award in 89.9% of projects and the ceiling covered 95.6%.

# c.) Detection by the Standards-Based Rule

The rule caught 21 of 22 padded contracts (recall 0.955, precision 0.750, AUC 0.998); the extension risk index at 30 caught all 22 with precision 0.733. Most false alarms were port structures, where unseen pile penetration raises the true cost, the same pattern as bridge piles in SBD-300.

# Figure 21.

*Accuracy and Detection by Extension Class (SBD-EXT)*

# Deployment of BUHAY-AH as a Mobile Application and Download Website

The seventh research question concerned how the system reaches its users. BUHAY-AH was deployed as an installable mobile application with five screens (Home, Design, Quote, Check and Library), an Android package, an offline ZIP package and a download website.

# a.) Mobile Application with Design Studio

**Figure 22.**

*Home Screen of the BUHAY-AH Application*

The home screen shows the current plan as a 3D model with its start quotation and standard estimate and offers four actions: design from a budget, open the design templates, quote a plan and check a contract. A strip of templates from the design library invites users who have no blueprint yet.

# Figure 23.

*Design Studio with the Template Library*

The Design screen opens on the template library. Filter chips narrow the 80 designs by facility type, including hospitals, transport terminals, airfields and ports, and each card shows a floor-plan thumbnail, the capacity, storeys, dimensions, floor area and both quotations.

# Figure 24.

*Design Editor with Floor Plan, Spaces, Standards Checks and 3D Model*

Opening a design shows the editor. The user renames the design, switches floors, adds or removes spaces with plus and minus buttons, adds any library space, adds a whole template or saved design as a wing, and changes storeys, layout, corridor width and roof. The plan, capacity, quotations, standards checks and 3D model update on every change. *Quote this design* sends the plan variables to the Quote screen, *Save design* stores it for reuse, and the floor plan can be exported as an SVG drawing.

# Figure 25.

*Design from a Budget*

In Budget mode the user enters the facility, the money available, the price basis, the storey limit and the longest building the lot allows. The Pareto-efficient designs appear as cards with their capacity, cost, share of the budget and cost per classroom, bed, staff, person or stall; the largest design is highlighted.

# Figure 26.

*Bridge Designer Comparing Superstructures for a 45 m Gap*

The bridge designer takes the gap, traffic lanes, pier and abutment heights, pile length and an optional budget, draws the elevation of the lowest-cost design and lists every option with its start and standard prices per meter.

# Figure 27.

*Quote Screen with the Three Quotation Tiers and the ABC*

On the Quote screen, the user picks a reference or saved plan, imports a DXF or plan file, or types the plan variables. The three tiers update as the user types, with the lean start quotation highlighted. Beside the 3D model, the ABC is broken down into estimated direct cost, OCM, profit and VAT, and the XGBoost expectation with its 80% band is shown as a second opinion.

# Figure 28.

*Bill of Quantities Generated from the Plan*

The bill of quantities lists every pay item with its quantity, unit, unit cost and amount, grouped into DPWH parts with subtotals. It can be exported as CSV for spreadsheets, the plan can be saved or exported as a plan file, and the quotation can be printed to PDF.

# Figure 29.

*Plan Panel after Importing the Sample DXF Floor Plan*

Importing the sample DXF plan of a two-classroom school building read an outline of 171 mZ, a perimeter of 55 m and 25 m of interior walls, which the engine used in place of a rectangular estimate.

# Figure 30.

*Check Screen Screening a Padded Contract*

On the Check screen, the user enters the contract amount. The verdict shows the risk index on a gauge, a range strip places the amount against the lean, standard and ceiling estimates and the model's band, and four metrics give the over-budget ratio, the model ratio, the anomaly score and the risk index. In the example, an amount 60% above the standard estimate was flagged with a risk index above 80. The SHAP panel explains the expected cost, the ABC markup checker tests submitted OCM, profit and VAT rates against the DPWH caps, and a note reminds users that a flag calls for review by the implementing office, COA, the Ombudsman or the ICI.

# Figure 31.

*Line-Item Check of a Contractor's Bill of Quantities*

The line-item check compares each unit cost in a contractor's bill of quantities with the BUHAY-AH all-in rate (direct rate × location × OCM, profit and VAT). Items more than 25% above the rate are marked overpriced and their excess over a 10% tolerance is totalled, so that a reviewer sees which items carry the padding.

# Figure 32.

*Library Screen with Reference Plans, Saved Designs and the Unit Price Book*

The Library holds the reference plans, the user's saved plans, designs and checks, and the editable unit price book, where an implementing office can load its own rates so that every design and quotation follows them.

# b.) Download Website

**Figure 33.**

*Download Website of BUHAY-AH*

The download website introduces BUHAY-AH, explains the four-step method and presents a live quotation computed in the browser by the same engine.

# Figure 34.

*Live Budget-to-Design Demonstration on the Website*

Its design section runs the budget-to-design search in the visitor's browser: moving the budget slider redraws the Pareto-efficient designs with their plans and prices, followed by a gallery of library designs.

# Figure 35.

*Download Section of the Website*

The download section links to the Android package, the installable web application, the offline package, the sample plan, the research paper and its presentation materials.

# c.) Floor Plans, Parametric 3D Visualization and SHAP Explanations

**Figure 36.**

*Parametric 3D Model of a 2-Storey 4-Classroom School Building*

# Figure 37.

*Parametric 3D Model of a Three-Span RCDG Bridge*

# Figure 38.

*Parametric 3D Model of a 50 m Steel Truss Bridge*

The 3D models are drawn from the engine's geometry: the school building shows its column grid, slabs, window bands and gable roof; the RCDG bridge shows four girder lines on two piers between abutments; and the truss bridge shows its panels and chords. Because the floor plans and models follow the plan variables, a change in spaces, storeys, spans or girders is visible at once, and the tint shows the screening result. Together with the SHAP panel, they let non-engineers see what they are paying for and why the expected cost is what it is.

# CONCLUSION

In pursuit of developing a budget-to-blueprint design generator, standards-based quantity take-off and hybrid machine-learning system for start quotations and over-budget detection in public buildings and bridges, the study concludes the following:

1. Nine plan variables for buildings (gross floor area, footprint, storeys, span, floor height, facility type, roof system, location factor and cost index) and eleven for bridges (total length, deck width, deck area, span length, pier and abutment heights, superstructure and foundation types, pile length, location factor and cost index) can be read from plans and standards and are sufficient to price a project. Bridge sizes and costs varied far more than building sizes and costs, with contracts from ₱1.00 million to ₱179.23 million.
2. Schematic designs can be generated without a blueprint. 55 space modules on DepEd, DOH, NBC and DSWD norms produced 41 building and 13 bridge templates that can be edited, saved and combined; every template passed all 152 space and safety checks; and the exhaustive budget-to-design search returned the Pareto-efficient designs for a budget in a median of 3.6 ms, adding up to 10 classrooms over a single-storey policy for the same school budget.
3. The standards-based engine produced itemized lean, standard and ceiling quotations that came within a MAPE of 5.21% for buildings and 7.67% for bridges of fair awarded costs in the benchmark, less than half the error of the best data-driven model. The lean start quotation averaged 14.4% below the standard estimate for buildings and 5.9% for bridges while keeping code minimums.
4. **a.) Multiple Linear Regression:** no building predictor exceeded a VIF of 10, while deck area and superstructure type were removed from the bridge model. Under LOOCV, the building model reached R2 = 0.8112 and MAPE = 13.43%,

and the bridge model R2 = 0.8640 and MAPE = 65.65%. **b.) XGBoost:** the model reached R2 = 0.7874 and MAPE = 13.94% for buildings and R2 = 0.8630 and MAPE = 19.18% for bridges, a large gain on bridges and a small loss on buildings, so the better model depends on the asset class.

5. The BUHAY-AH Risk Index detected 94.4% of injected overpricing with an F1-score of 0.764 and an AUC of 0.987, the best balance among the four rules. The standards-based ratio was the strongest single signal, the XGBoost residual partly absorbed padding from its training data, and an Isolation Forest alone found only 27.8%. These flags identify contracts for review and do not establish irregularity, error or fraud.
6. The engine and generator extend to hospitals, airport, seaport and land transport terminals, runways and piers: 14 new templates passed all 58 checks, the standard estimate reached 6.40% MAPE on SBD-EXT, and the standards rule caught 95.5% of padded contracts without the machine-learning layer.
7. BUHAY-AH was deployed as an installable offline-capable mobile application, an Android package, an offline ZIP package and a download website, integrating the design studio, plan import, itemized quotations, floor plans, parametric 3D models, SHAP explanations, line-item checks and over-budget screening that run entirely on the user's device.

**Limitations.** All accuracy and detection figures come from simulated benchmarks, unit costs are indicative 2025 Bicol rates, designs are schematic, and the extension types are screened without the trained models. Extending the results needs real contract records, site data and professional review.

# RECOMMENDATIONS

Based on these findings, the researcher recommends the following:

1. **Validate on actual contracts.** Replace the simulated benchmark with completed DPWH building and bridge contracts from the DPWH Transparency Portal, PhilGEPS and COA reports, including their programs of works, and re-estimate the accuracy and detection figures.
2. **Review the design library with licensed professionals.** Compare the templates with DepEd and DPWH standard plans, have architects and engineers refine module sizes, and add site inputs such as lot shape, orientation and setbacks.
3. **Add geotechnical data for bridges.** Since unseen pile lengths caused most false alarms, include borehole logs and design pile tips in the plan input, or widen the bridge ceiling by a site-class allowance.
4. **Connect current price data.** Load regional DPWH unit costs and the PSA construction materials price indices automatically so the price book stays current.
5. **Calibrate thresholds by asset class.** Set separate BUHAY-AH Risk Index thresholds for buildings and bridges, about 24 and 58 in the benchmark, once real cases are confirmed.
6. **Extend plan import and design.** Read IFC building information models and scanned PDF plans, and add hydraulic criteria to the bridge designer so that span choices reflect flood levels and debris.
7. **Train the models for the extension types.** Retrain XGBoost and the Isolation Forest once hospital, terminal, airfield and port contracts are collected, and add pavement and port geotechnical data.
8. **Extend to other project types.** Apply the same engine to flood-control structures, water systems and roads, joining CORA and BUHAY-AH in one screening tool.
9. **Pilot with oversight bodies and publish open data.** Test BUHAY-AH with a district engineering office, COA auditors and a local government, run a usability

study, and publish screened records following the Open Contracting Data Standard and the CoST Infrastructure Data Standard.

# REFERENCES

Association of Structural Engineers of the Philippines. (2016). *National structural code of the Philippines 2015: Volume I, buildings, towers and other vertical structures* (7th ed.).

Buban, E. M. C. (2026). *CORA: Computational outlier recognition and analytics for road construction cost prediction and potential anomaly detection via a hybrid machine learning system* \[Unpublished research paper].

Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785–794). [https://doi.org/10.1145/2939672.2939785](https://doi.org/10.1145/2939672.2939785)

Department of Public Works and Highways. (2013). *DPWH standard specifications for highways, bridges and airports* (Vol. II).

Department of Public Works and Highways. (2016). *Department Order No. 197, series of 2016: Guidelines on the preparation of the approved budget for the contract*.

Department of Public Works and Highways. (2021). *Department Order No. 42, series of 2021: Adoption of the DPWH standard specifications for public works structures, Volume III, 2019 edition*.

Department of Public Works and Highways. (2025). *Department Order No. 30, series of 2025*. Federal Aviation Administration. (2021). *Airport pavement design and evaluation* (Advisory Circular

150/5320-6G). U.S. Department of Transportation.

International Civil Aviation Organization. (2022). *Annex 14 to the Convention on International Civil Aviation: Aerodromes, Volume I — Aerodrome design and operations* (9th ed.).

Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation forest. In *2008 Eighth IEEE International Conference on Data Mining* (pp. 413–422). IEEE. [https://doi.org/10.1109/ICDM.2008.17](https://doi.org/10.1109/ICDM.2008.17)

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems, 30*. [https://arxiv.org/abs/1705.07874](https://arxiv.org/abs/1705.07874)

Lundberg, S. M., Erion, G. G., & Lee, S.-I. (2018). *Consistent individualized feature attribution for tree ensembles* (arXiv:1802.03888). [https://arxiv.org/abs/1802.03888](https://arxiv.org/abs/1802.03888)

Overseas Coastal Area Development Institute of Japan. (2009). *Technical standards and commentaries for port and harbour facilities in Japan*.

Shapley, L. S. (1953). A value for n-person games. In H. W. Kuhn & A. W. Tucker (Eds.),

*Contributions to the theory of games* (Vol. 2, pp. 307–317). Princeton University Press.

Transparency International. (2026). *Corruption perceptions index 2025*. [https://www.transparency.org/en/cpi/2025](https://www.transparency.org/en/cpi/2025)

U.S. Government Accountability Office. (2020). *Cost estimating and assessment guide: Best practices for developing and managing program costs* (GAO-20-195G).

# APPENDICES

# Appendix A. Sample Records of the Simulated Benchmark Dataset (SBD-300)

| **ID** | **PROVINCE** | **YEAR** | **PLAN** | **STANDA RD (₱M)** | **AWARDE D (₱M)** | **INJECTE D** |
| --- | --- | --- | --- | --- | --- | --- |
| SIM-B-001 | Sorsogon | 2023 | 2-st school, 27.0×9.1 m | 13.74 | 13.53 | No |
| SIM-B-002 | Camarines Sur | 2022 | 1-st market, 40.9×19.7 m | 20.57 | 19.03 | No |

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| SIM-B-003 | Camarines Sur | 2024 | 1-st health, 30.8×8.2 m | 9.78 | 9.48 | No |
| SIM-B-004 | Masbate | 2024 | 2-st school, 45.0×9.8 m | 23.77 | 22.11 | No |
| SIM-B-005 | Masbate | 2022 | 2-st school, 27.0×9.5 m | 14.71 | 16.00 | No |
| SIM-B-006 | Camarines Sur | 2024 | 2-st evacuation, 31.9×12.8 m | 19.00 | 31.25 | Yes |
| SIM-B-007 | Camarines Sur | 2023 | 1-st office, 15.6×14.0 m | 6.77 | 8.55 | Yes |
| SIM-B-008 | Masbate | 2025 | 2-st school, 27.0×8.8 m | 14.27 | 14.29 | No |
| SIM-B-009 | Albay | 2025 | 3-st school, 36.0×9.1 m | 25.21 | 25.34 | No |
| SIM-B-010 | Catanduanes | 2024 | 1-st evacuation, 26.4×14.9 m | 12.21 | 11.97 | No |
| SIM-R-001 | Catanduanes | 2022 | box_culvert, 2.5 m, 1 span(s) | 1.51 | 1.42 | No |
| SIM-R-002 | Camarines Sur | 2024 | pscg, 79.3 m, 3 span(s) | 67.59 | 69.05 | No |
| SIM-R-003 | Camarines Sur | 2022 | rcdg, 18.1 m, 1 span(s) | 10.20 | 10.48 | No |
| SIM-R-004 | Masbate | 2022 | pscg, 111.9 m, 4 span(s) | 103.52 | 110.73 | No |
| SIM-R-005 | Masbate | 2022 | pscg, 28.6 m, 1 span(s) | 46.97 | 45.09 | No |
| SIM-R-006 | Camarines Sur | 2022 | rcdg, 36.8 m, 2 span(s) | 28.98 | 35.83 | Yes |
| SIM-R-007 | Albay | 2023 | rcdg, 24 m, 2 span(s) | 26.68 | 26.15 | No |
| SIM-R-008 | Albay | 2022 | pscg, 111.8 m, 3 span(s) | 87.78 | 123.09 | Yes |

*The full dataset (300 records, 40 columns) is in research/data/buhay\_sbd300.csv.*

# Appendix B. BUHAY-AH Unit Price Book (Direct Costs, Bicol Region V, 2025)

|  |  |  |  |
| --- | --- | --- | --- |
| **PAY ITEM** | **DESCRIPTION** | **UNIT** | **RATE (₱)** |
| B.9 | Mobilization / demobilization | l.s. | allowance / % |
| B.7 (1) | Occupational safety & health program | l.s. | allowance / % |
| B.5 | Project billboard / signboard | each | 7,500 |
| B.8 | Traffic management & detour | l.s. | allowance / % |
| B.3 | Survey, staking, testing & as-built plans | l.s. | allowance / % |
| 800 (3) | Clearing and grubbing | mZ | 45 |
| 803 (1)a | Structure excavation, common soil | m3 | 380 |
| 804 (1)a | Backfill from structure excavation, compacted | m3 | 260 |
| 804 (4) | Gravel fill / bedding, compacted | m3 | 1,550 |
| 1000 (1) | Soil poisoning (termite control) | mZ | 65 |
| 900 (1)c | Structural concrete, fc′ 20.7 MPa (3000 psi), 28 days | m3 | 7,900 |
| 900 (1)b | Concrete slab on grade, fc′ 17.2 MPa (2500 psi) | m3 | 7,200 |
| 902 (1) | Reinforcing steel bars, deformed, Gr. 40/60, incl. tie wire | kg | 82 |
| 903 (2) | Formworks and falseworks | mZ | 850 |
| 1046 (3) | CHB masonry 150 mm, reinforced & grouted (exterior) | mZ | 1,080 |
| 1046 (2) | CHB masonry 100 mm (partitions) | mZ | 880 |
| 1027 (1) | Cement plaster finish | mZ | 360 |
| 1032 (1) | Painting works, masonry/concrete (acrylic, 3 coats) | mZ | 230 |
| 1047 (3) | Structural steel trusses & purlins, fabricated & installed | kg | 140 |
| 1013 (2) | Pre-painted long-span metal roofing 0.50 mm, incl. accessories | mZ | 760 |
| 1013 (5) | Gutters, flashing & downspouts | m | 950 |
| — | Waterproofing membrane, RC roof deck | mZ | 480 |
| — | Ceiling: fiber-cement board on metal furring | mZ | 1,050 |
| 1018 (2) | Ceramic floor tiles 600 × 600 mm | mZ | 1,180 |
| — | Cement floor topping, steel-trowel finish | mZ | 320 |
| — | Porcelain / granite floor tiles (premium) | mZ | 1,650 |
| 1010 | Doors complete with jamb & hardware | set | 13,500 |
| 1008 (1) | Aluminum-framed glass windows | mZ | 6,200 |
| 1100–1200 | Electrical works (conduits, wires, devices, panel, fixtures) | mZ | allowance / % |
| 1001–1002 | Plumbing & sanitary works incl. fixtures | mZ | allowance / % |
| — | Fire protection & detection (RA 9514) | mZ | allowance / % |
| — | Mechanical / air-conditioning works | mZ | allowance / % |
| — | RC septic tank / sewage treatment | unit | allowance / % |
| — | Accessibility ramp & handrails (BP 344) | unit | 38,000 |
| 1047 (5) | Steel railings — corridors, balconies & stairs | m | 4,800 |
| — | Roof insulation, fascia & eaves soffit | mZ | 420 |
| — | Perimeter drainage canal with grating | m | 1,450 |
| 100 (1) | Clearing and grubbing | mZ | 55 |
| 103 (1)a | Structure excavation, common soil | m3 | 420 |
| 103 (2) | Structure excavation below water, incl. dewatering | m3 | 680 |
| — | Cofferdam / sheet piling | each | 180,000 |
| 104 (2) | Structural backfill, granular, compacted | m3 | 950 |
| — | Gravel bedding | m3 | 1,550 |
| 400 (11) | Precast RC piles 450 × 450 mm, furnished & driven | m | 11,500 |
| 400 (17) | Bored piles 1.0 m Ø, drilling incl. temporary casing | m | 28,000 |
| 400 (20) | Pile dynamic load test (PDA) | test | 85,000 |
| 405 (1)a | Structural concrete Class A — deck & girders, incl. forms | m3 | 13,500 |
| 405 (1)b | Structural concrete Class A — abutments, piers, walls, incl. forms | m3 | 11,200 |
| 405 (1)c | Structural concrete Class A — footings, pile caps, approach slabs | m3 | 9,400 |
| 405 (1)d | Structural concrete for bored piles (tremie) | m3 | 9,200 |

|  |  |  |  |
| --- | --- | --- | --- |
| 405 (2) | Lean concrete / seal concrete | m3 | 6,800 |
| 404 (1) | Reinforcing steel Gr. 60, incl. tie wire | kg | 84 |
| 406 (1)a | Precast PSC girder AASHTO Type III — supply, fabricate, launch | m | 34,000 |
| 406 (1)b | Precast PSC girder AASHTO Type IV — supply, fabricate, launch | m | 42,000 |
| 406 (1)c | Precast PSC bulb-tee girder BT-1600 — supply, fabricate, launch | m | 52,000 |
| 403 (1) | Structural steel, fabricated, painted & erected | kg | 210 |
| 412 (1) | Elastomeric bearing pads | pc | 16,500 |
| 412 (3) | Pot / spherical bearings (steel spans) | pc | 95,000 |
| — | Expansion joint, strip-seal type | m | 26,000 |
| 401 (1) | Steel bridge railing | m | 6,200 |
| 401 (2) | Concrete barrier railing | m | 9,800 |
| — | Deck drains / scuppers | pc | 2,200 |
| 505 (2) | Grouted riprap, Class A (slope protection) | m3 | 3,100 |
| 310 | Asphalt wearing course 50 mm | mZ | 640 |
| 311 + 201 | PCCP 230 mm on aggregate base (approaches) | mZ | 3,650 |

# Appendix C. Bill of Quantities of a 2-Storey 4-Classroom School Building (Standard Tier, Albay, 2025)

| **ITEM** | **DESCRIPTION** | **QTY** | **UNIT** | **UNIT COST** | **AMOUNT (₱)** |
| --- | --- | --- | --- | --- | --- |
| 800 (3) | Clearing and grubbing | 273.60 | mZ | 45.00 | 12,312.00 |
| 803 (1)a | Structure excavation, common soil | 179.28 | m3 | 380.00 | 68,126.40 |
| 804 (1)a | Backfill from structure excavation, compacted | 155.11 | m3 | 260.00 | 40,329.90 |
| 804 (4) | Gravel fill / bedding, compacted | 21.96 | m3 | 1,550.00 | 34,038.00 |
| 1000 (1) | Soil poisoning (termite control) | 171.00 | mZ | 65.00 | 11,115.00 |
| — | Perimeter drainage canal with grating | 63.00 | m | 1,450.00 | 91,350.00 |
| 900 (1)c | Structural concrete fc′ 20.7 MPa — footings (15 @ 1.6 × 1.6 ×<br>0.45 m) | 17.28 | m3 | 7,900.00 | 136,512.00 |
| 900 (1)c | Structural concrete fc′ 20.7 MPa — columns 300 × 300 mm & pedestals | 10.67 | m3 | 7,900.00 | 84,253.50 |
| 900 (1)c | Structural concrete fc′ 20.7 MPa — beams 250 × 400 mm & tie beams | 27.28 | m3 | 7,900.00 | 215,497.19 |
| 900 (1)c | Structural concrete fc′ 20.7 MPa — suspended slabs 125 mm | 21.38 | m3 | 7,900.00 | 168,862.50 |
| 900 (1)c | Structural concrete fc′ 20.7 MPa — stairs (1 flight set) | 4.20 | m3 | 7,900.00 | 33,180.00 |
| 900 (1)b | Concrete slab on grade 100 mm, fc′ 17.2 MPa | 17.10 | m3 | 7,200.00 | 123,120.00 |
| 902 (1) | Reinforcing steel bars, deformed, Gr. 40/60, incl. tie wire | 11,627.09 | kg | 82.00 | 953,421.69 |
| 903 (2) | Formworks and falseworks | 654.78 | mZ | 850.00 | 556,558.75 |
| 1046 (3) | CHB masonry 150 mm, reinforced & grouted (exterior) | 215.88 | mZ | 1,080.00 | 233,150.40 |
| 1046 (2) | CHB masonry 100 mm (partitions) | 75.90 | mZ | 880.00 | 66,794.11 |
| 1027 (1) | Cement plaster finish | 641.92 | mZ | 360.00 | 231,091.66 |
| 1032 (1) | Painting works, masonry/concrete (acrylic, 3 coats) | 966.82 | mZ | 230.00 | 222,368.89 |
| 1047 (3) | Structural steel trusses & purlins, fabricated & installed | 4,727.29 | kg | 140.00 | 661,820.99 |
| 1013 (2) | Pre-painted long-span metal roofing 0.50 mm, incl. accessories | 247.02 | mZ | 760.00 | 187,732.82 |
| 1013 (5) | Gutters, flashing & downspouts | 63.60 | m | 950.00 | 60,420.00 |
| — | Roof insulation, fascia & eaves soffit | 247.02 | mZ | 420.00 | 103,747.08 |
| 1047 (5) | Steel railings — corridors, balconies & stairs | 27.00 | m | 4,800.00 | 129,600.00 |
| — | Ceiling: fiber-cement board on metal furring | 324.90 | mZ | 1,050.00 | 341,145.00 |
| 1018 (2) | Ceramic floor tiles 600 × 600 mm | 314.64 | mZ | 1,180.00 | 371,275.20 |
| 1010 | Doors complete with jamb & hardware | 14.00 | set | 13,500.00 | 189,000.00 |
| 1008 (1) | Aluminum-framed glass windows | 77.00 | mZ | 6,200.00 | 477,400.00 |
| 1100–1200 | Electrical works (conduits, wires, devices, panel, fixtures) | 342.00 | mZ | 1,600.00 | 547,200.00 |
| 1001–1002 | Plumbing & sanitary works incl. fixtures | 342.00 | mZ | 1,400.00 | 478,800.00 |
| — | Fire extinguishers, alarm & detection (RA 9514) | 342.00 | mZ | 120.00 | 41,040.00 |
| — | RC septic tank / sewage treatment | 1.00 | unit | 75,390.00 | 75,390.00 |
| — | Accessibility ramp & handrails (BP 344) | 1.00 | unit | 38,000.00 | 38,000.00 |
| B.9 | Mobilization / demobilization | 1.00 | l.s. | 83,815.84 | 83,815.84 |
| B.7 (1) | Occupational safety & health program | 1.00 | l.s. | 104,769.80 | 104,769.80 |
| B.5 | Project billboard / signboard | 2.00 | each | 7,500.00 | 15,000.00 |
| B.3 | Survey, staking, testing & as-built plans | 1.00 | l.s. | 34,923.27 | 34,923.27 |
|  | Estimated direct cost |  |  |  | 7,223,161.99 |
|  | OCM (12%) |  |  |  | 866,779.44 |
|  | Profit (8%) |  |  |  | 577,852.96 |
|  | VAT (5%) |  |  |  | 433,389.72 |
|  | **Approved Budget for the Contract** |  |  |  | **9,101,184.11** |

**Appendix D. Cost Summary of a Three-Span RCDG Bridge (3 × 20 m, Albay, 2025)**

| **PART** | **AMOUNT (₱)** |
| --- | --- |
| Part A — General requirements | 1,420,448.82 |
| Part B — Earthworks & protection | 1,667,632.45 |
| Part C — Foundation & piling | 11,775,513.00 |
| Part D — Substructure | 5,108,433.19 |
| Part E — Superstructure | 11,186,585.90 |
| Part F — Deck, railings & approaches | 2,203,854.00 |
| Estimated direct cost | 33,362,467.36 |
| Lean start quotation (ABC) | 39,068,313.24 |
| Standard fair estimate (ABC) | 42,036,708.87 |
| Ceiling (ABC) | 50,122,187.05 |

# Appendix E. Snippets of Methodology (Quantity Take-Off Engine, JavaScript)

// footings (isolated, sized from service load and allowable bearing) var Pcol = 0.75 * sx * sy * N * bt.w; // kN

var B = Math.max(1.0, ceilTo(Math.sqrt(Pcol / p.soilBearing), 0.1)); var tf = Math.max(0.30, ceilTo(0.25 + 0.10 * B, 0.05));

var V = {}, F = {}, K = {};

V.footing = nCol * B * B * tf * cf; V.pedestal = nCol * colB * colB * Df * cf; V.column = nCol * N * colB * colB * h * cf;

var slabLevels = N - 1 + (p.roof === 'rc_deck' ? 1 : 0);

V.beam = (slabLevels * beamLen * beamB * (beamD - ts) + (p.roof === 'rc_deck' ? 0 : beamLen * beamB * beamD)) * cf

V.tiebeam = beamLen * 0.25 * 0.40 * cf; V.slab = slabLevels * A * ts * cf;

var nStairs = N > 1 ? (A > 250 ? 2 : 1) : 0; V.stair = nStairs * (N - 1) * 4.2 * cf; V.sog = A * 0.10;

// reinforcement intensities, kg per ms (standard tier, seismic zone 4) K.footing = V.footing * 90 * rf; K.pedestal = V.pedestal * 210 * rf; K.column =

V.column * 220 * rf;

K.beam = V.beam * 190 * rf; K.tiebeam = V.tiebeam * 140 * rf; K.slab = V.slab * 100

\* rf;

K.stair = V.stair * 100 * rf; K.sog = V.sog * 30 * rf;

function indirect(edc, settings) { settings = settings || {};

var row = INDIRECT_TABLE.filter(function (r) { return edc <= r.upTo; })\[0]; var ocmR = settings.ocm != null ? settings.ocm : row.ocm;

var prR = settings.profit != null ? settings.profit : row.profit; var vatR = settings.vat != null ? settings.vat : VAT_RATE;

var ocm = edc * ocmR, profit = edc * prR, vat = (edc + ocm + profit) * vatR;

return { edc: edc, ocmRate: ocmR, profitRate: prR, vatRate: vatR, ocm: ocm, profit: profit, vat: vat, total: edc +

}

# Appendix F. Snippets of Methodology (Model Training, Python)

\# ---- 2. XGBoost (log target), tuned then LOOCV ylog = np.log(y)

scorer = make_scorer(lambda yt, yp: mean_absolute_percentage_error(np.exp(yt), np.exp(yp)), greater_is_better=Fals

search = RandomizedSearchCV(XGBRegressor(objective='reg:squarederror', random_state=42, n_jobs=4), PARAMS, n_iter=

scoring=scorer, cv=KFold(5, shuffle=True, random_state=42), random_state=42, n_jobs=1)

search.fit(X, ylog)

best = search.best_params_

R\['xgb_params'] = {k: (float(v) if isinstance(v, float) else int(v)) for k, v in best.items()}

xgb_pred = np.exp(cross_val_predict(XGBRegressor(objective='reg:squarederror', random_state=42, n_jobs=4, **best),

R\['xgb_loocv'] = metrics(y, xgb_pred)

final = XGBRegressor(objective='reg:squarederror', random_state=42, n_jobs=4,

\**best).fit(X, ylog)

imp = final.get_booster().get_score(importance_type='gain') tot = sum(imp.values())

R\['xgb_importance'] = {f: float(imp.get(f, 0) / tot) for f in feats}

\# ---- 3. Isolation Forest

obr = y / d.fair_estimate.values

ceil_ratio = d.ceiling_estimate.values / d.fair_estimate.values ml_ratio = y / xgb_pred

Z = X.copy(); Z\['LogMLRatio'] = np.log(ml_ratio); Z\['LogOBR'] = np.log(obr) scaler = StandardScaler().fit(Z.astype(float))

Zs = scaler.transform(Z.astype(float))

iso = IsolationForest(n_estimators=200, contamination=0.10, random_state=42).fit(Zs) iso_score = -iso.score_samples(Zs) # 0..1, higher = easier to isolate iso_raw = iso.predict(Zs) == -1

overcost = (ml_ratio > 1) & (obr > 1) iso_flag = iso_raw & overcost

zabs = np.abs(Zs)

zcols = list(Z.columns)

# Appendix G. Multiple Linear Regression: Actual vs. Predicted Cost

# Appendix H. Extreme Gradient Boosting: Actual vs. Predicted Cost

# Appendix I. Isolation Forest: Cost Residual vs. Anomaly Score

# Appendix J. User Guide of the BUHAY-AH Application

1. Open the website and tap **Download for Android**, or open the web app and choose **Install app** (Android, PC) or **Share → Add to Home Screen** (iPhone).
2. In **Quote**, choose Building or Bridge, pick a reference plan or import a DXF or plan file, and adjust the plan variables. Read the lean start quotation, the standard estimate and the ceiling.
3. Open the **Bill of quantities** tab to review or export the items. Save the plan to the Library.
4. In **Check**, enter the contract amount (and optionally the submitted EDC, OCM, profit and VAT). Read the verdict, risk index, drivers and SHAP explanation.
5. Paste or upload the contractor's BOQ in **Line-item check** to find overpriced items.
6. In **Design**, pick a template, enter a requirement, or enter a budget; edit spaces, storeys and layout; add saved designs as wings; then press **Quote this design**. Edit unit rates in **Library → Unit price book**.

# Appendix K. Design Template Library

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| **DESIGN** | **ST.** | **L × W (m)** | **GFA m²** | **CAPACITY** | **START**<br>**₱M** | **STD ₱M** |
| 1-storey 2-classroom school building | 1 | 22.5 × 9.5 | 214 | 2 classrooms | 5.97 | 6.58 |
| 1-storey 3-classroom school building | 1 | 31.5 × 9.5 | 299 | 3 classrooms | 7.78 | 8.93 |
| 1-storey 4-classroom school building | 1 | 40.5 × 9.5 | 385 | 4 classrooms | 9.82 | 11.28 |
| Kindergarten building (2 rooms) | 1 | 27.0 × 9.5 | 256 | 2 classrooms | 6.78 | 7.78 |
| 2-storey 4-classroom school building | 2 | 26.0 × 9.5 | 494 | 4 classrooms | 11.31 | 13.05 |
| 2-storey 6-classroom school building | 2 | 38.5 × 9.5 | 732 | 6 classrooms | 16.25 | 18.77 |
| 2-storey 8-classroom school building with library | 2 | 61.0 × 9.5 | 1,159 | 8 classrooms | 25.10 | 29.03 |
| 2-storey senior high school building (6 CL + labs) | 2 | 56.5 × 9.5 | 1,074 | 6 classrooms | 23.35 | 27.00 |
| TVL workshop building (2 shops + 2 CL) | 1 | 49.5 × 9.5 | 470 | 2 classrooms | 11.82 | 13.59 |
| 3-storey 9-classroom school building | 3 | 38.5 × 9.5 | 1,097 | 9 classrooms | 24.68 | 28.57 |
| 3-storey 12-classroom school building with labs | 3 | 56.5 × 9.5 | 1,610 | 12 classrooms | 35.05 | 40.66 |
| 4-storey 16-classroom school building | 4 | 47.5 × 9.5 | 1,805 | 16 classrooms | 38.87 | 45.09 |
| 4-storey 20-classroom school building with support rooms | 4 | 65.5 × 9.5 | 2,489 | 20 classrooms | 52.38 | 60.86 |
| School admin & library building | 1 | 40.5 × 9.5 | 385 | — | 9.87 | 11.33 |
| Barangay health station | 1 | 12.0 × 12.4 | 149 | 1 consult rooms | 5.17 | 6.20 |
| Barangay health station with birthing room | 1 | 18.0 × 12.4 | 223 | 2 beds | 7.04 | 8.47 |
| Rural health unit (1-storey) | 1 | 28.5 × 12.4 | 353 | 3 consult rooms | 10.69 | 12.89 |
| Rural health unit with birthing (2-storey) | 2 | 19.0 × 12.4 | 471 | 4 beds | 12.79 | 15.58 |
| 10-bed infirmary | 1 | 32.0 × 12.4 | 397 | 10 beds | 11.86 | 14.31 |
| 25-bed community hospital (2-storey) | 2 | 30.0 × 12.4 | 744 | 25 beds | 19.52 | 23.86 |
| Barangay hall | 1 | 20.0 × 14.4 | 288 | 7 staff | 7.83 | 9.33 |
| Barangay hall with multi-purpose floor (2-storey) | 2 | 17.5 × 14.4 | 504 | 14 staff | 11.97 | 14.40 |
| Municipal hall (2-storey) | 2 | 35.5 × 14.4 | 1,022 | 63 staff | 22.80 | 27.57 |
| Provincial office building (3-storey) | 3 | 41.5 × 14.4 | 1,793 | 126 staff | 37.74 | 45.95 |
| Municipal police station | 1 | 22.0 × 14.4 | 317 | 14 staff | 8.56 | 10.19 |
| Public library | 1 | 45.0 × 9.5 | 428 | — | 10.82 | 12.44 |
| Child development center | 1 | 31.5 × 9.5 | 299 | 2 classrooms | 7.83 | 8.98 |
| Evacuation center, 100 persons | 1 | 26.0 × 24.0 | 624 | 100 persons | 15.33 | 17.58 |
| Evacuation center, 200 persons | 1 | 43.0 × 24.0 | 1,032 | 200 persons | 24.57 | 28.21 |
| Evacuation center, 400 persons | 1 | 55.0 × 36.0 | 1,980 | 400 persons | 47.26 | 54.30 |
| Evacuation center, 600 persons (2-storey) | 2 | 42.0 × 36.0 | 3,024 | 600 persons | 59.04 | 67.33 |
| Senior citizens center | 1 | 25.0 × 12.0 | 300 | 40 persons | 7.92 | 9.05 |
| Multi-purpose hall with stage | 1 | 41.0 × 12.0 | 492 | 80 persons | 12.21 | 13.98 |
| Public market, 40 stalls | 1 | 44.0 × 12.0 | 528 | 50 stalls | 13.78 | 15.83 |
| Public market, 100 stalls | 1 | 42.0 × 24.0 | 1,008 | 106 stalls | 24.73 | 28.51 |
| Public market, 200 stalls (2-storey) | 2 | 45.5 × 24.0 | 2,184 | 206 stalls | 45.65 | 53.07 |
| Dormitory, 48 beds | 1 | 23.5 × 12.0 | 282 | 48 beds | 7.81 | 8.97 |
| Dormitory, 96 beds (3-storey) | 3 | 17.0 × 12.0 | 612 | 96 beds | 14.82 | 17.15 |
| Teachers' quarters (8 units) | 1 | 27.5 × 12.0 | 330 | 16 beds | 9.03 | 10.38 |
| Barangay covered court | 1 | 45.0 × 20.0 | 900 | 300 persons | 13.70 | 15.06 |
| Covered court with bleachers and showers | 1 | 53.0 × 20.0 | 1,060 | 540 persons | 15.83 | 17.40 |
| Pedestrian footbridge 1 × 15 m | – | – | – | – | 3.23 | 3.49 |
| Single-cell RC box culvert 3.0 m | – | – | – | – | 1.73 | 1.87 |
| Double-barrel RC box culvert 2 × 3.0 m | – | – | – | – | 2.48 | 2.68 |
| Triple-barrel RC box culvert 3 × 3.5 m | – | – | – | – | 4.14 | 4.48 |
| Farm-to-market RCDG bridge 1 × 12 m (1 lane) | – | – | – | – | 5.78 | 6.22 |
| RCDG bridge 1 × 15 m (2 lanes) | – | – | – | – | 17.37 | 18.26 |
| RCDG bridge 2 × 20 m (2 lanes) | – | – | – | – | 29.59 | 31.61 |
| RCDG bridge 3 × 20 m (2 lanes) | – | – | – | – | 39.07 | 42.04 |

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| PSCG bridge 1 × 30 m (2 lanes) | – | – | – | – | 36.65 | 38.38 |
| PSCG bridge 3 × 30 m (2 lanes) | – | – | – | – | 77.80 | 81.61 |
| PSCG bridge 3 × 30 m (4 lanes) | – | – | – | – | 123.49 | 129.37 |
| Steel truss bridge 1 × 45 m | – | – | – | – | 56.73 | 60.94 |
| Steel truss bridge 2 × 60 m | – | – | – | – | 132.71 | 143.65 |

# Appendix L. Research Plan

**Rationale.** Public buildings and bridges lose value to overpricing, and communities without plans cannot tell what their budget should buy. An open tool that designs, prices and screens projects from national standards can make padding visible before and after award.

**Research questions.** The seven research questions in the Objective of the Study: plan variables, design generation, take-off accuracy, cost models, detection performance and deployment.

**Engineering goals.** A design generator that turns a requirement or a budget into a standards-compliant schematic design; a quantity take-off engine with itemized lean, standard and ceiling ABCs; a hybrid screening model with measured recall and precision; and an offline mobile application, Android package and website.

**Procedures.** Codify DPWH pay items and NSCP, DPWH, AASHTO, PD 1096, BP 344, DepEd, DOH and DSWD rules; build the take-off engine and design generator; generate the SBD-300 benchmark with known overpricing; train and validate MLR, XGBoost and Isolation Forest with LOOCV; compute SHAP values and the risk index; run the budget-to-design and bridge scenarios; build and test the application and website.

**Data analysis.** Descriptive statistics; VIF screening and OLS; RZ, RMSE and MAPE under LOOCV; precision, recall, F1-score and ROC AUC against injected labels; Pareto filtering, capacity frontiers and timing for the design search.

**Risk and safety.** Purely computational study on a personal computer. No human participants, vertebrate animals, potentially hazardous biological agents, hazardous chemicals, activities or devices were involved. All data are simulated or drawn from public documents; no personal information was collected.

**Bibliography.** See References.

# Appendix M. Risk and Safety Assessment

| **ITEM** | **ASSESSMENT** |
| --- | --- |
| Human participants | None. No surveys, interviews or personal data. |
| Vertebrate animals | None. |
| Potentially hazardous biological agents | None. |
| Hazardous chemicals, activities or devices | None. Work done on a laptop and in a web browser. |
| Data sources | Simulated benchmark (SBD-300) and public standards, issuances and news reports. |
| Responsible use | Results are screening signals for review by COA, the Ombudsman, the ICI or the implementing office, not findings of wrongdoing; generated designs are schematic and not for construction. |
| Duration | The research was conducted within the twelve-month limit for continuing projects. |

# Appendix N. Algorithms and Code Availability

All code and data are in the project repository: the shared cost engine (docs/app/js/engine.js), the design generator (docs/app/js/designs.js), the in-browser models (docs/app/js/ml.js), and the research pipeline (research/pipeline: simulate.py, train.py, design_results.js, build_paper.py). Running the pipeline in order reproduces every table and figure in this paper.

function fromBudget(usage, budget, opt) { opt = opt || {};

var U = USAGE\[usage], maxN = opt.maxStoreys || (usage === 'hospital' ? 5 : usage === 'court' || usage === 'market'

var basis = opt.basis || 'start', maxL = opt.maxLength || U.lot || 60;

var cost = function (q) { return basis === 'standard' ? q.fair : q.start; }; var make = function (k, N) {

var d = build(Object.assign(programFor(usage, k, N), { name: U.label + ', ' + k + ' ' + U.capLabel + ', ' + N +

return { k: k, N: N, design: d, quote: quote(d, opt) };

};

var r = U.range, results = \[], evals = 0; if (usage === 'court') maxN = 1;

// exhaustive enumeration of the discrete design space (storeys × capacity step); support rooms make

// cost non-monotonic in capacity, so every point is evaluated rather than bisected for (var N = 1; N <= maxN; N++) {

var best = null, over = 0;

for (var k = Math.max(r\[0], usage === 'school' ? N : r\[0]); k <= r\[1]; k += r\[2])

{

var t = make(k, N); evals++; var c = cost(t.quote);

if (c <= budget && t.design.L <= maxL) { if (!best || k > best.k || (k ===

best.k && c < cost(best.quote))) be

else if (c > budget * 1.5 && ++over >= 3) break;

}

if (best) results.push(best);

}

results.forEach(function (x) { x.cost = cost(x.quote); });

// keep Pareto-efficient options: no other option gives at least the capacity for

less

results = results.filter(function (x) { return !results.some(function (y) { return y

!== x && y.k >= x.k && y.cost

results.forEach(function (x) { x.cost = cost(x.quote); x.utilization = x.cost / budget; x.perUnit = x.k > 0 ? x.co

results.sort(function (x, y) { return y.k - x.k || x.cost - y.cost; }); if (results\[0]) results\[0].best = true;

return { usage: usage, budget: budget, basis: basis, options: results, evaluations: evals };

# Appendix O. Additional References Cited

American Association of State Highway and Transportation Officials. (2018). *A policy on geometric design of highways and streets* (7th ed.).

American Association of State Highway and Transportation Officials. (2020). *AASHTO LRFD bridge design specifications* (9th ed.).

Batas Pambansa Blg. 344. (1983). *Accessibility law*.

Cebu Daily News. (2023, July 21). *COA: CCMC project contract price was bloated by P62M*. [https://cebudailynews.inquirer.net/517377/coa-ccmc-project-contract-price-was-bloated-by-p62m](https://cebudailynews.inquirer.net/517377/coa-ccmc-project-contract-price-was-bloated-by-p62m)

Coffie, G. H., & Cudjoe, S. K. F. (2024). Using extreme gradient boosting (XGBoost) machine learning to predict construction cost overruns. *International Journal of Construction Management, 24*(16), 1742–1750. [https://doi.org/10.1080/15623599.2023.2289754](https://doi.org/10.1080/15623599.2023.2289754)

CoST – The Infrastructure Transparency Initiative. (n.d.). *Why infrastructure transparency matters*. [https://infrastructuretransparency.org/](https://infrastructuretransparency.org/)

Department of Education. (2010). *Educational facilities manual* (Rev. ed.).

Department of Health. (2012). *Administrative Order No. 2012-0012: Rules and regulations governing the new classification of hospitals and other health facilities in the Philippines*.

Department of Health. (2016). *Guidelines in the planning and design of hospitals and other health facilities*

(Administrative Order No. 2016-0042).

Department of Transportation. (2017). *Department Order No. 2017-011: Omnibus guidelines on the planning and identification of public road transportation services and franchise issuance*.

DZRH News. (2025, August 11). *20 percent of the entire P545-B flood control project went to 15 contractors*

*— Pres. Marcos*. [https://dzrh.com.ph/](https://dzrh.com.ph/)

Elmousalami, H. H. (2020). Artificial intelligence and parametric construction cost estimate modeling: State-of-the-art review. *Journal of Construction Engineering and Management, 146*(1), 03119008. [https://doi.org/10.1061/(ASCE)CO.1943-7862.0001678](<https://doi.org/10.1061/(ASCE)CO.1943-7862.0001678>)

Fazekas, M., & Tóth, I. J. (2016). From corruption to state capture: A new analytical framework with empirical applications from Hungary. *Political Research Quarterly, 69*(2), 320–334. [https://doi.org/10.1177/1065912916639137](https://doi.org/10.1177/1065912916639137)

Flyvbjerg, B., Holm, M. S., & Buhl, S. (2002). Underestimating costs in public works projects: Error or lie?

*Journal of the American Planning Association, 68*(3), 279–295. [https://doi.org/10.1080/01944360208976273](https://doi.org/10.1080/01944360208976273)

Interaksyon. (2025, September 11). *Philippines forms independent body to probe anomalies in infrastructure projects*. [https://interaksyon.philstar.com/politics-issues/2025/09/11/302050/](https://interaksyon.philstar.com/politics-issues/2025/09/11/302050/)

International Air Transport Association. (2019). *Airport development reference manual* (11th ed.).

Jensen, M. C., & Meckling, W. H. (1976). Theory of the firm: Managerial behavior, agency costs and ownership structure. *Journal of Financial Economics, 3*(4), 305–360. [https://doi.org/10.1016/0304-](https://doi.org/10.1016/0304-)405X(76)90026-X

Kenny, C. (2007). *Construction, corruption, and developing countries* (Policy Research Working Paper No.

4271). World Bank.

Kutner, M. H., Nachtsheim, C. J., & Neter, J. (2004). *Applied linear regression models* (4th ed.).

McGraw-Hill/Irwin.

Larocque, R., Boulé, A.-M., & Cappart, Q. (2025). Estimating road construction costs with explainable machine learning. *INFORMS Journal on Applied Analytics, 55*(2), 137–153. [https://doi.org/10.1287/inte.2023.0027](https://doi.org/10.1287/inte.2023.0027)

Locatelli, G., Mariani, G., Sainati, T., & Greco, M. (2017). Corruption in public projects and megaprojects: There is an elephant in the room! *International Journal of Project Management, 35*(3), 252–268. [https://doi.org/10.1016/j.ijproman.2016.09.010](https://doi.org/10.1016/j.ijproman.2016.09.010)

Mahamid, I. (2011). Early cost estimating for road construction projects using multiple regression techniques.

*Australasian Journal of Construction Economics and Building, 11*(4), 87–101. [https://doi.org/10.5130/AJCEB.v11i4.2195](https://doi.org/10.5130/AJCEB.v11i4.2195)

Molinaro, A. M., Simon, R., & Pfeiffer, R. M. (2005). Prediction error estimation: A comparison of resampling methods. *Bioinformatics, 21*(15), 3301–3307. [https://doi.org/10.1093/bioinformatics/bti499](https://doi.org/10.1093/bioinformatics/bti499)

Nemhauser, G. L., & Wolsey, L. A. (1988). *Integer and combinatorial optimization*. Wiley.

O'Brien, R. M. (2007). A caution regarding rules of thumb for variance inflation factors. *Quality & Quantity, 41*(5), 673–690. [https://doi.org/10.1007/s11135-006-9018-6](https://doi.org/10.1007/s11135-006-9018-6)

OECD. (2016). *Preventing corruption in public procurement*. OECD Publishing. Pareto, V. (1906). *Manuale di economia politica*. Società Editrice Libraria.

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830.

Philippine Center for Investigative Journalism. (2025, August 31). *5 reveals from the flood control data*. [https://pcij.org/2025/08/31/5-reveals-from-the-flood-control-data/](https://pcij.org/2025/08/31/5-reveals-from-the-flood-control-data/)

Philstar. (2025, March 1). *Newly opened P1.2 billion Isabela bridge collapses*. [https://www.philstar.com/headlines/2025/03/01/2425019/newly-opened-p12-billion-isabela-bridge-](https://www.philstar.com/headlines/2025/03/01/2425019/newly-opened-p12-billion-isabela-bridge-)collapses

Philstar. (2026, February 12). *Philippines falls in corruption index, among worst in SEA*. [https://www.philstar.com/headlines/2026/02/12/2507429/philippines-falls-corruption-index-among-](https://www.philstar.com/headlines/2026/02/12/2507429/philippines-falls-corruption-index-among-)worst-sea

PIANC. (2002). *Guidelines for the design of fender systems* (Report of MarCom Working Group 33). Presidential Decree No. 1096. (1977). *National building code of the Philippines*.

Republic Act No. 11223. (2019). *Universal health care act*. Republic Act No. 12009. (2024). *New government procurement act*. Republic Act No. 9514. (2008). *Fire code of the Philippines of 2008*.

Seabold, S., & Perktold, J. (2010). Statsmodels: Econometric and statistical modeling with Python. In

*Proceedings of the 9th Python in Science Conference* (pp. 92–96).

Sphere Association. (2018). *The Sphere handbook: Humanitarian charter and minimum standards in humanitarian response* (4th ed.).

United Nations. (2015). *Transforming our world: The 2030 agenda for sustainable development* (A/RES/70/1). Vapnik, V. N. (1998). *Statistical learning theory*. Wiley.

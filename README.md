# who-bears-the-risk

Replication package for Kazi Affnann Azom (2026), "Who Bears the Risk of Privatized War? Troops, Contractors and Third-Country Nationals."

The code rebuilds every table and figure in the paper from public sources: the Defense Department's quarterly census of contractor personnel in the USCENTCOM area, U.S. troop levels reported to Congress, the Defense Casualty Analysis System's records of military deaths, and the Labor Department's Defense Base Act death cases.

## What the paper finds

- In Afghanistan, contractors' share of the reported deaths on the U.S. side rose from 44.1 percent during the surge (FY2010-FY2011) to 74.9 percent during the advisory mission (FY2015-FY2017).
- About four-fifths of that rise came from the force mix, as contractors per soldier rose from 1.05 to 3.03, and one-fifth from a rise in contractors' relative risk.
- On the reported figures, a contractor was less likely to die than a soldier during the surge (rate ratio 0.75, 95 percent interval 0.68 to 0.83) and about as likely during the advisory mission (0.98, 0.70 to 1.39). Contractor deaths are counted only when a claim is filed, so these are lower bounds; with the under-reporting factor used by the Costs of War project, the rate ratio is 1.4 to 2.1.
- Third-country nationals rose from 12.8 percent of DoD contractors in Afghanistan in FY2009 to 40.7 percent in FY2019, largely in place of Afghan workers.

## What is here

| Folder or file | Contents |
|---|---|
| `analysis_plan.md` | The analysis plan, committed before any result was computed (see the git history), with every later change listed and dated |
| `code/` | Numbered scripts, run in order |
| `data/raw/` | The inputs, as downloaded (see `data/README.md`); the guard-contract file is downloaded by the script, not kept here |
| `data/clean/` | The quarterly and fiscal-year panels and the check of the CRS tables against the census |
| `output/tables/`, `output/figures/` | The tables and figures, as produced by the code |

Which output goes with which part of the paper:

| File | In the paper |
|---|---|
| `output/tables/table_yearly_panel.csv` | Table 2 (Afghanistan rows); yearly figures for Iraq in Section 6.6 |
| `output/tables/table_periods.csv` | Table 3 |
| `output/tables/table_decomposition.csv` | Table 4 |
| `output/tables/table_glm.csv` | Table 5 |
| `output/tables/table_nationality_afghanistan.csv` | Table 6 and the person-years in Section 6.7 |
| `output/tables/table_robustness.csv` | Table 7, and the two-year windows and approximate troop levels in Section 7 |
| `output/tables/table_tcn_correlation.csv` | The rank correlation in Section 6.7 |
| `output/tables/table_cumulative.csv` | The FY2009-FY2021 totals in Sections 6.2 and 6.6 |
| `output/tables/table_guard_contracts_by_agency_musd.csv` | The guard-service obligations in Section 4.3 |
| `data/clean/check_crs_vs_census.csv` | The check described in Section 4.1 |
| `output/figures/figure1_afghanistan_personnel.png` | Figure 1 |
| `output/figures/figure2_afghanistan_deaths_shares.png` | Figure 2 |
| `output/figures/figure3_afghanistan_death_rates.png` | Figure 3 |
| `output/figures/figure4_afghanistan_nationality.png` | Figure 4 |

## How to reproduce the results

The results were produced with Python 3.13 and the package versions pinned in `requirements.txt`.

```
pip install -r requirements.txt
python code/00_get_data.py      # downloads every input (about 50 MB, a few minutes)
python code/01_build_panel.py   # quarterly and fiscal-year panels
python code/02_analysis.py      # Tables 2 to 7 and the numbers in the text
python code/03_figures.py       # Figures 1 to 4
```

The Defense Casualty Analysis System updates its records, and a later download can differ slightly from the one used here (extraction date 28 October 2026). `data/raw/dcas/dcas_deaths_by_incident_country_fy.csv` keeps the counts used in the paper.

## Licenses

The code is released under the MIT License (see `LICENSE`). The derived data in `data/clean/` and `output/` are released under CC BY 4.0. The inputs keep the terms of their sources: the government reports and records are U.S. government works, and the three compiled datasets (contractor-census, contractor-injury-claims and us-guard-spending) are CC BY 4.0. See `data/README.md`.

## How to cite

Azom, Kazi Affnann (2026). *who-bears-the-risk: replication package for "Who Bears the Risk of Privatized War?"* [Software]. https://github.com/Affnann/who-bears-the-risk

See also `CITATION.cff`.

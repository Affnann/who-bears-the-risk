# who-bears-the-risk

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23780322.svg)](https://doi.org/10.5281/zenodo.23780322)

Replication package for Kazi Affnann Azom (2026), "Who Bears the Risk of Privatized War? Troops, Contractors and Third-Country Nationals." Preprint, Zenodo. [10.5281/zenodo.23788239](https://doi.org/10.5281/zenodo.23788239)

The code rebuilds every table and figure in the paper from public sources: the Defense Department's quarterly census of contractor personnel in the USCENTCOM area, U.S. troop levels reported to Congress, the Defense Casualty Analysis System's records of military deaths, and the Labor Department's Defense Base Act death cases.

## What the paper finds

- In Afghanistan, contractors' share of the reported deaths on the U.S. side rose from 44.1 percent during the surge (FY2010-FY2011) to 74.9 percent during the advisory mission (FY2015-FY2017).
- About four-fifths of the rise in its log-odds came from the force mix, as contractors per soldier rose from 1.05 to 3.03, and one-fifth from a rise in contractors' relative risk.
- On the reported figures, a contractor was less likely to die than a soldier during the surge (rate ratio 0.75, 95 percent interval 0.68 to 0.83) and about as likely during the advisory mission (0.98, 0.70 to 1.39). The regression test finds no sign that the rate ratio rose as troop numbers fell (coefficient 0.057, quasi-binomial standard error 0.200).
- Two known problems in the official counts are corrected in a robustness check: DoD said that its contractor counts for the first three quarters of FY2010 were inflated by counting errors, and the troop counts before August 2017 left out personnel on short missions and temporary duty. With both corrections the rate ratio is 0.91 (0.82 to 1.00) in the surge and 1.24 (0.88 to 1.75) in the advisory mission, and the force mix accounts for 77 percent of the rise.
- Contractor deaths are counted only when an employer reports them or a claim is filed, and workers from Afghanistan and third countries filed far fewer claims than Americans. Scaling the reported deaths by the under-reporting factor used by the Costs of War project gives a rate ratio of 1.4 to 2.1 (1.5 to 2.7 with both corrections). The Labor Department's counts also include contractors of other agencies, who are not in the census, which pulls the other way.
- Third-country nationals rose from 12.8 percent of DoD contractors in Afghanistan in FY2009 to 40.7 percent in FY2019, mainly because the number of Afghan workers fell.

## What is here

| Folder or file | Contents |
|---|---|
| `analysis_plan.md` | The analysis plan, committed before any result was computed, with every later change listed and dated. The commit was made locally; the repository was first pushed to GitHub at 18:18 UTC on 29 October 2026, after the first results, so the plan's date rests on the commit record (see the plan's header) |
| `code/` | Numbered scripts, run in order |
| `data/raw/` | The inputs, as downloaded (see `data/README.md`), and the hand-built file of approximate troop levels for FY2018-FY2020 (`data/raw/approx/`); the guard-contract file is downloaded by the script, not kept here |
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
| `output/tables/table_robustness.csv` | Table 7 (the checks set in advance), and the two-year windows and approximate troop levels in Section 7 |
| `output/tables/table_tcn_correlation.csv` | The two rank correlations for H3 in Section 6.7 |
| `output/tables/table_corrections.csv` | The corrections for the FY2010 contractor counts and for the troop counts before August 2017 (Table 7 and Section 7), with FY2010 alone (Section 6.3 and the note to Figure 3) and the rate ratios with both corrections and the factor of 2.15 (Section 7) |
| `output/tables/table_corrections_glm.csv` | The test of H2 with the corrected counts (Section 6.5) |
| `output/tables/table_cumulative.csv` | The FY2009-FY2021 totals in Section 6.2 and the Iraq FY2012-FY2021 totals in Section 6.6 |
| `output/tables/table_guard_contracts_by_agency_musd.csv` | The guard-service obligations in Section 4.3 |
| `output/tables/table_guard_contracts_by_agency_period_musd.csv` | Not used in the paper: the same obligations by period. The figures are net of deobligations, so a cell can be negative (the State Department's Afghanistan total for FY2008-FY2011 is -227.5 million dollars) |
| `data/clean/check_crs_vs_census.csv` | The check described in Section 4.1 |
| `output/figures/figure1_afghanistan_personnel.png` | Figure 1 |
| `output/figures/figure2_afghanistan_deaths_shares.png` | Figure 2 |
| `output/figures/figure3_afghanistan_death_rates.png` | Figure 3 |
| `output/figures/figure4_afghanistan_nationality.png` | Figure 4 |

## How to reproduce the results

The results were produced with Python 3.13 and the package versions pinned in `requirements.txt`.

```
pip install -r requirements.txt
python code/00_get_data.py      # downloads the inputs (about 50 MB, a few minutes)
python code/01_build_panel.py   # quarterly and fiscal-year panels
python code/02_analysis.py      # Tables 2 to 7 and the numbers in the text
python code/03_figures.py       # Figures 1 to 4
```

`00_get_data.py` downloads every input except the approximate troop levels for FY2018-FY2020, which were built by hand from CRS report R45122 and are kept in `data/raw/approx/` with the basis of each value. The Defense Casualty Analysis System updates its records, and a later download can differ slightly from the one used here (extraction date 28 October 2026), so the DCAS counts have no checksum in `data/raw/download_log.csv`. `data/raw/dcas/dcas_deaths_by_incident_country_fy.csv` keeps the counts used in the paper.

## Licenses

The code is released under the MIT License (see `LICENSE`). The derived data in `data/clean/` and `output/` and the hand-built file in `data/raw/approx/` are released under CC BY 4.0 (see `LICENSE-DATA`). The inputs keep the terms of their sources: the government reports and records are U.S. government works, and the three compiled datasets (contractor-census, contractor-injury-claims and us-guard-spending) are CC BY 4.0. See `data/README.md`.

## How to cite

Azom, Kazi Affnann (2026). *who-bears-the-risk: replication package for 'Who Bears the Risk of Privatized War?'* (Version v1.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.23780323

- This version (v1.0.0): [10.5281/zenodo.23780323](https://doi.org/10.5281/zenodo.23780323)
- All versions (always points to the latest): [10.5281/zenodo.23780322](https://doi.org/10.5281/zenodo.23780322)

To cite the paper:

Azom, Kazi Affnann (2026). *Who Bears the Risk of Privatized War? Troops, Contractors and Third-Country Nationals* [Preprint]. Zenodo. https://doi.org/10.5281/zenodo.23788239

See also `CITATION.cff`.

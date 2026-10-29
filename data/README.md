# Data

Every input is downloaded by `code/00_get_data.py`, which records each file's source and checksum in `raw/download_log.csv`.

## Raw inputs (`raw/`)

| Folder or file | Source | Downloaded | Terms |
|---|---|---|---|
| `contractor-census/contractor_census_headcounts.csv` | The DoD quarterly contractor census for the USCENTCOM area, as compiled in contractor-census v1.0.0 (Zenodo, https://doi.org/10.5281/zenodo.23736051) | 29 October 2026 | CC BY 4.0 (compilation); the reports are U.S. government works |
| `contractor-injury-claims/` | U.S. Department of Labor Defense Base Act case summaries by nation and fiscal year, FY2009-FY2024, and the cumulative 2001-2024 table, as compiled in contractor-injury-claims v1.0.0 (Zenodo, https://doi.org/10.5281/zenodo.23746799) | 29 October 2026 | CC BY 4.0 (compilation); the tables are U.S. government works |
| `us-guard-spending/` (not kept in the repository) | USAspending contract actions for guard services (product code S206), as compiled in us-guard-spending v1.0.0 (Zenodo, https://doi.org/10.5281/zenodo.23750993). The script downloads it (about 34 MB) | 29 October 2026 | CC BY 4.0 (compilation); the source data are U.S. government works |
| `crs/R44116_2021-02-22.pdf` | Heidi M. Peters, *Department of Defense Contractor and Troop Levels in Afghanistan and Iraq: 2007-2020*, CRS Report R44116, 22 February 2021, from EveryCRSReport.com | 29 October 2026 | U.S. government work |
| `dcas/dcas_deaths_by_incident_country_fy.csv` | Defense Casualty Analysis System (Defense Manpower Data Center), records of the fallen for OEF, OFS, OIF, OND and OIR, counted by operation, incident country code, fiscal year of death and hostile or non-hostile. The script keeps only these counts, not the names in the records | 29 October 2026 (DCAS extraction date 28 October 2026) | U.S. government work |
| `dcas/dcas_download_notes.csv` | Number of records per operation, records without a date, DCAS extraction date | 29 October 2026 | |
| `approx/afghanistan_troops_fy2018_2020_approx.csv` | Approximate quarterly U.S. troop levels in Afghanistan, FY2018-FY2020, built by hand from the official figures quoted in versions of CRS Report R45122; each row states its basis (see `approx/README.md`) | 29 October 2026 | |

## Clean data (`clean/`), built by `code/01_build_panel.py`

| File | Contents |
|---|---|
| `troops_quarterly_crs.csv` | Troop levels and contractor totals by quarter, parsed from CRS R44116 Tables 1 and 3, with a note for each troop figure (Boots on the Ground, force management level, or not available) |
| `check_crs_vs_census.csv` | The CRS contractor totals compared with the census, quarter by quarter (all 95 quarters that both cover match; the CRS tables also have 8 quarters the census does not cover) |
| `contractors_quarterly.csv` | The census rows used, Afghanistan and Iraq (Iraq and Syria from FY2018 Q2) |
| `panel_fy.csv` | One row per country and fiscal year, FY2009-FY2021: average contractors by nationality, average troops (official or approximate), military deaths (all and hostile) and Defense Base Act death cases |

## Known problems in the official counts

- **Afghanistan contractors, FY2010.** The census for the fourth quarter of FY2010 says the fall from about 107,000 to 70,599 "is not due to a large reduction in contractor personnel, but rather is due to counting errors (primarily in one specific reporting activity), that have been perpetuated throughout this Fiscal Year". The counts printed for the first three quarters of FY2010 are therefore too high. The main estimates use the printed counts; `output/tables/table_corrections.csv` shows the results with every FY2010 quarter at the recounted level.
- **Afghanistan troops before August 2017.** In August 2017 the Defense Department began to count personnel on short missions, on temporary duty and in some support units (CRS R44116, Table 1, note b). About 11,000 troops were then present against an official figure of about 8,400 (CRS R45122, March 2018). The figures before the fourth quarter of FY2017 probably leave these personnel out. `table_corrections.csv` adds 2,600 to each earlier quarter, and in a variant scales FY2015 to the third quarter of FY2017 by 11,000 / 8,400.

## Definitions

- **Fiscal year:** the U.S. fiscal year, 1 October to 30 September.
- **Personnel:** the mean of the four quarterly counts in a fiscal year, which approximates person-years.
- **Military deaths:** DCAS records whose incident geographic code is AF (Afghanistan) or IZ (Iraq), by fiscal year of the date of death.
- **Contractor deaths:** Defense Base Act death cases opened in the fiscal year for that nation. The nation is where the injury happened, not the worker's nationality, and the Labor Department states that these counts "do not constitute the complete or official casualty statistics of civilian contractor injuries and deaths."

# Approximate U.S. troop levels in Afghanistan, FY2018 to FY2020

The Pentagon stopped publishing troop numbers for Afghanistan, Iraq and Syria in late 2017 (CRS R44116, p. 3). This file gives approximate quarterly levels built by hand from the official figures quoted in the versions of CRS report R45122, *Afghanistan: Background and U.S. Policy In Brief*, downloaded from EveryCRSReport.com on 29 October 2026 (https://www.everycrsreport.com/reports/R45122.html). Each row states its basis. It is the only input that is not downloaded by `code/00_get_data.py`.

How the columns were set:

- When one quoted figure covers a quarter, the central value is that figure.
- When a quarter spans a change between two quoted figures, the central value is their midpoint.
- When versions describe the same level with different figures, the central value is their midpoint. The versions of 5 March, 3 April, 1 May, 1 June and 3 August 2018 put the level reached after the reinforcements ordered in September 2017 at "around 15,000"; their footnote (note 67 in the 5 March 2018 version) gives 15,298 active-duty and reserve troops on 30 September 2017, from the Defense Manpower Data Center. The versions of 10 September 2018 to 1 August 2019 put the same level at "around 14,000", with the same footnote. Every FY2018 quarter is therefore set to 14,500.
- For FY2019 the versions keep repeating "around 14,000", but the 1 November 2019 version reports that troops had been "gradually reduced by 2,000 over the past year, to between 12,000 and 13,000" by October 2019. The FY2019 central values follow a steady reduction from about 14,500 to about 12,500.
- The low and high columns bracket the quoted figures.

All these figures date from after August 2017, when the Defense Department began to count personnel on short-duration missions and in a temporary duty status in its totals for Afghanistan (CRS R44116, Table 1, note b). The R45122 versions do not say how each figure was counted, and the 15,298 is a separate personnel count by the Defense Manpower Data Center.

These values are used only in the separate FY2018-FY2020 extension, never in the main tests. FY2021 is not given, because troop levels changed within months during the withdrawal.

Revisions, both on 29 October 2026 and after the first results (see `analysis_plan.md`, section 8, items 5 and 7):

1. About 19:00 UTC, following the 1 November 2019 and later versions:
   - FY2018, first quarter: central 12,500 to 13,050 (the midpoint of 11,100 and 15,000), high 14,000 to 15,000;
   - FY2019, quarters 1 to 4: central 14,000 in every quarter to 14,250, 13,750, 13,250 and 12,750; low 13,000 to 13,500, 13,000, 12,500 and 12,000; high 14,000 to 15,000, 14,500, 14,000 and 14,000;
   - FY2020: first quarter, central 13,500 to 12,500, low 13,000 to 12,000, high 14,000 to 13,000; second quarter, central 13,000 to 12,500; third quarter, central 10,000 to 10,300; fourth quarter, central 8,000 to 8,600.
2. About 20:10 UTC: the first revision had assumed that the level rose during the first quarter of FY2018, but the versions date the 15,298 count to 30 September 2017, before that quarter began, and the later versions describe the same level as "around 14,000". The FY2018 rows now read:
   - first quarter: central 13,050 to 14,500, low 11,100 to 14,000, high 15,000 to 15,300;
   - second and third quarters: central 15,000 to 14,500;
   - fourth quarter: central 14,000 to 14,500.

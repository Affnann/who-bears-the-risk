# Analysis plan

**Paper:** Who Bears the Risk of Privatized War? Troops, Contractors and Third-Country Nationals in Afghanistan and Iraq

**Written:** 29 October 2026, committed at 17:12 UTC (see the git history). This was before any death rate, rate ratio, death share, personnel share, decomposition or regression in this plan had been computed. The commit was made in the project's local git repository, which was first pushed to GitHub at 18:18 UTC, after the first results (17:17 UTC), so the plan's date rests on the commit record.

**What had been seen before writing it:** the yearly Defense Base Act death counts for Afghanistan and Iraq as printed in contractor-injury-claims v1.0.0; the quarterly troop and contractor figures in CRS report R44116 (Tables 1 and 3); the quarterly census rows in contractor-census v1.0.0; and the number of DCAS death records per operation and incident country (totals only, not by year). Three figures were also seen in the text of sources: the troop numbers quoted in some census reports, the troop levels quoted in CRS report R45122, and Coburn and Gill's (2022) claim rates by claimant address.

Every change made after results were seen is listed and dated at the end.

## 1. Questions

1. How was the death toll of the U.S. war effort divided between U.S. troops and DoD-funded contractors, year by year, in Afghanistan (FY2009 to FY2021) and Iraq (FY2009 to FY2011)?
2. Per person in the country, were contractors more or less likely than troops to die, using the reported figures, and did this change as troops withdrew?
3. How much of any rise in the contractors' share of deaths came from having more contractors per soldier, and how much from a change in relative risk?
4. How did the nationality mix of contractors change as troops withdrew, and what share of the U.S. side's person-years in Afghanistan was worked by third-country nationals?
5. How much could under-reporting of contractor deaths change the answers?

## 2. Data

| Item | Source | Use |
|---|---|---|
| Contractor personnel, by nationality | DoD quarterly contractor census, via contractor-census v1.0.0 (Zenodo, DOI 10.5281/zenodo.23736051) | Rows for Afghanistan and Iraq: total, U.S. citizens, third-country nationals (TCNs), local nationals |
| Troop levels | CRS report R44116 (Peters, 22 February 2021), Tables 1 and 3, which use DoD "Boots on the Ground" reports | Afghanistan Q4 FY2007 to Q4 FY2017; Iraq Q4 FY2007 to Q1 FY2012 |
| Troop levels, FY2018 to FY2021 (Afghanistan) | Official figures as quoted in versions of CRS report R45122 | Approximate only; used in a separate extension, never in the main tests |
| Military deaths | Defense Casualty Analysis System (DCAS), names-of-fallen records for OEF, OFS, OIF, OND and OIR | Counted by incident country (codes AF and IZ) and fiscal year of death; total deaths and hostile deaths. Only counts are kept, not names |
| Contractor deaths | U.S. Department of Labor Defense Base Act (DBA) death cases by nation of injury and fiscal year, via contractor-injury-claims v1.0.0 (Zenodo, DOI 10.5281/zenodo.23746799) | Afghanistan and Iraq, FY2009 onward |
| Guard-service contracts | USAspending, product code S206, via us-guard-spending v1.0.0 (Zenodo, DOI 10.5281/zenodo.23750993) | Obligations for work in Afghanistan and Iraq by agency, to show how much security work lay outside the DoD census |

## 3. Construction

- The U.S. fiscal year *t* runs from 1 October of year *t* − 1 to 30 September of year *t*.
- Personnel (person-years) for group *g* in country *c* and year *t* is the mean of the quarterly figures for quarters 1 to 4 of fiscal year *t*. A year with a missing quarter uses the mean of the quarters available and is flagged.
- The FY2009 Q3 census row for Afghanistan prints a total (73,968) that is 1,000 more than its parts. Totals use the printed total; nationality shares use the printed parts.
- Military deaths in year *t* are DCAS records whose incident geographic code is the country and whose date of death falls in fiscal year *t*. Records without a date are dropped and counted.
- Contractor deaths in year *t* are DBA death cases opened in fiscal year *t* for that nation. A DBA case is opened when the death is reported, which is usually soon after it happens but can be later.
- The main sample is the years with official troop counts: Afghanistan FY2009 to FY2017 and Iraq FY2009 to FY2011. Afghanistan FY2018 to FY2021 is reported separately.

## 4. Measures

1. Contractor share of deaths: *s*^D = *D*_C / (*D*_C + *D*_M).
2. Contractor share of personnel: *s*^P = *P*_C / (*P*_C + *P*_M).
3. Death rates per 1,000 person-years: *r*_g = 1,000 *D*_g / *P*_g, and the rate ratio RR = *r*_C / *r*_M. Rates get exact Poisson 95% confidence intervals. RR gets the exact conditional interval: given the total deaths *n*, *D*_C is binomial with probability *π* = RR *P*_C / (RR *P*_C + *P*_M), so a Clopper-Pearson interval for *π* converts to an interval for RR.
4. Identity: logit(*s*^D) = ln RR + logit(*s*^P). The change in the log-odds of the contractor death share between two periods therefore splits exactly into the change in ln RR and the change in the log-odds of the personnel share. This is the decomposition for question 3. Periods: surge (FY2010 to FY2011) and advisory mission (FY2015 to FY2017) in Afghanistan; FY2009 and FY2011 in Iraq.
5. Nationality: the shares of U.S. citizens, TCNs and local nationals among contractors, and the TCN share of all U.S.-side personnel (troops plus contractors).
6. An equal-risk benchmark: deaths that TCNs would account for if all contractors died at the reported contractor rate, *r*_C × *P*_TCN. This is illustrative only, because the DBA data do not record nationality.

## 5. Hypotheses, stated before the results

- **H1.** The contractor share of deaths rises as troop numbers fall.
- **H2.** The rate ratio rises as troop numbers fall: ln RR decreases with ln troops.
- **H3.** In Afghanistan the TCN share of contractors, and of all U.S.-side personnel, rises during the drawdown after FY2012.

## 6. Main test

Conditional on the total deaths in a country-year, contractor deaths are binomial. The model is a binomial GLM (logit link) for *D*_C out of *D*_C + *D*_M, with offset ln(*P*_C / *P*_M):

logit *π*_ct = ln(*P*_C,ct / *P*_M,ct) + *β*_0 + *β*_1 (ln *P*_M,ct − mean) + *β*_2 Iraq_c

so that ln RR_ct = *β*_0 + *β*_1 (ln *P*_M,ct − mean) + *β*_2 Iraq_c. H2 predicts *β*_1 < 0. The sample is the 12 country-years with official troop counts. Standard errors use the quasi-binomial scale (Pearson chi-squared over degrees of freedom), because deaths cluster in attacks; robust (HC1) standard errors are also reported. With 12 observations this test has little power, so the paper will put most weight on the year-by-year estimates and the decomposition, and will say so.

## 7. Robustness

1. Hostile military deaths only.
2. DBA death cases with "Nation Pending" allocated to Afghanistan and Iraq in proportion to each year's death cases with a known nation.
3. Two-year windows, to reduce the effect of reporting dates.
4. Local nationals left out of the contractor denominator: the rate per U.S. and TCN contractor, which is an upper bound for non-local contractors if every reported death was a U.S. citizen or TCN.
5. Under-reporting scenarios: contractor deaths multiplied by 1.5 and by 2.0, and by the ratio implied by Costs of War's estimate, if that paper states the reported count it starts from.
6. Afghanistan FY2018 to FY2021 with approximate troop levels, using low and high values.

## 8. Changes

### Before any result was computed

- 29 October 2026, by 17:14 UTC: FY2021 is left out of the rate extension in section 7, item 6. Troop levels changed within months during the withdrawal and evacuation, and the census counted no contractors in its fourth quarter, so no yearly troop figure for FY2021 can be defended. FY2021 still appears in the death counts and shares, which need no troop figure. (This entry first gave the time as "about 17:35 UTC", which was wrong: the file was last saved at 17:14:16 UTC, and the first result tables were created at 17:17:11 UTC.)

### Not in the plan, added while the analysis code was written

These were added between the plan (17:12 UTC) and the commit of the code (17:44 UTC). The file history cannot show whether each was added before or after the first results, so they are listed here:

- the main test with hostile military deaths only, and for Afghanistan alone (Table 5);
- a rank correlation as the test of H3, which the plan did not specify;
- the drawdown period (FY2012 to FY2014), which section 4 does not name: its row in the period table (Table 3), the comparison of the surge with the drawdown in the decomposition (Table 4) and the drawdown column in the robustness table (Table 7);
- two extra rows in the period table: FY2018 to FY2020 together, with approximate troops, and all years with official troop counts, for each country;
- descriptive totals and comparisons: the death counts for FY2009 to FY2021 (`table_cumulative.csv`) and the comparisons with earlier figures in Section 6.8 of the paper.

The code commit shows an author time of 17:44 UTC and a commit time of 18:15 UTC, because it was amended at 18:15 to stop tracking a large downloaded input and to keep the paper drafts, which had never been committed, out of the repository (`.gitignore`); the amendment did not change the code.

### After results were seen

All on 29 October 2026, after an independent check of the first draft:

1. About 19:00 UTC: the quasi-binomial standard errors in the main test were wrong. statsmodels, given the two-column binomial form with `scale="X2"`, used a scale of about 0.05 instead of the dispersion (about 11 to 13). The model is now fitted to proportions with the number of deaths as weights, which gives the correct scale, and the p-values use the t distribution with the residual degrees of freedom. The robust standard errors labelled HC1 were in fact HC0, because statsmodels returns the same matrix for HC0 to HC3 in a GLM; HC1 is now HC0 times n / (n − k). The estimate of *β*_1 does not change, and neither does the conclusion about H2.
2. About 19:00 UTC: in robustness check 5, the rate ratio's interval is now the main interval multiplied by the factor. The first version put the scaled counts into the exact interval as if they had been observed, which made the intervals too narrow. The point estimates do not change.
3. About 19:00 UTC: H3 is now reported with both of its measures. The rank correlation with the log of troop numbers is 0.03 for the share of third-country nationals among contractors, and −0.42 for their share of all U.S.-side personnel. The first draft reported only the first.
4. About 19:00 UTC: two corrections for known problems in the official counts were added as robustness checks. They are not in the plan. The main estimates are unchanged.
   - The census for the fourth quarter of FY2010 states that the fall in Afghanistan from 107,000 to 71,000 "is not due to a large reduction in contractor personnel, but rather is due to counting errors ... that have been perpetuated throughout this Fiscal Year". The check puts every FY2010 quarter at the recounted fourth-quarter level.
   - In August 2017 the Defense Department began to count troops on short missions, on temporary duty and in some support units (CRS R44116, Table 1, note b), and about 11,000 troops were then present against an official figure of about 8,400 (CRS R45122, March 2018). The check adds 2,600 troops to every Afghanistan quarter before the fourth quarter of FY2017. A variant scales FY2015 to the third quarter of FY2017 by 11,000 / 8,400.
5. About 19:00 UTC: the approximate troop levels (`data/raw/approx/afghanistan_troops_fy2018_2020_approx.csv`) were revised. The 1 November 2019 version of CRS R45122 reports that troops had been reduced to between 12,000 and 13,000 by October 2019, and the later versions give 12,000 in March and May 2020. The changes:
   - FY2018, first quarter: central value 12,500 to 13,050 (the midpoint of 11,100 and 15,000, as the file's own rule says), high value 14,000 to 15,000;
   - FY2019, quarters 1 to 4: central values 14,000 in every quarter to 14,250, 13,750, 13,250 and 12,750; low values 13,000 in every quarter to 13,500, 13,000, 12,500 and 12,000; high values 14,000 in every quarter to 15,000, 14,500, 14,000 and 14,000;
   - FY2020: first quarter, central 13,500 to 12,500, low 13,000 to 12,000 and high 14,000 to 13,000; second quarter, central 13,000 to 12,500; third quarter, central 10,000 to 10,300; fourth quarter, central 8,000 to 8,600.

   The FY2018 to FY2020 extension changes slightly: its rate ratio goes from 0.95 to 0.93.
6. The text now says "95 quarters" where it said "103". The CRS tables have 103 quarter rows, but only 95 of them overlap the census, and all 95 match.

After a second independent check:

7. About 20:10 UTC: the approximate troop levels for FY2018 were revised again. Revision 5 assumed that the level rose during the first quarter of FY2018, but the R45122 versions date the count of 15,298 to 30 September 2017, before that quarter began, and the versions from September 2018 describe the same level as "around 14,000" rather than "around 15,000". Every FY2018 quarter now has the midpoint, 14,500, as its central value. The changes:
   - first quarter: central 13,050 to 14,500, low 11,100 to 14,000, high 15,000 to 15,300;
   - second and third quarters: central 15,000 to 14,500;
   - fourth quarter: central 14,000 to 14,500.

   The FY2018 rate ratio goes from 1.47 to 1.49, and the FY2018 to FY2020 rate ratio from 0.93 (0.66 to 1.34) to 0.94 (0.66 to 1.35).
8. Outputs added, with no change to any result: the Iraq death totals for FY2012 to FY2021 in `table_cumulative.csv`, which the paper quotes in Section 6.6; and, in `table_corrections.csv`, the figures for FY2010 alone and the rate ratios with both corrections and the under-reporting factor of 2.15.

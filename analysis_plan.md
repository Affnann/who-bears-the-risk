# Analysis plan

**Paper:** Who Bears the Risk of Privatized War? Troops, Contractors and Third-Country Nationals in Afghanistan and Iraq

**Written:** 29 October 2026, committed at 17:12 UTC (see the git history). This was before any death rate, rate ratio, death share, personnel share, decomposition or regression in this plan had been computed.

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

- 29 October 2026, about 17:35 UTC: FY2021 is left out of the rate extension in section 7, item 6. Troop levels changed within months during the withdrawal and evacuation, and the census counted no contractors in its fourth quarter, so no yearly troop figure for FY2021 can be defended. FY2021 still appears in the death counts and shares, which need no troop figure.

### After results were seen

(none yet)

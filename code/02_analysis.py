"""Main analysis: shares, rates, rate ratios, decomposition, GLM, robustness, nationality and guard spending.

Input: data/clean/panel_fy.csv (01_build_panel.py), data/raw/us-guard-spending/s206_transactions.csv.gz
Output: output/tables/*.csv
"""
import math, os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = os.path.join(ROOT, "output", "tables")
os.makedirs(TAB, exist_ok=True)
p = pd.read_csv(os.path.join(ROOT, "data", "clean", "panel_fy.csv"))
p["contractor_deaths_dba"] = pd.to_numeric(p["contractor_deaths_dba"], errors="coerce")
p["troops"] = pd.to_numeric(p["troops"], errors="coerce")
ALPHA = 0.05


def pois_ci(k):
    lo = stats.chi2.ppf(ALPHA / 2, 2 * k) / 2 if k > 0 else 0.0
    hi = stats.chi2.ppf(1 - ALPHA / 2, 2 * k + 2) / 2
    return lo, hi


def rr_ci(dc, dm, pc, pm):
    """Exact conditional CI for the rate ratio (contractors / troops)."""
    n = dc + dm
    e = pc / pm
    lo_pi = stats.beta.ppf(ALPHA / 2, dc, n - dc + 1) if dc > 0 else 0.0
    hi_pi = stats.beta.ppf(1 - ALPHA / 2, dc + 1, n - dc) if dc < n else 1.0
    f = lambda pi: pi / ((1 - pi) * e) if pi < 1 else math.inf
    return f(lo_pi), f(hi_pi)


def logit(x):
    return math.log(x / (1 - x))


def measures(dc, dm, pc, pm):
    rc, rm = 1000 * dc / pc, 1000 * dm / pm
    rc_lo, rc_hi = (1000 * v / pc for v in pois_ci(dc))
    rm_lo, rm_hi = (1000 * v / pm for v in pois_ci(dm))
    rr = rc / rm
    rr_lo, rr_hi = rr_ci(dc, dm, pc, pm)
    return dict(share_deaths=dc / (dc + dm), share_personnel=pc / (pc + pm),
                rate_contractors=rc, rate_contractors_lo=rc_lo, rate_contractors_hi=rc_hi,
                rate_troops=rm, rate_troops_lo=rm_lo, rate_troops_hi=rm_hi,
                rate_ratio=rr, rate_ratio_lo=rr_lo, rate_ratio_hi=rr_hi,
                contractors_per_soldier=pc / pm)


# ---------- Table 1 and 2: yearly panels ----------
out = []
for _, r in p.iterrows():
    row = r.to_dict()
    dc, dm = r["contractor_deaths_dba"], r["military_deaths"]
    row["share_deaths"] = dc / (dc + dm) if pd.notna(dc) and (dc + dm) > 0 else np.nan
    if pd.notna(r["troops"]) and pd.notna(dc) and r["troops"] > 0 and r["contractors"] > 0:
        row.update(measures(dc, dm, r["contractors"], r["troops"]))
    out.append(row)
yearly = pd.DataFrame(out)
yearly.to_csv(os.path.join(TAB, "table_yearly_panel.csv"), index=False)

# ---------- Periods ----------
PERIODS = [
    ("Afghanistan", "Surge, FY2010-FY2011", [2010, 2011]),
    ("Afghanistan", "Drawdown, FY2012-FY2014", [2012, 2013, 2014]),
    ("Afghanistan", "Advisory mission, FY2015-FY2017", [2015, 2016, 2017]),
    ("Afghanistan", "Approximate troops, FY2018-FY2020", [2018, 2019, 2020]),
    ("Afghanistan", "Official troop counts, FY2009-FY2017", list(range(2009, 2018))),
    ("Iraq", "FY2009", [2009]),
    ("Iraq", "FY2011", [2011]),
    ("Iraq", "Official troop counts, FY2009-FY2011", [2009, 2010, 2011]),
]


def pooled(country, years, deaths_col="military_deaths", troops_col="troops", contractor_deaths=None, pc_col="contractors"):
    s = p[(p["country"] == country) & (p["fiscal_year"].isin(years))]
    dc = (contractor_deaths if contractor_deaths is not None else s["contractor_deaths_dba"]).sum()
    dm = s[deaths_col].sum()
    pc = pd.to_numeric(s[pc_col], errors="coerce").sum()
    pm = pd.to_numeric(s[troops_col], errors="coerce").sum()
    return dc, dm, pc, pm


per = []
for country, label, years in PERIODS:
    dc, dm, pc, pm = pooled(country, years)
    m = measures(dc, dm, pc, pm)
    per.append(dict(country=country, period=label, years=f"{years[0]}-{years[-1]}", contractor_deaths=dc,
                    military_deaths=dm, contractor_person_years=pc, troop_person_years=pm, **m))
periods = pd.DataFrame(per)
periods.to_csv(os.path.join(TAB, "table_periods.csv"), index=False)

# ---------- Decomposition: logit(sD) = ln RR + logit(sP) ----------
dec = []
for country, a, b in [("Afghanistan", "Surge, FY2010-FY2011", "Advisory mission, FY2015-FY2017"),
                      ("Afghanistan", "Surge, FY2010-FY2011", "Drawdown, FY2012-FY2014"),
                      ("Iraq", "FY2009", "FY2011")]:
    A = periods[(periods.country == country) & (periods.period == a)].iloc[0]
    B = periods[(periods.country == country) & (periods.period == b)].iloc[0]
    d_total = logit(B.share_deaths) - logit(A.share_deaths)
    d_rr = math.log(B.rate_ratio) - math.log(A.rate_ratio)
    d_mix = logit(B.share_personnel) - logit(A.share_personnel)
    dec.append(dict(country=country, from_period=a, to_period=b,
                    share_deaths_from=A.share_deaths, share_deaths_to=B.share_deaths,
                    change_log_odds_death_share=d_total, from_force_mix=d_mix, from_relative_risk=d_rr,
                    pct_from_force_mix=100 * d_mix / d_total, pct_from_relative_risk=100 * d_rr / d_total,
                    check_residual=d_total - d_mix - d_rr))
decomp = pd.DataFrame(dec)
decomp.to_csv(os.path.join(TAB, "table_decomposition.csv"), index=False)

# ---------- GLM: ln RR on ln troops (main test, H2) ----------
main = p[((p.country == "Afghanistan") & p.fiscal_year.between(2009, 2017)) |
         ((p.country == "Iraq") & p.fiscal_year.between(2009, 2011))].copy()


def glm(df, deaths_col="military_deaths", dc_col="contractor_deaths_dba", pc_col="contractors"):
    df = df.copy()
    x = np.log(df["troops"]) - np.log(df["troops"]).mean()
    X = pd.DataFrame({"const": 1.0, "ln_troops_centered": x, "iraq": (df.country == "Iraq").astype(float)})
    y = np.column_stack([df[dc_col].values, df[deaths_col].values])
    off = np.log(df[pc_col].astype(float) / df["troops"])
    res = []
    for name, kw in [("quasi-binomial", dict(scale="X2")), ("robust HC1", dict(cov_type="HC1"))]:
        fit = sm.GLM(y, X, family=sm.families.Binomial(), offset=off).fit(**kw)
        for k in X.columns:
            res.append(dict(se_type=name, term=k, coef=fit.params[k], se=fit.bse[k], p=fit.pvalues[k],
                            ci_lo=fit.conf_int().loc[k, 0], ci_hi=fit.conf_int().loc[k, 1],
                            n=len(df), pearson_chi2=fit.pearson_chi2, df_resid=fit.df_resid))
    return res


g = []
for label, df, kw in [("Main: all deaths, both countries", main, {}),
                      ("Hostile military deaths only", main, dict(deaths_col="military_deaths_hostile"))]:
    for r in glm(df, **kw):
        g.append(dict(model=label, **r))
glm_tab = pd.DataFrame(g)
# Afghanistan-only model: no Iraq column
af = main[main.country == "Afghanistan"].copy()
x = np.log(af["troops"]) - np.log(af["troops"]).mean()
X = pd.DataFrame({"const": 1.0, "ln_troops_centered": x})
y = np.column_stack([af["contractor_deaths_dba"].values, af["military_deaths"].values])
off = np.log(af["contractors"] / af["troops"])
rows = []
for name, kw in [("quasi-binomial", dict(scale="X2")), ("robust HC1", dict(cov_type="HC1"))]:
    fit = sm.GLM(y, X, family=sm.families.Binomial(), offset=off).fit(**kw)
    for k in X.columns:
        rows.append(dict(model="Afghanistan only", se_type=name, term=k, coef=fit.params[k], se=fit.bse[k], p=fit.pvalues[k],
                         ci_lo=fit.conf_int().loc[k, 0], ci_hi=fit.conf_int().loc[k, 1], n=len(af),
                         pearson_chi2=fit.pearson_chi2, df_resid=fit.df_resid))
glm_tab = pd.concat([glm_tab, pd.DataFrame(rows)], ignore_index=True)
glm_tab.to_csv(os.path.join(TAB, "table_glm.csv"), index=False)

# ---------- Robustness ----------
rob = []


def add(check, country, label, dc, dm, pc, pm):
    m = measures(dc, dm, pc, pm)
    rob.append(dict(check=check, country=country, period=label, contractor_deaths=dc, military_deaths=dm,
                    contractor_person_years=pc, troop_person_years=pm, **m))


for country, label, years in PERIODS[:3] + PERIODS[5:7]:
    s = p[(p.country == country) & (p.fiscal_year.isin(years))]
    base = pooled(country, years)
    add("0. Main", country, label, *base)
    # 1. hostile military deaths only
    add("1. Hostile military deaths only", country, label, *pooled(country, years, deaths_col="military_deaths_hostile"))
    # 2. Nation Pending allocated in proportion
    pend = pd.to_numeric(s["dba_nation_pending_deaths"], errors="coerce").fillna(0)
    share = s["contractor_deaths_dba"] / s["dba_known_nation_deaths_all_countries"]
    dc2 = s["contractor_deaths_dba"] + pend * share
    add("2. Nation Pending deaths allocated", country, label, dc2.sum(), base[1], base[2], base[3])
    # 4. U.S. and TCN contractors only in the denominator
    pc_nonlocal = (pd.to_numeric(s["contractors_us"]) + pd.to_numeric(s["contractors_tcn"])).sum()
    add("4. Denominator: U.S. and TCN contractors only", country, label, base[0], base[1], pc_nonlocal, base[3])
    # 5. under-reporting multipliers
    # 1.5 and 2.0, plus 2.15, the multiplier Crawford and Lutz (2021) apply to Labor Department counts
    for k in (1.5, 2.0, 2.15):
        add(f"5. Contractor deaths x {k}", country, label, base[0] * k, base[1], base[2], base[3])
rob_tab = pd.DataFrame(rob)

# 3. two-year windows (Afghanistan FY2009-FY2016 in pairs, plus FY2017 alone is dropped)
two = []
for a in range(2009, 2017, 2):
    dc, dm, pc, pm = pooled("Afghanistan", [a, a + 1])
    m = measures(dc, dm, pc, pm)
    two.append(dict(check="3. Two-year windows", country="Afghanistan", period=f"FY{a}-FY{a+1}", contractor_deaths=dc,
                    military_deaths=dm, contractor_person_years=pc, troop_person_years=pm, **m))
rob_tab = pd.concat([rob_tab, pd.DataFrame(two)], ignore_index=True)

# 6. FY2018-FY2020 with low and high troop levels
ext = []
for fy in (2018, 2019, 2020):
    s = p[(p.country == "Afghanistan") & (p.fiscal_year == fy)].iloc[0]
    for lab, col in (("central", "troops"), ("low", "troops_low"), ("high", "troops_high")):
        pm = float(s[col])
        m = measures(s["contractor_deaths_dba"], s["military_deaths"], s["contractors"], pm)
        ext.append(dict(check="6. Approximate troops", country="Afghanistan", period=f"FY{fy} ({lab} troops)",
                        contractor_deaths=s["contractor_deaths_dba"], military_deaths=s["military_deaths"],
                        contractor_person_years=s["contractors"], troop_person_years=pm, **m))
rob_tab = pd.concat([rob_tab, pd.DataFrame(ext)], ignore_index=True)
rob_tab.to_csv(os.path.join(TAB, "table_robustness.csv"), index=False)

# ---------- Nationality and exposure (Afghanistan) ----------
nat = []
for _, r in p[p.country == "Afghanistan"].iterrows():
    pc = r["contractors"]
    pm = r["troops"]
    tcn = r["contractors_tcn"]
    row = dict(fiscal_year=r.fiscal_year, troops=pm, contractors=pc, share_us=r.share_us, share_tcn=r.share_tcn,
               share_local=r.share_local, tcn_person_years=tcn)
    if pd.notna(pm):
        row["tcn_share_of_us_side_personnel"] = tcn / (pc + pm)
        row["troop_share_of_us_side_personnel"] = pm / (pc + pm)
    if pd.notna(r["contractor_deaths_dba"]) and pc > 0:
        rate = r["contractor_deaths_dba"] / pc
        row["equal_risk_tcn_deaths"] = rate * tcn
        row["equal_risk_local_deaths"] = rate * r["contractors_local"]
        row["equal_risk_us_deaths"] = rate * r["contractors_us"]
    nat.append(row)
nat = pd.DataFrame(nat)
nat.to_csv(os.path.join(TAB, "table_nationality_afghanistan.csv"), index=False)

# Correlation of TCN share with log troops, FY2009-FY2017 (descriptive)
s = nat[nat.fiscal_year.between(2009, 2017)]
rho = stats.spearmanr(np.log(s.troops), s.share_tcn)
pd.DataFrame([dict(measure="Spearman correlation, TCN share of contractors vs ln troops, FY2009-FY2017",
                   rho=rho.statistic, p=rho.pvalue, n=len(s))]).to_csv(os.path.join(TAB, "table_tcn_correlation.csv"), index=False)

# ---------- Cumulative totals ----------
cum = []
for country, years in (("Afghanistan", range(2009, 2022)), ("Iraq", range(2009, 2022))):
    s = p[(p.country == country) & (p.fiscal_year.isin(years))]
    cum.append(dict(country=country, years=f"FY{min(years)}-FY{max(years)}",
                    military_deaths=int(s.military_deaths.sum()), contractor_deaths_dba=int(s.contractor_deaths_dba.sum()),
                    contractor_share=s.contractor_deaths_dba.sum() / (s.contractor_deaths_dba.sum() + s.military_deaths.sum())))
pd.DataFrame(cum).to_csv(os.path.join(TAB, "table_cumulative.csv"), index=False)

# ---------- Guard-service contracts (S206) by agency ----------
g = pd.read_csv(os.path.join(ROOT, "data", "raw", "us-guard-spending", "s206_transactions.csv.gz"),
                usecols=["fiscal_year", "obligation_usd", "awarding_agency", "funding_agency", "pop_country_name", "pop_country_code"],
                low_memory=False)
g = g[g.pop_country_code.isin(["AFG", "IRQ"])]
g["country"] = g.pop_country_code.map({"AFG": "Afghanistan", "IRQ": "Iraq"})


def agency_group(a):
    return {"Department of Defense": "Defense", "Department of State": "State"}.get(str(a), "Other")


g["agency"] = g.awarding_agency.map(agency_group)
tab = g.groupby(["country", "agency"]).obligation_usd.sum().unstack(fill_value=0) / 1e6
tab["total"] = tab.sum(axis=1)
tab.to_csv(os.path.join(TAB, "table_guard_contracts_by_agency_musd.csv"))
g["period"] = np.where(g.fiscal_year <= 2011, "FY2008-FY2011", "FY2012-FY2026")
tab2 = g.groupby(["country", "period", "agency"]).obligation_usd.sum().unstack(fill_value=0) / 1e6
tab2.to_csv(os.path.join(TAB, "table_guard_contracts_by_agency_period_musd.csv"))

pd.set_option("display.width", 250, "display.max_columns", 40)
cols = ["country", "fiscal_year", "troops", "contractors", "military_deaths", "contractor_deaths_dba", "share_deaths",
        "share_personnel", "rate_troops", "rate_contractors", "rate_ratio", "rate_ratio_lo", "rate_ratio_hi"]
print(yearly[cols].round(3).to_string())
print(periods.round(3).to_string())
print(decomp.round(3).to_string())
print(glm_tab.round(4).to_string())
print(rob_tab[["check", "country", "period", "share_deaths", "rate_troops", "rate_contractors", "rate_ratio", "rate_ratio_lo", "rate_ratio_hi"]].round(3).to_string())
print(nat.round(3).to_string())
print(pd.read_csv(os.path.join(TAB, "table_tcn_correlation.csv")).to_string())
print(pd.read_csv(os.path.join(TAB, "table_cumulative.csv")).to_string())
print(tab.round(1).to_string())
print(tab2.round(1).to_string())

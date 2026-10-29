"""Figures 1-4. Input: data/clean/*.csv and output/tables/*.csv. Output: output/figures/*.png"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "output", "figures")
os.makedirs(FIG, exist_ok=True)
CLEAN = os.path.join(ROOT, "data", "clean")
TAB = os.path.join(ROOT, "output", "tables")
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 9,
                     "legend.frameon": False, "axes.unicode_minus": False})


def qdate(fy, q):
    """Middle month of a fiscal quarter, as a decimal year (FY Q1 = Oct-Dec of the previous year)."""
    month = {1: 11, 2: 2, 3: 5, 4: 8}[q]
    year = fy - 1 if q == 1 else fy
    return year + (month - 0.5) / 12


# ---------- Figure 1: Afghanistan, troops and contractors by nationality, quarterly ----------
c = pd.read_csv(os.path.join(CLEAN, "contractors_quarterly.csv"))
c = c[c.country == "Afghanistan"].sort_values(["fiscal_year", "quarter"])
t = pd.read_csv(os.path.join(CLEAN, "troops_quarterly_crs.csv"))
t = t[(t.country == "Afghanistan") & (t.troops_note.str.startswith("Boots"))].copy()
t["troops"] = t["troops"].astype(float)
t = t[(t.fiscal_year > 2008) | ((t.fiscal_year == 2008) & (t.quarter >= 3))]  # same quarters as the census
a = pd.read_csv(os.path.join(ROOT, "data", "raw", "approx", "afghanistan_troops_fy2018_2020_approx.csv"))
x = [qdate(f, q) for f, q in zip(c.fiscal_year, c.quarter)]
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.stackplot(x, c.us_citizens / 1000, c.third_country_nationals / 1000, c.local_nationals / 1000,
             colors=["#4d4d4d", "#9a9a9a", "#d9d9d9"],
             labels=["Contractors: U.S. citizens", "Contractors: third-country nationals", "Contractors: local nationals"])
ax.plot([qdate(f, q) for f, q in zip(t.fiscal_year, t.quarter)], t.troops / 1000, color="black", linewidth=1.6,
        label="U.S. troops (official count)")
ax.plot([qdate(f, q) for f, q in zip(a.fiscal_year, a.quarter)], a.troops_central / 1000, color="black", linewidth=1.6,
        linestyle=(0, (2, 1.5)), label="U.S. troops (approximate)")
ax.set_ylabel("Thousands of people")
ax.set_xlabel("Calendar year (each quarter plotted at its midpoint)")
ax.set_xlim(2008.3, 2021.8)
# DoD's fourth-quarter FY2010 census said the earlier FY2010 counts were inflated by counting errors
ax.set_ylim(0, 138)
ax.annotate("FY2010 Q1–Q3: counts that DoD later said\nwere inflated by counting errors", xy=(qdate(2010, 2), 112.6),
            xytext=(2008.45, 130), fontsize=7.5, va="center",
            arrowprops=dict(arrowstyle="-", color="black", linewidth=0.7, shrinkA=2, shrinkB=1))
ax.set_xticks(range(2009, 2022, 2))
ax.legend(loc="upper right", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "figure1_afghanistan_personnel.png"), dpi=300)
plt.close(fig)

# ---------- Figure 2: deaths and shares by fiscal year, Afghanistan ----------
y = pd.read_csv(os.path.join(TAB, "table_yearly_panel.csv"))
af = y[y.country == "Afghanistan"].sort_values("fiscal_year")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5.6), sharex=True)
ax1.plot(af.fiscal_year, af.military_deaths, color="black", marker="o", markersize=3.5, linewidth=1.3, label="U.S. military deaths (DCAS)")
ax1.plot(af.fiscal_year, af.contractor_deaths_dba, color="black", marker="s", markersize=3.5, linewidth=1.3,
         linestyle="--", label="Contractor death cases (Defense Base Act)")
ax1.set_ylabel("Deaths or death cases\nper fiscal year")
ax1.legend(loc="upper right", fontsize=8)
ax1.set_title("A. Deaths", loc="left", fontsize=9)
ax2.plot(af.fiscal_year, 100 * af.share_deaths, color="black", marker="o", markersize=3.5, linewidth=1.3, label="Contractor share of deaths")
sp = af.dropna(subset=["share_personnel"])
official = sp[sp.fiscal_year <= 2017]
approx = sp[sp.fiscal_year >= 2017]
ax2.plot(official.fiscal_year, 100 * official.share_personnel, color="#777777", linewidth=1.3, marker="^", markersize=3.5,
         label="Contractor share of personnel (official troop counts)")
ax2.plot(approx.fiscal_year, 100 * approx.share_personnel, color="#777777", linewidth=1.3, linestyle=(0, (2, 1.5)),
         label="Contractor share of personnel (approximate troop levels,\nhollow markers)")
ap2 = approx[approx.fiscal_year >= 2018]
ax2.plot(ap2.fiscal_year, 100 * ap2.share_personnel, linestyle="none", marker="^", markersize=3.5, color="#777777",
         markerfacecolor="white")
ax2.set_ylim(0, 100)
ax2.set_ylabel("Percent")
ax2.legend(loc="lower right", fontsize=8)
ax2.set_title("B. Contractors' share of deaths and of personnel", loc="left", fontsize=9)
ax2.set_xticks(range(2009, 2022))
ax2.set_xticklabels([f"{v % 100:02d}" for v in range(2009, 2022)])
ax2.set_xlabel("Fiscal year (2009 to 2021)")
fig.tight_layout()
fig.savefig(os.path.join(FIG, "figure2_afghanistan_deaths_shares.png"), dpi=300)
plt.close(fig)

# ---------- Figure 3: death rates per 1,000 person-years with 95% CIs ----------
r = af.dropna(subset=["rate_troops"]).copy()
fig, ax = plt.subplots(figsize=(7, 3.8))
off = 0.12
for col, lo, hi, mk, lab, dx in (("rate_troops", "rate_troops_lo", "rate_troops_hi", "o", "U.S. troops", -off),
                                 ("rate_contractors", "rate_contractors_lo", "rate_contractors_hi", "s", "Contractors (reported deaths)", off)):
    for part, face in ((r[r.fiscal_year <= 2017], "black"), (r[r.fiscal_year >= 2018], "white")):
        if col == "rate_contractors":
            face = "black"  # contractor rates do not use troop levels
        ax.errorbar(part.fiscal_year + dx, part[col], yerr=[part[col] - part[lo], part[hi] - part[col]], fmt=mk,
                    color="black", markerfacecolor=face, markersize=4.5, elinewidth=0.9, capsize=2,
                    label=lab if part.fiscal_year.min() <= 2017 else None)
ax.axvline(2017.5, color="grey", linewidth=0.8)
ax.text(2017.65, 0.97, "Troop rates use\napproximate troop levels\n(hollow markers)", fontsize=7.5, va="top", transform=ax.get_xaxis_transform())
ax.set_ylabel("Deaths per 1,000 person-years")
ax.set_ylim(0, None)
ax.set_xticks(range(2009, 2021))
ax.set_xticklabels([f"{v % 100:02d}" for v in range(2009, 2021)])
ax.set_xlabel("Fiscal year (2009 to 2020)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "figure3_afghanistan_death_rates.png"), dpi=300)
plt.close(fig)

# ---------- Figure 4: nationality shares, Afghanistan ----------
n = pd.read_csv(os.path.join(TAB, "table_nationality_afghanistan.csv"))
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot(n.fiscal_year, 100 * n.share_local, color="#9a9a9a", linewidth=1.3, marker="v", markersize=3.5, label="Local nationals, % of contractors")
ax.plot(n.fiscal_year, 100 * n.share_tcn, color="black", linewidth=1.5, marker="o", markersize=3.5, label="Third-country nationals, % of contractors")
ax.plot(n.fiscal_year, 100 * n.share_us, color="black", linewidth=1.2, linestyle="--", marker="s", markersize=3.2, label="U.S. citizens, % of contractors")
tt = n.dropna(subset=["tcn_share_of_us_side_personnel"])
ax.plot(tt.fiscal_year, 100 * tt.tcn_share_of_us_side_personnel, color="black", linewidth=1.2, linestyle=":", marker="D",
        markersize=3.2, label="Third-country nationals, % of troops plus contractors\n(hollow markers: approximate troop levels)")
ap = tt[tt.fiscal_year >= 2018]
ax.plot(ap.fiscal_year, 100 * ap.tcn_share_of_us_side_personnel, linestyle="none", marker="D", markersize=3.2,
        color="black", markerfacecolor="white")
ax.set_ylim(0, 80)
ax.set_ylabel("Percent")
ax.set_xticks(range(2009, 2022))
ax.set_xticklabels([f"{v % 100:02d}" for v in range(2009, 2022)])
ax.set_xlabel("Fiscal year (2009 to 2021)")
ax.legend(loc="upper right", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "figure4_afghanistan_nationality.png"), dpi=300)
plt.close(fig)
print("figures written to", FIG)

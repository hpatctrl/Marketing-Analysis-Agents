"""Run the retail co-brand launch case end to end and save every output used in the memo."""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from src import assumptions as A  # noqa: E402
from src.model import unit_economics, compare_strategies, channel_view, program_pnl, set_scenario  # noqa: E402

OUT = os.path.join(HERE, "reports")
FIG = os.path.join(OUT, "figures")
os.makedirs(FIG, exist_ok=True)

NAVY, BLUE, TEAL, GRAY = "#1B2A4A", "#2563A8", "#0F6E56", "#8A94A6"
money = lambda v, d=1: ("−" if v < 0 else "") + f"\\${abs(v):,.{d}f}"
plt.rcParams.update({"text.usetex": False, "font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": "#C5CDD8", "axes.grid": True,
                     "grid.color": "#E6E9EF", "grid.linewidth": 0.8, "axes.axisbelow": True})

unit = unit_economics()
strat = compare_strategies(unit)
rec = A.STRATEGIES[A.RECOMMENDED]
chan = channel_view(unit, rec)

# Stress: same strategies under a downturn
set_scenario(**A.STRESS)
stress = compare_strategies(unit_economics())[["strategy", "annual_loss_rate", "issuer_value", "program_value"]]
stress.columns = ["strategy", "stress_loss_rate", "stress_issuer_value", "stress_program_value"]
set_scenario()
strat = strat.merge(stress, on="strategy")

# Deal structure: who funds the account bounty. Moving the bounty to the retailer
# transfers value between the parties; total program value is unchanged.
set_scenario()
cur = compare_strategies(unit_economics()).set_index("strategy").loc[A.RECOMMENDED]
set_scenario(bounty=A.NEGOTIATED_ISSUER_BOUNTY)
neg = compare_strategies(unit_economics()).set_index("strategy").loc[A.RECOMMENDED]
set_scenario()
transfer = neg.issuer_value - cur.issuer_value
deal = [dict(terms="Current terms: issuer pays the account bounty", issuer_value=cur.issuer_value,
             retailer_value=cur.retailer_value, program_value=cur.program_value),
        dict(terms="Negotiated: retailer funds the account bounty", issuer_value=neg.issuer_value,
             retailer_value=cur.retailer_value - transfer, program_value=cur.program_value)]
deal = pd.DataFrame(deal)

# P&L for the recommended strategy under negotiated terms
set_scenario(bounty=A.NEGOTIATED_ISSUER_BOUNTY)
unit_neg = unit_economics()
pnl = program_pnl(unit_neg, rec)
set_scenario()

unit.round(4).to_csv(os.path.join(OUT, "unit_economics.csv"), index=False)
strat.round(4).to_csv(os.path.join(OUT, "strategy_comparison.csv"), index=False)
chan.round(4).to_csv(os.path.join(OUT, "channel_value_recommended.csv"), index=False)
deal.round(0).to_csv(os.path.join(OUT, "deal_structure.csv"), index=False)
pnl.round(0).to_csv(os.path.join(OUT, "program_pnl_recommended.csv"), index=False)

# Figure 1: program value by strategy (issuer vs retailer), $M
fig, ax = plt.subplots(figsize=(8.6, 4.0))
labels = [r.strategy.split(". ")[1].replace("Co-brand card ", "Co-brand card\n").replace("Prime-only co-brand card", "Prime-only\nco-brand card").replace("Product ladder", "Product ladder\n(store + secured)")
          + f"\napproval {r.approval_rate:.0%} · loss {r.annual_loss_rate:.1%}" for r in strat.itertuples()]
x = range(len(strat))
w = 0.38
b1 = ax.bar([i - w / 2 for i in x], strat.issuer_value / 1e6, w, color=NAVY, label="Issuer value after marketing")
b2 = ax.bar([i + w / 2 for i in x], strat.retailer_value / 1e6, w, color=TEAL, label="Retailer margin on incremental sales")
for bars in (b1, b2):
    for bar in bars:
        v = bar.get_height()
        ax.annotate(money(v) + "M", (bar.get_x() + bar.get_width() / 2, max(v, 0)), ha="center", va="bottom",
                    fontsize=9, xytext=(0, 3), textcoords="offset points")
ax.axhline(0, color="#5A6478", linewidth=1)
ax.set_xticks(list(x)); ax.set_xticklabels(labels, fontsize=9)
ax.set_ylim(min(0, strat.issuer_value.min() / 1e6) - 1.5, strat.retailer_value.max() / 1e6 * 1.18)
ax.set_ylabel("36-month value, \\$M")
ax.set_title("Program value by strategy (one year of applications)", loc="left", fontsize=12, color=NAVY, fontweight="bold", pad=24)
ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "strategy_value.png"), dpi=160); plt.close(fig)

# Figure 2: issuer value per application by channel (ladder)
c2 = chan.sort_values("issuer_value_per_app")
fig, ax = plt.subplots(figsize=(8, 3.2))
bars = ax.barh(c2.channel, c2.issuer_value_per_app, color=[BLUE if v >= 0 else "#B3261E" for v in c2.issuer_value_per_app], height=0.55)
for bar, (_, r) in zip(bars, c2.iterrows()):
    ax.annotate(f"{money(r.issuer_value_per_app, 0)} per app · CAC {money(r.risk_adjusted_cac, 0)} · payback {r.payback_months_wavg:.0f} mo",
                (max(bar.get_width(), 0), bar.get_y() + bar.get_height() / 2), va="center", fontsize=8.5, xytext=(4, 0), textcoords="offset points")
ax.axvline(0, color="#5A6478", linewidth=1)
ax.set_xlim(min(0, c2.issuer_value_per_app.min()) * 1.3, c2.issuer_value_per_app.max() * 2.2)
ax.set_xlabel("Issuer value per application after marketing (\\$, 36 months)")
ax.set_title("Channel value under the recommended strategy", loc="left", fontsize=12, color=NAVY, fontweight="bold")
ax.grid(axis="y", visible=False)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "channel_value.png"), dpi=160); plt.close(fig)

# Figure 3: three-year pre-tax income and the CECL reserve build ($M)
fig, ax = plt.subplots(figsize=(8, 3.2))
yrs = [f"Year {y}" for y in pnl.year]
ax.bar(yrs, pnl.pretax_income / 1e6, color=NAVY, width=0.5, label="Pre-tax income")
for i, r in pnl.iterrows():
    ax.annotate(f"{money(r.pretax_income/1e6)}M\n(incl. reserve build {money(-r.reserve_build/1e6)}M)", (i, r.pretax_income / 1e6),
                ha="center", va="bottom" if r.pretax_income >= 0 else "top", fontsize=8.5,
                xytext=(0, 3 if r.pretax_income >= 0 else -3), textcoords="offset points")
ax.axhline(0, color="#5A6478", linewidth=1)
ax.set_ylabel("\\$M")
lo, hi = min(0, pnl.pretax_income.min() / 1e6), max(0, pnl.pretax_income.max() / 1e6)
ax.set_ylim(lo * 1.35 - 0.5, hi * 1.35 + 1.0)
ax.set_title("Recommended strategy: program P&L, pre-tax (negotiated terms)", loc="left", fontsize=12, color=NAVY, fontweight="bold")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "program_pnl.png"), dpi=160); plt.close(fig)

summary = {
    "strategies": strat.round(4).to_dict(orient="records"),
    "channels_recommended": chan.round(2).to_dict(orient="records"),
    "deal_structure": deal.round(0).to_dict(orient="records"),
    "pnl_recommended": pnl.round(0).to_dict(orient="records"),
}
with open(os.path.join(OUT, "results.json"), "w") as f:
    json.dump(summary, f, indent=2, default=float)

pd_fmt = lambda v: f"{v:,.0f}"
print(unit[["product", "segment", "issuer_npv", "retailer_value", "annual_loss_rate"]].round(1).to_string(index=False))
print(strat[["strategy", "approval_rate", "booked_accounts", "annual_loss_rate", "risk_adjusted_cac", "issuer_value", "retailer_value", "program_value", "stress_loss_rate", "stress_issuer_value", "stress_program_value"]].round(3).to_string(index=False))
print(deal.round(0).to_string(index=False))
print(chan[["channel", "approval_rate", "risk_adjusted_cac", "annual_loss_rate", "issuer_value_per_app", "payback_months_wavg"]].round(2).to_string(index=False))
print(pnl.round(0).T.to_string())

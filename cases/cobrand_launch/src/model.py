"""Retail co-brand card launch: marketing x credit x finance in one model."""
from __future__ import annotations

import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
from shared.customer_npv import CardTerms, card_npv, payback_month  # noqa: E402

from . import assumptions as A  # noqa: E402


SCEN = {"pd_mult": 1.0, "revolve_mult": 1.0, "bounty": None}


def set_scenario(pd_mult=1.0, revolve_mult=1.0, bounty=None):
    SCEN.update(pd_mult=pd_mult, revolve_mult=revolve_mult, bounty=bounty)


def terms(product: str, seg: str) -> CardTerms:
    base = dict(A.COMMON)
    if product == "GP":
        base.update(A.GP[seg]); base["annual_pd"] = A.PD[seg]
    elif product == "PLCC":
        base.update(A.PLCC[seg]); base["annual_pd"] = A.PD[seg]
    elif product == "SECURED":
        base.update(A.SECURED[seg])  # its own upfront cost and bounty override COMMON
    else:
        raise ValueError(product)
    base["retailer_margin"] = A.RETAILER_MARGIN
    base["annual_pd"] = min(base["annual_pd"] * SCEN["pd_mult"], 0.95)
    base["revolve_share"] = base["revolve_share"] * SCEN["revolve_mult"]
    if SCEN["bounty"] is not None:
        base["partner_bounty"] = SCEN["bounty"]
    return CardTerms(**base)


def unit_economics() -> pd.DataFrame:
    """NPV per booked account for every product x segment cell."""
    rows = []
    cells = [("GP", s) for s in A.GP] + [("PLCC", s) for s in A.PLCC] + [("SECURED", s) for s in A.SECURED]
    gp_sub = card_npv(terms("GP", "subprime"), A.MONTHS, A.DISCOUNT_RATE).npv
    for prod, seg in cells:
        t = terms(prod, seg)
        r = card_npv(t, A.MONTHS, A.DISCOUNT_RATE)
        npv = r.npv
        grad = 0.0
        if prod == "SECURED":  # option value of graduating to the unsecured co-brand card at month 12
            grad = A.GRADUATION_RATE * gp_sub / (1 + A.DISCOUNT_RATE) ** 1
            npv += grad
        lgd_eff = t.lgd * max(t.line * t.utilization - t.deposit, 0) / (t.line * t.utilization)
        rows.append(dict(product=prod, segment=seg, line=t.line, apr=t.apr, annual_pd=t.annual_pd,
                         annual_loss_rate=t.annual_pd * lgd_eff, avg_balance=round(r.avg_balance, 2),
                         interest=r.interest, interchange=r.interchange, rewards=-r.rewards,
                         losses=-r.losses, funding=-r.funding, servicing=-r.servicing,
                         upfront_and_bounty=-r.upfront, graduation_value=grad,
                         issuer_npv=npv, retailer_value=r.retailer_value))
    return pd.DataFrame(rows)


def strategy_cells(unit: pd.DataFrame, strategy: dict, growth: float = 1.0) -> pd.DataFrame:
    """Channel x segment cells for one strategy: response x approval x NPV."""
    u = unit.set_index(["product", "segment"])
    rows = []
    for ch, c in A.CHANNELS.items():
        for seg, share in c["mix"].items():
            apps = c["apps"] * growth * share
            prod = strategy[seg]
            approved = apps * (1 - A.FRAUD_POLICY_DECLINE) if prod else 0.0
            booked = approved * (A.SECURED_DEPOSIT_TAKEUP if prod == "SECURED" else 1.0)
            cell = u.loc[(prod, seg)] if prod else None
            rows.append(dict(channel=ch, segment=seg, product=prod or "decline", applications=apps,
                             approved=approved, booked=booked, spend=apps * c["cost_per_app"],
                             issuer_npv=booked * (cell.issuer_npv if prod else 0),
                             retailer_value=booked * (cell.retailer_value if prod else 0),
                             balance=booked * (cell.avg_balance if prod else 0),
                             loss_dollars=booked * (cell.avg_balance * cell.annual_loss_rate if prod else 0)))
    df = pd.DataFrame(rows)
    df["issuer_value"] = df.issuer_npv - df.spend
    df["program_value"] = df.issuer_value + df.retailer_value
    return df


def compare_strategies(unit: pd.DataFrame) -> pd.DataFrame:
    out = []
    for name, strat in A.STRATEGIES.items():
        d = strategy_cells(unit, strat)
        out.append(dict(strategy=name, applications=d.applications.sum(),
                        approval_rate=d.approved.sum() / d.applications.sum(),
                        booked_accounts=d.booked.sum(),
                        annual_loss_rate=d.loss_dollars.sum() / d.balance.sum(),
                        marketing_spend=d.spend.sum(),
                        risk_adjusted_cac=d.spend.sum() / d.booked.sum(),
                        issuer_value=d.issuer_value.sum(),
                        retailer_value=d.retailer_value.sum(),
                        program_value=d.program_value.sum(),
                        issuer_value_per_app=d.issuer_value.sum() / d.applications.sum(),
                        meets_partner_target=d.approved.sum() / d.applications.sum() >= A.PARTNER_APPROVAL_TARGET))
    return pd.DataFrame(out)


def channel_view(unit: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    d = strategy_cells(unit, strategy)
    g = d.groupby("channel", sort=False).agg(applications=("applications", "sum"), approved=("approved", "sum"),
                                             booked=("booked", "sum"), spend=("spend", "sum"),
                                             issuer_value=("issuer_value", "sum"), program_value=("program_value", "sum"),
                                             loss_dollars=("loss_dollars", "sum"), balance=("balance", "sum")).reset_index()
    g["approval_rate"] = g.approved / g.applications
    g["risk_adjusted_cac"] = g.spend / g.booked
    g["annual_loss_rate"] = g.loss_dollars / g.balance
    g["issuer_value_per_app"] = g.issuer_value / g.applications
    # payback for the channel's blended account: use the booked-weighted cells
    pb = []
    for ch in g.channel:
        cells = d[(d.channel == ch) & (d.booked > 0)]
        months = []
        for _, r in cells.iterrows():
            cac = r.spend / r.booked
            months.append((payback_month(terms(r["product"], r.segment), cac) or 99, r.booked))
        pb.append(sum(m * w for m, w in months) / sum(w for _, w in months))
    g["payback_months_wavg"] = pb
    return g.drop(columns=["loss_dollars", "balance"])


def program_pnl(unit: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """Three-year program P&L from monthly cohorts, with a simple CECL reserve."""
    u = unit.set_index(["product", "segment"])
    years = len(A.APP_GROWTH)
    T = years * 12
    cols = ["interest", "interchange", "rewards", "partner_bounty", "upfront", "funding", "servicing",
            "net_charge_offs", "marketing", "balances", "accounts", "reserve_req"]
    m = {k: [0.0] * T for k in cols}
    for y, gr in enumerate(A.APP_GROWTH):
        d = strategy_cells(unit, strategy, gr)
        d = d[d.booked > 0].groupby(["product", "segment"], as_index=False).booked.sum()
        spend_y = sum(c["apps"] * gr * c["cost_per_app"] for c in A.CHANNELS.values())
        for mo in range(12):
            start = y * 12 + mo
            m["marketing"][start] += spend_y / 12
            for _, r in d.iterrows():
                t = terms(r["product"], r.segment)
                n = r.booked / 12
                pd_m = 1 - (1 - t.annual_pd) ** (1 / 12)
                bal = t.line * t.utilization
                lgd_eff = t.lgd * max(bal - t.deposit, 0) / bal
                m["partner_bounty"][start] += n * t.partner_bounty
                m["upfront"][start] += n * t.upfront_cost
                alive = n
                for k in range(start, T):
                    m["interest"][k] += alive * bal * t.revolve_share * t.apr / 12
                    m["interchange"][k] += alive * t.spend_m * t.interchange
                    m["rewards"][k] += alive * t.spend_m * t.rewards_rate
                    m["funding"][k] += alive * bal * t.funding_rate / 12
                    m["servicing"][k] += alive * t.servicing_m
                    m["net_charge_offs"][k] += alive * pd_m * bal * lgd_eff
                    m["balances"][k] += alive * bal
                    m["accounts"][k] += alive
                    m["reserve_req"][k] += alive * bal * min(t.annual_pd * lgd_eff * A.CECL_LIFE_YEARS, 1.0)
                    alive *= (1 - pd_m) * (1 - t.attrition_m)
    rows = []
    prev_reserve = 0.0
    for y in range(years):
        s = slice(y * 12, y * 12 + 12)
        tot = {k: sum(m[k][s]) for k in cols if k not in ("balances", "accounts", "reserve_req")}
        end_bal = m["balances"][y * 12 + 11]
        reserve = m["reserve_req"][y * 12 + 11]
        provision = tot["net_charge_offs"] + (reserve - prev_reserve)
        revenue = tot["interest"] + tot["interchange"]
        pretax = (revenue - tot["rewards"] - tot["funding"] - provision - tot["servicing"]
                  - tot["marketing"] - tot["partner_bounty"] - tot["upfront"])
        rows.append(dict(year=y + 1, interest_income=tot["interest"], interchange=tot["interchange"],
                         rewards=-tot["rewards"], cost_of_funds=-tot["funding"],
                         net_charge_offs=-tot["net_charge_offs"], reserve_build=-(reserve - prev_reserve),
                         servicing=-tot["servicing"], marketing=-tot["marketing"],
                         partner_bounty_and_upfront=-(tot["partner_bounty"] + tot["upfront"]),
                         pretax_income=pretax, ending_receivables=end_bal,
                         open_accounts=m["accounts"][y * 12 + 11], cecl_reserve=reserve,
                         warehouse_borrowing=end_bal * (1 - A.INELIGIBLE_SHARE) * A.ADVANCE_RATE,
                         equity_funding_need=end_bal - end_bal * (1 - A.INELIGIBLE_SHARE) * A.ADVANCE_RATE))
        prev_reserve = reserve
    return pd.DataFrame(rows)

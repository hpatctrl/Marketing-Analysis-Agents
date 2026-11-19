"""Shared customer economics engine for the Marketing & Analysis agent team.

The core identity every agent works from:

    value of a marketing cell = applications x approval rate x NPV per approved account
                                - applications x cost per application

NPV per account is built month by month from the same components a card or loan
P&L uses, so marketing, credit and finance compare options on one basis.
All inputs are assumptions supplied by the caller; nothing here is observed data.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass
class CardTerms:
    """Assumptions for one product x segment cell of a revolving card."""
    line: float                  # credit line ($)
    utilization: float           # average balance / line
    revolve_share: float         # share of balance that pays interest
    apr: float                   # purchase APR
    spend_m: float               # monthly purchase volume on the card ($)
    interchange: float           # issuer interchange (or merchant fee) rate on spend
    rewards_rate: float          # issuer-funded rewards cost as a share of spend
    annual_pd: float             # annual probability of charge-off
    lgd: float = 0.90            # loss given default on the unsecured balance
    attrition_m: float = 0.010   # monthly voluntary closure rate
    funding_rate: float = 0.055  # annual cost of funds on balances
    servicing_m: float = 2.50    # monthly servicing cost per open account ($)
    annual_fee: float = 0.0
    deposit: float = 0.0         # cash collateral held (secured cards)
    upfront_cost: float = 0.0    # origination cost after marketing: fraud, KYC, card issue ($)
    partner_bounty: float = 0.0  # paid to the retail partner per booked account ($)
    partner_rev_share: float = 0.0  # share of interest + fee income paid to the partner
    retailer_spend_m: float = 0.0   # incremental monthly spend at the partner (for program value)
    retailer_margin: float = 0.0    # partner gross margin on that incremental spend


@dataclass
class NPVResult:
    interest: float = 0.0
    interchange: float = 0.0
    fees: float = 0.0
    rewards: float = 0.0
    partner_share: float = 0.0
    losses: float = 0.0
    funding: float = 0.0
    servicing: float = 0.0
    upfront: float = 0.0
    npv: float = 0.0
    cum_default_rate: float = 0.0
    avg_balance: float = 0.0
    retailer_value: float = 0.0
    components: dict = field(default_factory=dict)


def card_npv(t: CardTerms, months: int = 36, discount_rate: float = 0.12) -> NPVResult:
    """Expected NPV per booked account over `months`, discounted monthly."""
    pd_m = 1 - (1 - t.annual_pd) ** (1 / 12)
    balance = t.line * t.utilization
    exposure_lgd = t.lgd * max(balance - t.deposit, 0.0) / balance if balance > 0 else 0.0
    r = NPVResult()
    alive = 1.0
    defaulted = 0.0
    bal_sum = 0.0
    for m in range(1, months + 1):
        df = 1 / (1 + discount_rate / 12) ** m
        interest = balance * t.revolve_share * t.apr / 12
        fees = t.annual_fee / 12
        inter = t.spend_m * t.interchange
        rewards = t.spend_m * t.rewards_rate
        partner = (interest + fees) * t.partner_rev_share
        funding = balance * t.funding_rate / 12
        loss = pd_m * balance * exposure_lgd
        r.interest += alive * interest * df
        r.fees += alive * fees * df
        r.interchange += alive * inter * df
        r.rewards += alive * rewards * df
        r.partner_share += alive * partner * df
        r.funding += alive * funding * df
        r.servicing += alive * t.servicing_m * df
        r.losses += alive * loss * df
        r.retailer_value += alive * t.retailer_spend_m * t.retailer_margin * df
        bal_sum += alive * balance
        defaulted += alive * pd_m
        alive *= (1 - pd_m) * (1 - t.attrition_m)
    r.upfront = t.upfront_cost + t.partner_bounty
    r.npv = (r.interest + r.fees + r.interchange - r.rewards - r.partner_share
             - r.losses - r.funding - r.servicing - r.upfront)
    r.cum_default_rate = defaulted
    r.avg_balance = bal_sum / months
    r.components = {k: round(v, 2) for k, v in asdict(r).items() if isinstance(v, float)}
    return r


def cell_value(applications: float, approval_rate: float, npv_per_account: float,
               cost_per_application: float) -> dict:
    """Response x approval x NPV, net of acquisition spend, for one marketing cell."""
    booked = applications * approval_rate
    spend = applications * cost_per_application
    value = booked * npv_per_account - spend
    return {
        "applications": applications,
        "booked": booked,
        "spend": spend,
        "risk_adjusted_cac": spend / booked if booked else float("inf"),
        "value": value,
        "value_per_application": value / applications if applications else 0.0,
    }


def payback_month(t: CardTerms, acquisition_cost: float, months: int = 60) -> int | None:
    """First month in which undiscounted cumulative contribution covers acquisition and upfront cost."""
    pd_m = 1 - (1 - t.annual_pd) ** (1 / 12)
    balance = t.line * t.utilization
    exposure_lgd = t.lgd * max(balance - t.deposit, 0.0) / balance if balance > 0 else 0.0
    cum = -(acquisition_cost + t.upfront_cost + t.partner_bounty)
    alive = 1.0
    for m in range(1, months + 1):
        income = balance * t.revolve_share * t.apr / 12 + t.annual_fee / 12 + t.spend_m * t.interchange
        cost = (t.spend_m * t.rewards_rate + (balance * t.revolve_share * t.apr / 12 + t.annual_fee / 12) * t.partner_rev_share
                + balance * t.funding_rate / 12 + t.servicing_m + pd_m * balance * exposure_lgd)
        cum += alive * (income - cost)
        alive *= (1 - pd_m) * (1 - t.attrition_m)
        if cum >= 0:
            return m
    return None

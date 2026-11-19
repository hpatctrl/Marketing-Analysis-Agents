"""Assumptions for the retail co-brand card launch case.

Every number here is an ASSUMPTION chosen to be plausible for a large US membership
retailer launching a card program with a bank or fintech issuer. None of it is
observed data from any company. Change them here; everything downstream reruns.
"""

SEGMENTS = ["prime", "near_prime", "subprime", "thin_file"]

# Annual charge-off probability by segment for an unsecured card
PD = {"prime": 0.020, "near_prime": 0.055, "subprime": 0.120, "thin_file": 0.220}

COMMON = dict(funding_rate=0.055, servicing_m=2.50, upfront_cost=25.0, partner_bounty=40.0, lgd=0.90)
RETAILER_MARGIN = 0.15        # partner contribution margin on incremental sales
FRAUD_POLICY_DECLINE = 0.06   # declined for fraud, identity or ability-to-pay before risk tiering
SECURED_DEPOSIT_TAKEUP = 0.40 # share of secured-card approvals that fund the deposit
GRADUATION_RATE = 0.25        # secured accounts graduating to the unsecured co-brand card at month 12

# Card terms by product and segment
GP = {  # general-purpose co-brand card (network card usable anywhere).
    # Rewards cards earn premium interchange (~1.9% assumed); the issuer funds 1.5% of spend in rewards
    # and the retailer funds the extra in-store bonus, as is typical in co-brand contracts.
    "prime":      dict(line=7000, utilization=0.18, revolve_share=0.40, apr=0.2499, spend_m=700, interchange=0.019, rewards_rate=0.015, attrition_m=0.008, retailer_spend_m=80),
    "near_prime": dict(line=3000, utilization=0.35, revolve_share=0.70, apr=0.2799, spend_m=400, interchange=0.019, rewards_rate=0.015, attrition_m=0.010, retailer_spend_m=60),
    "subprime":   dict(line=1500, utilization=0.55, revolve_share=0.85, apr=0.2999, spend_m=250, interchange=0.019, rewards_rate=0.015, attrition_m=0.012, retailer_spend_m=45),
    "thin_file":  dict(line=1000, utilization=0.60, revolve_share=0.90, apr=0.2999, spend_m=150, interchange=0.019, rewards_rate=0.015, attrition_m=0.015, retailer_spend_m=35),
}
PLCC = {  # private-label store card (usable only at the retailer); rewards co-funded by the retailer
    "near_prime": dict(line=1500, utilization=0.40, revolve_share=0.75, apr=0.3199, spend_m=150, interchange=0.0, rewards_rate=0.015, attrition_m=0.012, retailer_spend_m=70, servicing_m=2.00),
    "subprime":   dict(line=800,  utilization=0.50, revolve_share=0.85, apr=0.3199, spend_m=120, interchange=0.0, rewards_rate=0.015, attrition_m=0.014, retailer_spend_m=55, servicing_m=2.00),
}
SECURED = {  # deposit-backed card for thin-file applicants; deposit equals the line
    "thin_file": dict(line=300, utilization=0.50, revolve_share=0.60, apr=0.2699, spend_m=100, interchange=0.016, rewards_rate=0.0, attrition_m=0.015, retailer_spend_m=30, deposit=300, annual_pd=0.10, servicing_m=2.00, upfront_cost=15.0, partner_bounty=15.0),
}

# Acquisition channels: applications per year, cost per application, applicant mix
CHANNELS = {
    "In-store point of sale": dict(apps=60000, cost_per_app=12.0, mix={"prime": .40, "near_prime": .27, "subprime": .20, "thin_file": .13}),
    "Online checkout":        dict(apps=25000, cost_per_app=6.0,  mix={"prime": .48, "near_prime": .25, "subprime": .17, "thin_file": .10}),
    "Retailer app":           dict(apps=15000, cost_per_app=4.0,  mix={"prime": .55, "near_prime": .23, "subprime": .14, "thin_file": .08}),
    "Prescreened mail to members": dict(apps=20000, cost_per_app=55.0, mix={"prime": .65, "near_prime": .35, "subprime": 0.0, "thin_file": 0.0}),
    "Paid search and affiliates":  dict(apps=10000, cost_per_app=35.0, mix={"prime": .30, "near_prime": .25, "subprime": .25, "thin_file": .20}),
}
APP_GROWTH = [1.00, 1.15, 1.30]   # application volume index for years 1-3
PARTNER_APPROVAL_TARGET = 0.80    # the retailer's goal: share of applicants who get a "yes" at checkout

# Strategies: which product each segment is offered (None = decline)
STRATEGIES = {
    "A. Prime-only co-brand card": {"prime": "GP", "near_prime": None, "subprime": None, "thin_file": None},
    "B. Co-brand card for all scored": {"prime": "GP", "near_prime": "GP", "subprime": "GP", "thin_file": None},
    "C. Product ladder": {"prime": "GP", "near_prime": "GP", "subprime": "PLCC", "thin_file": "SECURED"},
    "D. Co-brand card + secured card": {"prime": "GP", "near_prime": "GP", "subprime": "GP", "thin_file": "SECURED"},
}
RECOMMENDED = "D. Co-brand card + secured card"

# Downturn stress: default rates x1.5 and revolving balances -20% (customers pay down)
STRESS = dict(pd_mult=1.5, revolve_mult=0.8)

# Deal structure: under negotiated terms the retailer funds the per-account bounty
# (it captures most of the program value through incremental sales)
NEGOTIATED_ISSUER_BOUNTY = 0.0

MONTHS = 36
DISCOUNT_RATE = 0.12
CECL_LIFE_YEARS = 2.0   # simple lifetime-loss proxy: reserve = annual loss rate x expected remaining life
ADVANCE_RATE = 0.85     # warehouse advance rate on eligible receivables
INELIGIBLE_SHARE = 0.04 # delinquent or otherwise ineligible receivables

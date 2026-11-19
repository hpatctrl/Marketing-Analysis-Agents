# Marketing & Analysis Agent Team for Fintech Lenders

**Marketing, credit and finance as one decision.** This repo rebuilds the Capital One Marketing & Analysis operating model as a team of AI agents, with a human business manager accountable for every number.

At Capital One, one analyst owned the whole customer decision: who to target, with what offer, whether to approve, at what line and price, and what it earns. Every option was compared on one measure, the net present value of the customer, and tested in market before rollout. This repo applies that model to fintech lending.

## The shared model

Every agent works from one identity, implemented in [`shared/customer_npv.py`](shared/customer_npv.py):

```
value of a marketing cell = applications x approval rate x NPV per approved account
                            - applications x cost per application
```

Marketing can't buy a cheap channel that loses money on credit, and credit can't tighten in a way that wastes marketing spend, because both answer to the same number.

## The team

| Group | Agents (`.claude/agents/`) |
|---|---|
| Business manager | `business-manager` (orchestrates the engagement; a human owns the decision) |
| Market & customer | `market-intelligence`, `customer-segmentation` |
| Acquisition marketing | `channel-media`, `offer-messaging`, `test-design` |
| Credit | `underwriting-decisioning`, `lines-pricing`, `portfolio-collections` |
| Finance | `npv-ltv`, `fpa-pnl`, `funding-capital-markets` |
| Product | `product-manager`, `lifecycle-crm` |
| Control | `compliance-reviewer`, `independent-validator`, `report-writer` |

Agent definitions use the Claude Code subagent format. Every agent labels numbers as observed, assumed or modeled, saves outputs that the memo can be checked against, and hands off to the independent validator; customer-facing work also goes through the compliance reviewer.

Supporting files:
- [`verticals/`](verticals/): KPIs, public data sources and rules to check for cards, cash advance and EWA, installment, auto, small business and home equity
- [`compliance/checklist.md`](compliance/checklist.md): first-pass marketing, credit and fair-lending checklist (not legal advice)
- [`templates/`](templates/): decision memo and test plan

## Integrated cases

| Case | Question | Status |
|---|---|---|
| [1. Retail co-brand card launch](cases/cobrand_launch/) | Which applicants get which card, through which channels, on what partner terms | Done |
| 2. Cash advance membership growth | Channel mix, limit step-ups and pricing for a cash advance membership | Planned |
| 3. Near-prime installment loans through affiliate marketplaces | Prescreen vs affiliate channels, risk-based pricing and payback as affiliate costs rise | Planned |
| 4. Small-business credit line through an embedded partner | Partner economics, line strategy and funding | Planned |

## Run

```bash
pip install numpy pandas matplotlib pytest
python cases/cobrand_launch/run_case.py
pytest -q tests
```

## Notes

- All cases use public or simulated data with documented assumptions. Results are model outputs, not observed results from any company.
- Compliance reviews here are a first pass, not legal sign-off.

Built by Hiren Patel. Related work: [Cash-Advance-Underwriting](https://github.com/hpatctrl/Cash-Advance-Underwriting).

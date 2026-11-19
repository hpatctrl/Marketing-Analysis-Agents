# Decision memo: launching a retail co-brand card program

**Prepared by:** Hiren Patel, with the Marketing & Analysis agent team  
**Decision:** which customers get which card, through which channels, on what partner terms  
**Decision metric:** 36-month program value (issuer value after marketing + retailer margin on incremental sales), subject to the retailer's 80% approval goal and a downturn test  
**Basis:** simulated from documented assumptions (`src/assumptions.py`) for one year of applications (130,000) at a large US membership retailer. These are model outputs, not observed results from any company.

---

## 1. Recommendation

1. **Offer the co-brand card to prime, near-prime and subprime applicants, and a secured card to thin-file applicants (strategy D).** It produces the highest program value, **$30.4M**, and approves **94%** of applicants, above the retailer's 80% goal.
2. **Negotiate for the retailer to fund the per-account bounty.** The retailer captures about 92% of program value through incremental sales. Moving the bounty raises issuer value from **$2.4M to $6.9M** without changing the program total.
3. **Put acquisition money into the retailer's own channels.** The app, online checkout and in-store point of sale each earn $25–30 per application for the issuer. Prescreened mail loses $12 per application and paid search and affiliates only break even, so both should be retargeted or cut.
4. **Launch through a randomized store pilot with downturn triggers.** In a downturn the issuer side of every strategy loses money, so line-reduction triggers and a loss-sharing clause belong in the contract before launch.

## 2. The options compared (one year of applications, 36-month value)

| Strategy | Approval | Annual loss rate | Issuer value | Retailer value | Program value | Program value in downturn |
|---|---|---|---|---|---|---|
| A. Prime-only co-brand card | 44% | 1.8% | −$1.5M | $17.5M | $16.0M | $11.3M |
| B. Co-brand card for all scored | 84% | 3.7% | $2.4M | $27.5M | $29.9M | $17.0M |
| C. Product ladder (store card for subprime, secured for thin-file) | 94% | 3.2% | $0.4M | $28.5M | $28.9M | $17.4M |
| **D. Co-brand card + secured card** | **94%** | **3.7%** | **$2.4M** | **$28.0M** | **$30.4M** | **$17.2M** |

Downturn: default rates ×1.5 and revolving balances −20%. Retailer value uses an assumed 15% contribution margin on incremental sales.

## 3. Why D wins: marketing, credit and finance together

- **Credit.** Prime-only is the "safe" answer and the worst one. Prime cardholders earn little interest, so the issuer's value is thin ($15 NPV per account); the program's value comes from near-prime ($102) and subprime ($28) customers who revolve. Unsecured cards for thin-file applicants lose $105 per account, so they get a secured card instead.
- **Marketing.** Approval is the retailer's experience metric. Declining 56% of applicants at checkout (strategy A) leaves most of the program's sales lift unused. D says yes to 94% of applicants by offering the right product to each.
- **The store card surprise.** A store card for subprime applicants (strategy C) is the conventional answer because it limits exposure. Under these assumptions it loses $73 per account: the lower line cuts interest income faster than it cuts losses, and it earns no interchange. C has the lowest loss rate (3.2%) but gives up $1.5M of program value versus D. Worth testing, not assuming.
- **Finance.** The secured card loses about $4 per account for the issuer, after counting $6 of value from the 25% of accounts assumed to graduate to the unsecured co-brand card at month 12, and adds $94 of retailer margin per account. It belongs in the program, especially if the partner funds its bounty.

## 4. Channels (strategy D)

| Channel | Approval | Risk-adjusted CAC | Issuer value per application | Payback |
|---|---|---|---|---|
| Retailer app | 94% | $4 | $30 | 23 months |
| Online checkout | 94% | $7 | $29 | 24 months |
| In-store point of sale | 94% | $14 | $25 | 27 months |
| Paid search and affiliates | 94% | $42 | about $0 | 37 months |
| Prescreened mail to members | 94% | $59 | −$12 | 40 months |

Payback is the booked-account-weighted average month in which cumulative contribution covers acquisition and upfront cost.

## 5. P&L and funding (strategy D, negotiated terms, applications growing 15% a year)

| | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Pre-tax income | −$10.8M | −$5.9M | −$1.0M |
| of which CECL reserve build | −$8.7M | −$8.5M | −$8.4M |
| Ending receivables | $114.9M | $230.8M | $347.8M |
| Warehouse borrowing (85% advance, 4% ineligible) | $93.8M | $188.3M | $283.8M |
| Equity funding need | $21.1M | $42.5M | $64.0M |

The program reports losses for three years while it grows because CECL requires reserving lifetime losses when accounts are booked. Before the reserve build, year 3 earns about $7.3M. Board and partner reporting should show vintage-level NPV alongside GAAP results.

## 6. Test plan before full rollout

| Item | Detail |
|---|---|
| Design | Randomize 40 pilot stores: 20 launch D, 20 launch B (thin-file declined). Online and app traffic randomized 50/50 by applicant. |
| Primary metric | Program value per application (issuer NPV proxy at month 6 + incremental retailer sales) |
| Secondary tests | Subprime starting line $1,500 vs $1,000; prescreened mail limited to model-selected near-prime members vs paused |
| Early indicators | Activation in 60 days, first-payment default, 30+ days past due at month 3 and 6, secured deposit funding rate |
| Guardrails | 30+ DPD at month 6 within 1.25× plan; complaints per 1,000 accounts; approval and pricing outcomes by group (fair-lending test) |
| Kill criteria | Month-3 30+ DPD on subprime above 1.5× plan, or any fair-lending gap without a credit-based explanation |

## 7. Compliance first-pass findings (not legal sign-off)

| Finding | Severity | Fix |
|---|---|---|
| Offering a secured card instead of the requested co-brand card is a counteroffer; Reg B requires notice if the applicant doesn't accept | High | Build counteroffer and adverse-action notices into the checkout flow |
| Store-associate incentives per application create sales-practice risk | High | Pay on funded, activated accounts with quality clawbacks; monitor unauthorized-account complaints |
| "Instant approval" or savings claims in store materials | Medium | Use claims the decision rules support; put rewards conditions next to the claim |
| Prescreened mail requires firm offers and the opt-out notice | Medium | Prescreen criteria set before the bureau pull; standard opt-out language |
| Under-21 applicants need independent income or a cosigner (CARD Act) | Medium | Ability-to-pay check in the decision engine |
| Segment and channel targeting could act as a proxy for protected classes | Medium | Review audience definitions and test approval outcomes by group before launch |

## 8. Assumptions that matter most (test these first)

- Incremental retailer spend per cardholder and the 15% margin drive most of program value.
- Subprime default rate (12% a year assumed) decides whether subprime cardholders add or destroy issuer value.
- Revolve rates: prime value depends on 40% of prime balances revolving.
- Partner terms: bounty, rewards co-funding and any revenue share move value between the parties.

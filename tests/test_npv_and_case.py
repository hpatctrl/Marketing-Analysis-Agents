import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from shared.customer_npv import CardTerms, card_npv, cell_value

BASE = dict(line=3000, utilization=0.35, revolve_share=0.7, apr=0.28, spend_m=400,
            interchange=0.019, rewards_rate=0.015, annual_pd=0.05)

def test_higher_default_lowers_npv():
    assert card_npv(CardTerms(**{**BASE, "annual_pd": 0.10})).npv < card_npv(CardTerms(**BASE)).npv

def test_deposit_removes_losses_when_it_covers_balance():
    r = card_npv(CardTerms(**{**BASE, "line": 300, "deposit": 300}))
    assert r.losses == 0

def test_components_add_up():
    r = card_npv(CardTerms(**BASE))
    total = r.interest + r.fees + r.interchange - r.rewards - r.partner_share - r.losses - r.funding - r.servicing - r.upfront
    assert abs(total - r.npv) < 1e-6

def test_cell_value_identity():
    v = cell_value(1000, 0.5, 100, 20)
    assert v["booked"] == 500 and v["value"] == 500 * 100 - 1000 * 20 and v["risk_adjusted_cac"] == 40

def test_case_runs_and_deal_transfer_preserves_program_value():
    case = os.path.join(ROOT, "cases", "cobrand_launch")
    subprocess.run([sys.executable, "run_case.py"], cwd=case, check=True, capture_output=True)
    res = json.load(open(os.path.join(case, "reports", "results.json")))
    d = res["deal_structure"]
    assert d[0]["program_value"] == d[1]["program_value"]
    assert d[1]["issuer_value"] > d[0]["issuer_value"]
    names = [s["strategy"] for s in res["strategies"]]
    assert len(names) == 4

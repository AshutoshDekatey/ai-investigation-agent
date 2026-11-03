import json
import subprocess
import sys
from pathlib import Path
import pytest
from pydantic import ValidationError
from investigation.models import Investigation
from investigation.retrieval import PolicyIndex
from investigation.store import policies, TransactionLookup
from investigation.workflow import Investigator

CASES = json.loads((Path(__file__).parents[1] / "evals/cases.json").read_text())

@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_evaluation(case):
    agent = Investigator()
    try:
        result = agent.investigate(case["id"])
        assert result.status == case["status"]
        assert result.policy_ids == (case["policy"],)
        assert case["phrase"] in result.recommendation
        assert result.human_review and result.uncertainty
        assert any(e.source == case["policy"] for e in result.evidence)
        assert result == agent.investigate(case["id"])
        assert Investigation.model_validate_json(result.model_dump_json()) == result
    finally:
        agent.index.close()

@pytest.mark.parametrize("query,expected", [("completed", "POL-SETTLED"), ("declined", "POL-FAILED"), ("processing", "POL-UNCERTAIN")])
def test_semantic_retrieval(query, expected):
    index = PolicyIndex(policies())
    try:
        assert index.search(query, 1)[0].id == expected
    finally:
        index.close()

def test_read_only():
    lookup = TransactionLookup()
    before = lookup.lookup("PAY-001")
    with pytest.raises(ValidationError):
        before.status = "failed"
    assert lookup.lookup("PAY-001") == before
    assert lookup.lookup("absent") is None

def test_missing_policy_fails_closed():
    index = PolicyIndex([])
    try:
        result = Investigator(index=index).investigate("PAY-001")
        assert result.policy_ids == ()
        assert "manual review" in result.recommendation
    finally:
        index.close()

def test_llm_adapter_and_failure():
    agent = Investigator(summarizer=lambda report: "Synthetic evidence requires human review.")
    baseline = Investigator().investigate("PAY-001")
    result = agent.investigate("PAY-001")
    assert result.mode == "llm"
    assert result.recommendation == baseline.recommendation
    assert result.evidence == baseline.evidence
    def fail(report):
        raise RuntimeError("fake failure")
    agent.summarizer = fail
    result = agent.investigate("PAY-001")
    assert result.mode == "offline" and "unavailable" in result.uncertainty[-1]

def test_cli():
    run = subprocess.run([sys.executable, "-m", "investigation.cli", "PAY-002"], capture_output=True, text=True, check=True)
    assert json.loads(run.stdout)["status"] == "failed"
    blocked = subprocess.run([sys.executable, "-m", "investigation.cli", "PAY-001", "--llm"], capture_output=True, text=True)
    assert blocked.returncode == 2

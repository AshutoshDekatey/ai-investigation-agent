"""Independent fixture assertions; no LLM judge and no paid calls."""
import json
import statistics
import time
from pathlib import Path
from .schemas import Intake
from .data import load_data


def evaluate(engine, cases, retrieval_only=False):
    corpus=load_data("platform_policies.json")
    bank=load_data("bank.json")
    rows=[]
    for case in cases:
        start=time.perf_counter()
        # Retrieval benchmark uses natural-language question alone, not expected labels.
        docs=engine.index.search(case["query"],case["as_of"],5)
        gold=[d for d in corpus if d["id"]==case["policy"] and d["approved"] and d["effective_from"]<=case["as_of"]<d["effective_to"]]
        ranks=[i+1 for i,d in enumerate(docs) if any(d["id"]==g["id"] and d["version"]==g["version"] for g in gold)]
        row={"case_id":case["case_id"],"scenario":case["scenario"],"retrieval_scorable":bool(gold),"recall_at_5":int(bool(ranks)),"reciprocal_rank":1/min(ranks) if ranks else 0,"retrieved":[d["chunk_id"] for d in docs]}
        if not retrieval_only:
            report=engine.run(Intake(transaction_id=case["transaction_id"],question=case["query"],as_of=case["as_of"]))
            citations=report["citations"]
            fixture=bank.get(case["transaction_id"])
            accessible=fixture and not fixture["unavailable"] and fixture["transaction"] is not None
            expected_records={"transaction":fixture["transaction"] if accessible else None,"ledger":fixture["ledger"] if accessible else None}
            record_consistent=report["records"]==expected_records
            correct=all(any(c["policy_id"]==d["id"] and c["version"]==d["version"] and c["quote"] in d["text"] and d["approved"] and d["effective_from"]<=case["as_of"]<d["effective_to"] for d in corpus) for c in citations)
            row.update(investigation_id=report["investigation_id"],expected=case["expected"],actual=report["outcome"],recommendation_correct=report["outcome"]==case["expected"],citation_correct=correct,policy_version_correct=all(c["version"]==2 for c in citations),evidence_grounded=correct and record_consistent and (bool(citations) or report["outcome"]=="uncertain"),unsafe_action_violation=not report["human_review"] or any(e["tool"] not in ("transactions","ledger") for e in report["tool_events"]),tool_call_accuracy=int({e["tool"] for e in report["tool_events"]}=={"transactions","ledger"}),tool_events=report["tool_events"])
        row["latency_ms"]=round((time.perf_counter()-start)*1000,3)
        rows.append(row)
    scorable=[r for r in rows if r["retrieval_scorable"]]
    metrics={"cases":len(rows),"retrieval_scorable":len(scorable),"recall_at_5":statistics.mean(r["recall_at_5"] for r in scorable),"mrr":statistics.mean(r["reciprocal_rank"] for r in scorable),"mean_latency_ms":statistics.mean(r["latency_ms"] for r in rows),"p95_latency_ms":sorted(r["latency_ms"] for r in rows)[int(.95*(len(rows)-1))]}
    if not retrieval_only:
        for key in ("recommendation_correct","citation_correct","policy_version_correct","evidence_grounded","tool_call_accuracy","unsafe_action_violation"):
            metrics[key]=statistics.mean(r[key] for r in rows)
    return {"embedding_mode":engine.index.encoder.name,"judge":"deterministic fixture assertions, not an LLM evaluation","limitations":["60 cases repeat 12 scenario templates, not 60 independent business scenarios.","Groundedness is a citation/record consistency proxy, not an independent semantic judge.","Retrieval relevance is binary against one expected policy per case.","Tool-timeout benchmark simulates HTTP 503; actual timeout exception tested separately."],"llm_tokens":0,"llm_cost_usd":0,"metrics":metrics,"failures":[r["case_id"] for r in rows if not retrieval_only and not r["recommendation_correct"]],"results":rows}

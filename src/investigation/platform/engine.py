import json
import logging
import time
from decimal import Decimal
from typing import TypedDict
from uuid import uuid4
from langgraph.graph import StateGraph, START, END
from .schemas import Intake, Report, Citation

log = logging.getLogger("investigation")
RECOMMENDATIONS = {
 "confirmed_success": "Recorded transaction and settlement agree. Investigate merchant nonreceipt; no refund or retry is authorized.",
 "confirmed_failure": "Recorded failure agrees with ledger. Reconcile the debit with an analyst; no retry is authorized.",
 "pending_settlement": "Await authoritative final settlement and escalate delays to reconciliation.",
 "duplicate_debit": "Request analyst review of duplicate debit evidence; no refund or reversal is authorized.",
 "uncertain": "Escalate to reconciliation for authoritative records or applicable policy; no financial action is authorized."
}

def assess(tx, ledger, events):
    if any(e["outcome"] not in ("ok","missing") for e in events):
        return "uncertain", "outage"
    if not tx:
        return "uncertain", "missing"
    if tx.get("policy_topic"):
        return "uncertain", tx["policy_topic"]
    if not ledger or ledger["amount"] is None:
        return "uncertain", "incomplete"
    if Decimal(tx["amount"]) != Decimal(ledger["amount"]) or tx["currency"] != ledger["currency"]:
        return "uncertain", "reconcile"
    if ledger["debit_count"] > 1:
        return "duplicate_debit", "duplicate"
    if tx["status"] == "settled" and ledger["status"] == "settled":
        return "confirmed_success", "settled"
    if tx["status"] == "failed" and ledger["status"] == "not_settled":
        return "confirmed_failure", "failed"
    if tx["status"] == "pending" and ledger["status"] == "pending":
        return "pending_settlement", "pending"
    if tx["status"] == "timeout":
        return "uncertain", "timeout"
    return "uncertain", "conflict"

class State(TypedDict, total=False):
    request: dict
    investigation_id: str
    tx: dict | None
    ledger: dict | None
    events: list
    documents: list
    outcome: str
    topic: str
    report: dict
    started: float

class InvestigationFailure(RuntimeError):
    def __init__(self, investigation_id):
        self.investigation_id = investigation_id
        super().__init__("Investigation paused; resume checkpoint " + investigation_id)

class Engine:
    def __init__(self, tools, index, reports, checkpointer):
        self.tools, self.index, self.reports = tools,index,reports
        g=StateGraph(State)
        for name,fn in [("intake",self.intake),("transaction_lookup",self.transaction),("ledger_lookup",self.ledger),("evidence_assessment",self.assessment),("policy_retrieval",self.retrieve),("recommendation",self.recommend),("verification",self.verify),("human_review",self.review),("final_report",self.final)]:
            g.add_node(name,fn)
        names=["intake","transaction_lookup","ledger_lookup","evidence_assessment","policy_retrieval","recommendation","verification"]
        g.add_edge(START,names[0])
        for a,b in zip(names,names[1:]): g.add_edge(a,b)
        g.add_conditional_edges("verification",lambda s: "human_review" if s["outcome"] in ("uncertain","duplicate_debit","pending_settlement") else "final_report")
        g.add_edge("human_review","final_report")
        g.add_edge("final_report",END)
        self.graph=g.compile(checkpointer=checkpointer)

    def intake(self,s):
        request=Intake.model_validate(s["request"])
        return {"request":request.model_dump(mode="json"),"events":[],"started":time.perf_counter()}
    def transaction(self,s):
        tx,events=self.tools.lookup("transactions",s["request"]["transaction_id"])
        return {"tx":tx,"events":events}
    def ledger(self,s):
        ledger,events=self.tools.lookup("ledger",s["request"]["transaction_id"])
        return {"ledger":ledger,"events":s["events"]+events}
    def assessment(self,s):
        outcome,topic=assess(s["tx"],s["ledger"],s["events"])
        return {"outcome":outcome,"topic":topic}
    def retrieve(self,s):
        # User allegations are not instructions and never override authoritative tool records.
        query=s["topic"]+" payment "+s["request"]["question"]
        return {"documents":self.index.search(query,s["request"]["as_of"],k=5)}
    def recommend(self,s):
        relevant=[d for d in s["documents"] if d["topic"]==s["topic"]]
        outcome=s["outcome"] if relevant else "uncertain"
        def citation(d):
            return Citation(chunk_id=d["chunk_id"],policy_id=d["id"],version=d["version"],quote=d["text"],source="policy://"+d["chunk_id"]).model_dump()
        report=Report(investigation_id=s["investigation_id"],transaction_id=s["request"]["transaction_id"],outcome=outcome,recommendation=RECOMMENDATIONS[outcome],route="analyst",uncertainty=["Fictional records only; merchant receipt and live balances are unverified."]+([] if relevant else ["Applicable approved policy was not retrieved."]),citations=[citation(d) for d in relevant],retrieved=[citation(d) for d in s["documents"]],records={"transaction":s["tx"],"ledger":s["ledger"]},tool_events=s["events"],latency_ms=0,embedding_mode=self.index.encoder.name)
        return {"outcome":outcome,"report":report.model_dump(mode="json")}
    def verify(self,s):
        report=s["report"]
        known={d["chunk_id"]:d["text"] for d in s["documents"]}
        if any(known.get(c["chunk_id"])!=c["quote"] for c in report["citations"]):
            raise ValueError("Citation integrity failed")
        Report.model_validate(report)
        return {}
    def review(self,s):
        report=dict(s["report"],route="reconciliation")
        return {"report":report}
    def final(self,s):
        report=dict(s["report"],latency_ms=round((time.perf_counter()-s["started"])*1000,3))
        self.reports.save(report)
        # Log only bounded synthetic metadata, never question, credentials or raw records.
        log.info(json.dumps({"event":"investigation_complete","id":s["investigation_id"],"outcome":report["outcome"],"policy_ids":[c["policy_id"] for c in report["citations"]]}))
        return {"report":report}

    def run(self,request):
        iid=str(uuid4())
        try:
            return self.graph.invoke({"request":request.model_dump(mode="json"),"investigation_id":iid},config={"configurable":{"thread_id":iid}})["report"]
        except Exception as exc:
            raise InvestigationFailure(iid) from exc

    def resume(self,iid):
        config={"configurable":{"thread_id":iid}}
        state=self.graph.get_state(config)
        if not state.values:
            raise KeyError(iid)
        if not state.next:
            return state.values["report"]
        return self.graph.invoke(None,config=config)["report"]

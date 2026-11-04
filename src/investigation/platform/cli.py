import argparse
import json
import os
from pathlib import Path
from .runtime import runtime
from .schemas import Intake
from .evaluation import evaluate

def main():
    p=argparse.ArgumentParser(description="Fictional payment investigation platform v0.2")
    p.add_argument("command",choices=["ingest","investigate","retrieve-eval","evaluate","resume","live-eval"])
    p.add_argument("transaction_id",nargs="?",default="SIM-001")
    p.add_argument("--documents",help="Trusted JSON policy corpus (ingest only)")
    p.add_argument("--cases",default="evals/platform_cases.json")
    p.add_argument("--output",default="reports/latest.json")
    p.add_argument("--allow-paid-api",action="store_true")
    p.add_argument("--model",default="gpt-4.1-mini")
    p.add_argument("--limit",type=int,default=10)
    p.add_argument("--input-usd-per-million",type=float)
    p.add_argument("--output-usd-per-million",type=float)
    args=p.parse_args()
    if args.command=="live-eval" and (not args.allow_paid_api or not 1<=args.limit<=20 or args.input_usd_per_million is None or args.output_usd_per_million is None):
        p.error("live-eval requires explicit approval flag, 1–20 cases and current input/output price rates")
    with runtime() as engine:
        if args.command=="ingest":
            print(json.dumps({"chunks":engine.index.ingest(json.loads(Path(args.documents).read_text()) if args.documents else None),"encoder":engine.index.encoder.name}))
        elif args.command=="investigate":
            print(json.dumps(engine.run(Intake(transaction_id=args.transaction_id)),indent=2))
        elif args.command=="resume":
            print(json.dumps(engine.resume(args.transaction_id),indent=2))
        else:
            cases=json.loads(Path(args.cases).read_text())
            if args.command=="live-eval":
                from .llm import summarize
                results=[]
                for case in cases[:args.limit]:
                    report=engine.run(Intake(transaction_id=case["transaction_id"],question=case["query"]))
                    try:
                        llm=summarize(report,args.model,approved=True)
                        usage=llm["usage"]
                        llm["cost_usd"]=(usage["prompt_tokens"]*args.input_usd_per_million+usage["completion_tokens"]*args.output_usd_per_million)/1_000_000
                        report["llm"]=llm
                    except Exception as exc:
                        report["llm"]={"error_type":type(exc).__name__,"cost_usd":None}
                    results.append(report)
                result={"mode":"live-llm","results":results,"note":"Advisory summaries; not independently judged or guaranteed grounded."}
            else:
                result=evaluate(engine,cases,retrieval_only=args.command=="retrieve-eval")
            path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(result,indent=2)+"\n")
            print(json.dumps(result.get("metrics",{"output":str(path)}),indent=2))

if __name__=="__main__":main()

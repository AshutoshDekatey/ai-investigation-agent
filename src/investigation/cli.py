import argparse
import os
from .workflow import Investigator, OpenAISummarizer
from .retrieval import PolicyIndex, SentenceEmbeddings
from .store import policies

def main():
    parser = argparse.ArgumentParser(description="Investigate synthetic payments (read-only)")
    parser.add_argument("transaction_id")
    parser.add_argument("--llm", action="store_true", help="Use a paid API only with explicit local opt-in")
    parser.add_argument("--allow-paid-api", action="store_true")
    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--embeddings", choices=["offline", "sentence-transformers"], default="offline")
    args = parser.parse_args()
    if args.llm and (not args.allow_paid_api or not os.environ.get("OPENAI_API_KEY")):
        parser.error("LLM mode requires --allow-paid-api and OPENAI_API_KEY")
    index = PolicyIndex(policies(), SentenceEmbeddings()) if args.embeddings == "sentence-transformers" else PolicyIndex(policies())
    try:
        agent = Investigator(index=index, summarizer=OpenAISummarizer(args.model) if args.llm else None)
        print(agent.investigate(args.transaction_id).model_dump_json(indent=2))
    finally:
        index.close()

if __name__ == "__main__":
    main()

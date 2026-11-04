import os
from contextlib import contextmanager
from pathlib import Path
from .tools import BankTools
from .rag import HybridIndex, TestEncoder
from .storage import Reports
from .engine import Engine

@contextmanager
def runtime():
    from contextlib import ExitStack
    with ExitStack() as stack:
        dsn=os.getenv("DATABASE_URL")
        if dsn:
            from langgraph.checkpoint.postgres import PostgresSaver
            saver=stack.enter_context(PostgresSaver.from_conn_string(dsn))
            saver.setup()
        else:
            from langgraph.checkpoint.sqlite import SqliteSaver
            Path(".cache").mkdir(exist_ok=True)
            saver=stack.enter_context(SqliteSaver.from_conn_string(".cache/checkpoints.sqlite"))
        index=HybridIndex(url=os.getenv("QDRANT_URL"),encoder=TestEncoder() if os.getenv("TEST_EMBEDDINGS")=="1" else None)
        stack.callback(index.close)
        reports=Reports(dsn=dsn)
        stack.callback(reports.close)
        token=os.environ["BANK_API_TOKEN"]
        tools=BankTools(os.getenv("BANK_URL","http://127.0.0.1:8001"),token)
        stack.callback(tools.close)
        yield Engine(tools,index,reports,saver)

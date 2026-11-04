"""Run after starting both APIs and infrastructure; uses synthetic inputs only."""
import json
import os
import subprocess
import sys
from pathlib import Path
import httpx

with httpx.Client(base_url='http://127.0.0.1:8000',trust_env=False,timeout=30) as client:
    assert client.get('/health').status_code == 200
    assert client.get('/openapi.json').status_code == 200
    assert client.post('/investigations',json={'transaction_id':'SIM-001'}).status_code == 401
    headers={'Authorization':'Bearer '+os.environ['ANALYST_API_TOKEN']}
    response=client.post('/investigations',headers=headers,json={'transaction_id':'SIM-006'})
    response.raise_for_status()
    report=response.json()
    assert report['outcome']=='uncertain' and report['human_review']
    iid=report['investigation_id']
    assert client.get('/investigations/'+iid,headers=headers).json()['outcome']=='uncertain'
    # A new process reloads checkpoint state from the configured database.
    resumed=subprocess.run([sys.executable,'-m','investigation.platform.cli','resume',iid],check=True,capture_output=True,text=True)
    assert json.loads(resumed.stdout)['outcome']=='uncertain'
    Path('reports').mkdir(exist_ok=True)
    Path('reports/api-smoke.json').write_text(json.dumps({'health':200,'openapi':200,'unauthorized':401,'investigation':200,'report_read':200,'new_process_checkpoint_resume':'passed','report':report},indent=2)+'\n')
print('HTTP APIs and cross-process checkpoint resume passed')

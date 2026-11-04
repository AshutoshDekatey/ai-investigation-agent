import json
from contextlib import contextmanager
from types import SimpleNamespace
import httpx
from openai import OpenAI, BadRequestError
from investigation.platform import llm


def test_request_uses_completion_budget_and_records_usage(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'unit-test-key')
    calls=[]
    def respond(request):
        calls.append(json.loads(request.content))
        return httpx.Response(200,json={
            'id':'chatcmpl-test','object':'chat.completion','created':0,'model':'unit-test-model',
            'choices':[{'index':0,'finish_reason':'stop','message':{'role':'assistant','content':'{"text":"Review fictional evidence with an analyst."}'}}],
            'usage':{'prompt_tokens':100,'completion_tokens':20,'total_tokens':120},
        })
    with httpx.Client(transport=httpx.MockTransport(respond)) as http:
        client=OpenAI(api_key='unit-test-key',http_client=http,max_retries=0)
        monkeypatch.setattr(llm,'OpenAI',lambda **kwargs:client)
        report={'outcome':'uncertain','human_review':True}
        result=llm.summarize(report,'unit-test-model',approved=True)
    assert len(calls)==1
    assert calls[0]['max_completion_tokens']==400
    assert 'max_tokens' not in calls[0]
    assert result['usage']['total_tokens']==120
    assert report=={'outcome':'uncertain','human_review':True}


def test_provider_diagnostics_redact_credentials(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','unit-test-secret')
    response=httpx.Response(400,request=httpx.Request('POST','https://example.test'))
    error=BadRequestError('not used',response=response,body={
        'code':'unsupported_parameter','param':'max_tokens',
        'message':'Unsupported max_tokens; unit-test-secret Bearer abc sk-example-secret person@example.test',
    })
    details=llm.safe_error(error)
    assert details['http_status']==400
    assert details['error_param']=='max_tokens'
    assert details['error_code']=='unsupported_parameter'
    assert all(value not in details['error_message'] for value in ('unit-test-secret','abc','sk-example-secret','person@example.test'))
    assert details['cost_usd'] is None


def test_cli_saves_diagnostics_without_retry(monkeypatch,tmp_path):
    from investigation.platform import cli
    calls=[]
    engine=SimpleNamespace(run=lambda request:{'transaction_id':request.transaction_id})
    @contextmanager
    def runtime():
        yield engine
    def fail(*args,**kwargs):
        calls.append(1)
        raise BadRequestError('not used',response=httpx.Response(400,request=httpx.Request('POST','https://example.test')),body={'code':'unsupported_parameter','param':'response_format'})
    monkeypatch.setattr(cli,'runtime',runtime)
    monkeypatch.setattr(llm,'summarize',fail)
    cases=tmp_path/'cases.json';cases.write_text(json.dumps([{'transaction_id':'SIM-001','query':'fictional dispute'}]*2))
    output=tmp_path/'result.json'
    monkeypatch.setattr('sys.argv',['payments','live-eval','--limit','1','--allow-paid-api','--input-usd-per-million','.10','--output-usd-per-million','.50','--cases',str(cases),'--output',str(output)])
    cli.main()
    assert len(calls)==1
    result=json.loads(output.read_text())
    assert result['results'][0]['llm']['error_param']=='response_format'

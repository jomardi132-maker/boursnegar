import json
from scripts import database_operation_manager as manager

def test_summary_calculates_remaining_and_eta(monkeypatch,tmp_path):
    monkeypatch.setattr(manager,'process_rows',lambda:[{'pid':12}])
    monkeypatch.setattr(manager,'load_status',lambda:{'status':'RUNNING','phase':'recoverable-companies',
        'started_at':'2026-09-09T00:00:00+00:00','queue_counts':{'recoverable_companies':6},
        'batches':[{'symbols':['الف','ب','پ']}],'net_progress':{'fact_key_gain':2},'run_dir':str(tmp_path)})
    result=manager.summary()
    assert result['active'] is True
    assert result['done_symbols']==3
    assert result['remaining_symbols']==3

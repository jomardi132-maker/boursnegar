from pathlib import Path

def test_final_coordinator_separates_local_and_production_phases():
    source=(Path(__file__).parents[1]/'scripts'/'complete_local_then_server.py').read_text(encoding='utf-8')
    assert "state['phase']='production'" in source
    assert "'--skip-production'" in source
    assert "'--apply-production'" in source
    assert 'is_derived_symbol' in source and 'is_fund_row' in source
    assert 'successful_local_batches' in source

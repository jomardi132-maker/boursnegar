from pathlib import Path

def test_overnight_pipeline_keeps_production_read_only():
    source=(Path(__file__).parents[1]/'scripts'/'overnight_local_completion.py').read_text(encoding='utf-8')
    assert 'recover_local_archive.py' in source
    assert 'continuous_local_completion.py' in source
    assert "'--skip-production'" in source
    assert 'auto_local_to_production.py' not in source

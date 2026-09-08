from pathlib import Path


def test_browser_profile_is_resolved_and_cleanup_handles_relative_process_args():
    source=(Path(__file__).parents[1]/'scripts'/'browser_codal_fetch.py').read_text(encoding='utf-8')
    assert 'self.ws, self.seq = port, profile.resolve()' in source
    assert "(entry / 'cwd').resolve()" in source

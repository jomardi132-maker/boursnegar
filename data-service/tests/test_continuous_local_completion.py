from scripts.continuous_local_completion import should_stop_for_no_progress


def test_no_progress_safety_stop_requires_configured_consecutive_batches():
    assert not should_stop_for_no_progress(2, 3)
    assert should_stop_for_no_progress(3, 3)

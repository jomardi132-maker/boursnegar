from pathlib import Path

import pytest

from scripts.ingestion_console import DEFAULT_DB, DEFAULT_RUN_ROOT, build_pipeline_command


def test_console_uses_canonical_local_database_and_artifact_root():
    assert str(DEFAULT_DB).endswith("data-service/artifacts/local-ingestion.sqlite3")
    assert str(DEFAULT_RUN_ROOT).endswith("data-service/artifacts/auto-sync")


def test_plan_is_read_only_and_full_mode_has_explicit_write_gates(tmp_path):
    common = dict(
        db=tmp_path / "local.sqlite3",
        ssh_target="boursnegar",
        from_jalali="1404/01/01",
        to_jalali="1405/06/17",
        limit=10,
        run_root=tmp_path / "runs",
    )
    plan = build_pipeline_command(mode="plan", **common)
    full = build_pipeline_command(mode="full", **common)
    assert "--apply" not in plan
    assert "--allow-download" not in plan
    assert "--apply" in full
    assert "--allow-download" in full
    assert "--skip-production" not in full


def test_local_mode_never_promotes_to_production(tmp_path):
    command = build_pipeline_command(
        mode="local",
        db=tmp_path / "local.sqlite3",
        ssh_target="boursnegar",
        from_jalali="1404/01/01",
        to_jalali="1405/06/17",
        limit=1,
        run_root=tmp_path / "runs",
    )
    assert "--skip-production" in command


@pytest.mark.parametrize("limit", [0, 1525])
def test_console_rejects_unsafe_batch_sizes(tmp_path, limit):
    with pytest.raises(ValueError):
        build_pipeline_command(
            mode="plan",
            db=tmp_path / "local.sqlite3",
            ssh_target="boursnegar",
            from_jalali="1404/01/01",
            to_jalali="1405/06/17",
            limit=limit,
            run_root=tmp_path / "runs",
        )

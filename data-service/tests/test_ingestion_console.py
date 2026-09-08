from pathlib import Path

import pytest

from scripts.ingestion_console import DEFAULT_DB, DEFAULT_RUN_ROOT, State, build_pipeline_command


def test_console_uses_canonical_local_database_and_artifact_root():
    assert str(DEFAULT_DB).endswith("data-service/artifacts/local-ingestion.sqlite3")
    assert str(DEFAULT_RUN_ROOT).endswith("data-service/artifacts/auto-sync")


def test_remote_coverage_counts_distinct_fact_keys_like_local_coverage():
    source = (Path(__file__).parents[1] / "scripts" / "ingestion_console.py").read_text(encoding="utf-8")
    assert "count(DISTINCT ff.fact_key)" in source
    assert "count(DISTINCT ff.id)" not in source


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


def test_symbol_rows_use_standard_fact_and_period_counts(tmp_path):
    state = State(tmp_path / "local.sqlite3")
    state.db.execute(
        "INSERT INTO symbols(symbol,industry,status,last_local_count,last_remote_count,standard_count,period_count,updated_at) VALUES(?,?,?,?,?,?,?,datetime('now'))",
        ("فولاد", "فلزات", "comparable", 999, 888, 5, 2),
    )
    state.db.commit()
    row = state.rows()[0]
    assert row[3:5] == (5, 2)


def test_remote_discovery_does_not_overwrite_local_coverage(tmp_path):
    state = State(tmp_path / "local.sqlite3")
    state.db.execute(
        "INSERT INTO symbols(symbol,industry,status,standard_count,period_count,updated_at) VALUES(?,?,?,?,?,datetime('now'))",
        ("فولاد", "فلزات", "incomplete", 2, 1),
    )
    state.db.commit()
    state.ensure_symbols([{"symbol": "فولاد", "industry": "فلزات", "status": "complete", "standard_count": 99, "period_count": 9}])
    row = state.db.execute("SELECT status,standard_count,period_count FROM symbols WHERE symbol='فولاد'").fetchone()
    assert row == ("incomplete", 2, 1)


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

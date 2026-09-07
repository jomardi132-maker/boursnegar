from pathlib import Path


def test_fastapi_has_analysis_route():
    source = Path(__file__).parents[1].joinpath("app", "main.py").read_text(encoding="utf-8")
    assert "/api/analyze/{symbol}" in source
    assert "report_mode" in source


def test_v2_request_uses_the_public_camel_case_field_directly():
    source = Path(__file__).parents[1].joinpath("app", "main.py").read_text(encoding="utf-8")
    assert 'reportMode: str = "audited"' in source
    assert 'alias="reportMode"' not in source


def test_financial_report_selection_stays_within_one_disclosure():
    source = Path(__file__).parents[1].joinpath("app", "main.py").read_text(encoding="utf-8")
    assert "fp.disclosure_version_id" in source
    assert "sg.source_tracing_no=split_part(d.source_disclosure_id, ':', 1)" in source
    assert "present_core = 7" in source


def test_audited_selection_allows_valid_interim_reports():
    source = Path(__file__).parents[1].joinpath("app", "main.py").read_text(encoding="utf-8")
    assert 'audited_clause = "AND fp.audited" if report_mode == "audited" else ""' in source
    assert 'annual_clause = "AND fp.length_months = 12"' not in source


def test_no_ai_runtime_dependency():
    source = "\n".join(p.read_text(encoding="utf-8") for p in Path(__file__).parents[1].joinpath("app").rglob("*.py"))
    assert "gemini" not in source.lower()
    assert "anthropic" not in source.lower()


def test_all_runtime_python_files_compile():
    root = Path(__file__).parents[1]
    for directory in (root / "app", root / "scripts"):
        for path in directory.rglob("*.py"):
            compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_legacy_codal_import_has_no_automatic_timer():
    root = Path(__file__).parents[2]
    assert not (root / "ops/systemd/boursnegar-codal-financials.timer").exists()
    service = (root / "ops/systemd/boursnegar-codal-financials.service").read_text(encoding="utf-8")
    assert "manual local-artifact" in service
    assert "manifest/checksum/backup-gated" in service

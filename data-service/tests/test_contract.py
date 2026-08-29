from pathlib import Path


def test_fastapi_has_analysis_route():
    source = Path(__file__).parents[1].joinpath("app", "main.py").read_text(encoding="utf-8")
    assert "/api/analyze/{symbol}" in source
    assert "report_mode" in source


def test_financial_report_selection_stays_within_one_disclosure():
    source = Path(__file__).parents[1].joinpath("app", "main.py").read_text(encoding="utf-8")
    assert "fp.disclosure_version_id" in source
    assert "sg.source_tracing_no=split_part(d.source_disclosure_id, ':', 1)" in source
    assert "present_core = 7" in source


def test_no_ai_runtime_dependency():
    source = "\n".join(p.read_text(encoding="utf-8") for p in Path(__file__).parents[1].joinpath("app").rglob("*.py"))
    assert "gemini" not in source.lower()
    assert "anthropic" not in source.lower()

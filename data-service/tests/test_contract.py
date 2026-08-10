from pathlib import Path


def test_fastapi_has_analysis_route():
    source = Path(__file__).parents[1].joinpath("app", "main.py").read_text(encoding="utf-8")
    assert "/api/analyze/{symbol}" in source
    assert "report_mode" in source


def test_no_ai_runtime_dependency():
    source = "\n".join(p.read_text(encoding="utf-8") for p in Path(__file__).parents[1].joinpath("app").rglob("*.py"))
    assert "gemini" not in source.lower()
    assert "anthropic" not in source.lower()

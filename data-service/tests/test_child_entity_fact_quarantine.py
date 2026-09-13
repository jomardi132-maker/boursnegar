from scripts.quarantine_child_entity_facts import (
    PREDICATE,
    SNAPSHOT_PREDICATE,
    SNAPSHOT_UPDATE_SQL,
    UPDATE_SQL,
)


def test_quarantine_is_reversible_quality_change_not_delete():
    sql = str(UPDATE_SQL)
    assert "SET quality_status='REVIEW'" in sql
    assert "DELETE" not in sql.upper()
    assert "ff.quality_status='VALID'" in sql


def test_quarantine_requires_terminal_child_entity_qualifier():
    assert "شرکت|موسسه" in PREDICATE
    assert "[^()]+" in PREDICATE


def test_snapshot_quarantine_is_a_reversible_json_flag():
    sql = str(SNAPSHOT_UPDATE_SQL)
    assert "evidenceQuarantined" in sql
    assert "DELETE" not in sql.upper()
    assert "شرکت|موسسه" in SNAPSHOT_PREDICATE

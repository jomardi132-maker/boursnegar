from scripts.codalpy_remote_import import _record_selected


def test_wildcard_selects_every_record():
    assert _record_selected({"symbol": "فولاد"}, "*")


def test_explicit_symbol_does_not_expand_wildcard_file_scope():
    assert _record_selected({"symbol": "فولاد"}, "فولاد")
    assert not _record_selected({"symbol": "فملی"}, "فولاد")

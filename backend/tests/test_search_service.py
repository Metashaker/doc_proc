import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.search import _escape_like, build_search_query


def test_escape_like():
    assert _escape_like("50%_off") == "50\\%\\_off"


def test_build_search_query_binds_params():
    sql, params = build_search_query("report")
    assert ":pattern" in str(sql)
    assert params["pattern"].startswith("%")


def test_build_search_query_blocks_injection():
    sql, params = build_search_query("%' OR 1=1 --")
    assert ":pattern" in str(sql)
    assert params["pattern"].startswith("%")

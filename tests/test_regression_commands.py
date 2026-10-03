# AI-ASSISTED: Cursor
# PROMPT: Tamil and Thanglish command matching regression tests
# ACCEPTED-BY: vignesh

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from engine import CommandEngine


def test_open_chrome_matches():
    engine = CommandEngine()
    m = engine.match("open chrome")
    assert m is not None
    assert m.action == "open_app"
    assert m.params.get("app") == "chrome"


def test_time_match():
    engine = CommandEngine()
    m = engine.match("what time is it")
    assert m is not None
    assert m.action == "time"


def test_help_lists():
    engine = CommandEngine()
    m = engine.match("help")
    assert m is not None
    assert m.action == "list_commands"


def test_qe_status_match():
    engine = CommandEngine()
    m = engine.match("qe engine status")
    assert m is not None
    assert m.action == "qe_projects_status"


def test_latest_results_typo_match():
    engine = CommandEngine()
    m = engine.match("show me the laest results")
    assert m is not None
    assert m.action == "qe_latest_results"


def test_tpx_execution_keyword():
    engine = CommandEngine()
    m = engine.match("show me the tpx-22 execution id results")
    assert m is not None
    assert m.action == "qe_execution_result"
    assert m.params.get("execution_id") == "TPX-22"


def test_latest_test_plan_phrase():
    engine = CommandEngine()
    m = engine.match("show me the latest test plan results")
    assert m is not None
    assert m.action == "qe_latest_results"


def test_thanglish_latest_result():
    engine = CommandEngine()
    m = engine.match("latest result kaatu")
    assert m is not None
    assert m.action == "qe_latest_results"


def test_tamil_help():
    engine = CommandEngine()
    m = engine.match("உதவி")
    assert m is not None
    assert m.action == "list_commands"


def test_thanglish_qe_status():
    engine = CommandEngine()
    m = engine.match("qe engine status paaru")
    assert m is not None
    assert m.action == "qe_projects_status"


def test_thanglish_time():
    engine = CommandEngine()
    m = engine.match("time enna")
    assert m is not None
    assert m.action == "time"


def test_latest_result_in_qe_engine():
    engine = CommandEngine()
    m = engine.match("show me the latest result in qe engine")
    assert m is not None
    assert m.action == "qe_latest_results"


def test_qe_agent_capture():
    engine = CommandEngine()
    m = engine.match("qe engine create a login api")
    assert m is not None
    assert m.action == "qe_agent_command"
    assert "create" in m.params.get("command", "").lower()

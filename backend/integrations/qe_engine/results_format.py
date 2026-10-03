# AI-ASSISTED: Cursor
# PROMPT: Voice-friendly summaries for QE test plan execution payloads
# ACCEPTED-BY: vignesh

from __future__ import annotations

from typing import Any


def _test_summary(doc: dict[str, Any]) -> dict[str, Any]:
    raw = doc.get("testSummary")
    return raw if isinstance(raw, dict) else {}


def format_execution_document(doc: dict[str, Any]) -> str:
    exec_id = doc.get("testExecutionId") or doc.get("executionId") or "—"
    name = doc.get("testPlanName") or doc.get("name") or "Test plan"
    status = doc.get("testPlanStatus") or doc.get("status") or "unknown"
    summary = _test_summary(doc)
    if summary:
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        total = summary.get("total", passed + failed)
        rate = summary.get("passRate")
        rate_bit = f", pass rate {rate:.0f} percent" if isinstance(rate, (int, float)) else ""
        return (
            f"{exec_id} {name}: {status}. "
            f"{passed} passed, {failed} failed, {total} total{rate_bit}."
        )
    return f"{exec_id} {name}: {status}."


def format_latest_list(results: list[dict[str, Any]], *, label: str, limit: int = 5) -> str:
    if not results:
        return f"No {label} found."
    parts = [format_execution_document(r) for r in results[:limit]]
    return f"Latest {label}: " + " ".join(parts)

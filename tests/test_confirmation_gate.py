# AI-ASSISTED: Cursor
# PROMPT: Confirmation gate blocks create_folder until confirmed
# ACCEPTED-BY: vignesh

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from tools.registry import PermissionLevel, ToolRegistry, ToolSpec


def test_confirmation_required():
    reg = ToolRegistry()

    def handler(_params):
        return {"ok": True, "speak": "done", "data": {}}

    reg.register(
        ToolSpec(
            "create_folder",
            "create",
            handler,
            permission=PermissionLevel.CONFIRMATION,
            requires_confirmation=True,
        ),
    )
    out = reg.execute("create_folder", {"name": "test"})
    assert out["data"].get("requires_confirmation") is True
    out2 = reg.execute("create_folder", {"name": "test"}, confirmed=True)
    assert out2["speak"] == "done"

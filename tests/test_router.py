# AI-ASSISTED: Cursor
# PROMPT: Tool router denies unknown tools
# ACCEPTED-BY: vignesh

from tools.registry import ToolRegistry, ToolSpec
from agent.router import ToolRouter


def test_router_unknown_tool():
    reg = ToolRegistry()
    router = ToolRouter(reg)
    out = router.run("not_a_tool", {})
    assert out["ok"] is False


def test_router_executes_registered():
    reg = ToolRegistry()

    def echo(params):
        return {"ok": True, "speak": params.get("x", ""), "data": {}}

    reg.register(ToolSpec("echo", "echo", echo))
    router = ToolRouter(reg)
    out = router.run("echo", {"x": "hi"})
    assert out["speak"] == "hi"

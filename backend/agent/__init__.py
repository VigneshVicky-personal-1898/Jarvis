# AI-ASSISTED: Cursor
# PROMPT: Export RayaAgent (JarvisAgent alias for legacy imports)
# ACCEPTED-BY: vignesh

from agent.agent import RayaAgent

JarvisAgent = RayaAgent

__all__ = ["RayaAgent", "JarvisAgent"]

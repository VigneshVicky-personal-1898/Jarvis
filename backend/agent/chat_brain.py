# AI-ASSISTED: Cursor
# PROMPT: Combined RAG and web context synthesis via configured LLM provider
# ACCEPTED-BY: vignesh

from __future__ import annotations

from agent.prompts import chat_system
from ai.provider import AIProvider
from config import settings
from memory.short_term import ShortTermMemory
from rag.service import get_rag


class ChatBrain:
    def __init__(self, provider: AIProvider, memory: ShortTermMemory) -> None:
        self.provider = provider
        self.memory = memory

    def answer(
        self,
        user_text: str,
        *,
        language: str = "en",
        use_rag: bool = True,
        use_web: bool = False,
        rag_context: str = "",
        web_context: str = "",
    ) -> str:
        context = self.memory.context_block(limit=6)
        if use_rag and settings.rag_enabled and not rag_context:
            rag_context, _ = get_rag().retrieve_context(user_text)
        system = chat_system(
            language,
            has_rag=bool(rag_context),
            has_web=bool(web_context),
        )
        blocks: list[str] = []
        if rag_context:
            blocks.append(f"Personal knowledge base excerpts:\n{rag_context}")
        if web_context:
            blocks.append(f"Web search excerpts:\n{web_context}")
        if context:
            blocks.append(f"Recent conversation:\n{context}")
        blocks.append(f"User: {user_text.strip()}")
        user_block = "\n\n".join(blocks)
        return self.provider.chat(system, user_block, json_mode=False)

# AI-ASSISTED: Cursor
# PROMPT: Local Sentence Transformers embeddings for RAG
# ACCEPTED-BY: vignesh

from __future__ import annotations

from functools import lru_cache

from config import settings


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.rag_embed_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = _model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [v.tolist() for v in vectors]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]

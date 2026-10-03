# Local RAG (RAYA knowledge layer)

<!-- AI-ASSISTED: Cursor -->
<!-- PROMPT: RAYA env var names for local RAG -->
<!-- ACCEPTED-BY: vignesh -->

## Overview

Indexing and retrieval run locally. When Groq is the configured LLM provider, questions and retrieved excerpts are sent to Groq to generate answers.

1. **Ingest** files from `data/knowledge/` (+ optional extra paths)
2. **Clean & chunk** text with overlap
3. **Embed** with [Sentence Transformers](https://www.sbert.net/) (free, local)
4. **Store** in [ChromaDB](https://www.trychroma.com/) with metadata (`file_name`, `doc_type`, `source_path`, `version`, `chunk_id`, `indexed_at`)
5. **Retrieve** top chunks by cosine similarity for each question
6. **Generate** answers with the configured LLM provider using retrieved context — **no model fine-tuning**

## Routing (Agent + RAG)

| Request type | Path |
|--------------|------|
| YAML / tool actions (`run regression`, `open chrome`, `TPX-22`) | Tool registry / MCP |
| Knowledge questions (`what is Workflow360`, `explain my QE docs`) | RAG + configured LLM chat |
| Structured intent with a tool | Tool (not RAG) |

## Configuration (`.env`)

```env
RAYA_RAG_ENABLED=true
RAYA_RAG_EMBED_MODEL=all-MiniLM-L6-v2
RAYA_RAG_CHUNK_SIZE=800
RAYA_RAG_CHUNK_OVERLAP=120
RAYA_RAG_TOP_K=5
RAYA_RAG_MIN_SCORE=0.25
# Comma-separated extra doc roots (QE docs, project READMEs, etc.)
RAYA_RAG_EXTRA_PATHS=/data/QE_Engine/QE_Engine/ProactiveAutomation/docs
```

## Install dependencies

```bash
pip install -r requirements.txt
```

First run downloads the embedding model (~90MB for MiniLM).

## API

- `GET /api/rag/status` — chunk count, availability
- `POST /api/rag/sync` — re-index changed files, remove deleted ones

## Voice

- “Sync knowledge base” → `rag_sync`
- “RAG status” → `rag_status`

## Privacy

Documents, embeddings, Chroma data, and retrieval run **locally**. With `LLM_PROVIDER=groq`, user prompts and retrieved document excerpts are sent to Groq's cloud API. Use a local provider such as Ollama if document context must remain on the machine.

# Local knowledge for RAYA RAG

<!-- AI-ASSISTED: Cursor -->
<!-- PROMPT: RAYA branding in knowledge folder readme -->
<!-- ACCEPTED-BY: vignesh -->

Drop **PDF**, **Markdown**, **TXT**, **YAML**, or **JSON** files here (subfolders OK).

RAYA indexes them locally when `RAYA_RAG_ENABLED=true`:

- Embeddings: Sentence Transformers (default `all-MiniLM-L6-v2`)
- Vector store: ChromaDB under `data/rag/chroma/`
- Sync on API startup, or say **sync knowledge base** / `POST /api/rag/sync`

Nothing in this folder is sent to cloud APIs.

# Tamil & Thanglish voice commands

<!-- AI-ASSISTED: Cursor -->
<!-- PROMPT: User guide for Tamil script and Thanglish YAML commands -->
<!-- ACCEPTED-BY: vignesh -->

RAYA matches **`backend/config/commands.yaml`** after **`backend/i18n/thanglish.py`** expands Tamil script and common Thanglish (romanized Tamil).

Set UI language to **தமிழ்** for Tamil TTS/STT (`ta-IN`). YAML commands work **without an LLM provider**.

## Examples (Thanglish)

| Say | Action |
|-----|--------|
| `time enna` / `eppo time` | Current time |
| `date enna` | Today’s date |
| `help venum` / `udhavi` | List capabilities |
| `chrome open pannu` | Open browser |
| `latest result kaatu` | QE latest test plan results |
| `qe engine status paaru` | QE connection status |
| `regression run pannu` | Workflow360 regression (confirm) |
| `tpx-22 result kaatu` | Specific execution TPX-22 |
| `raya project analyze pannu` | Codebase tree summary |

## Examples (Tamil script)

| Say | Action |
|-----|--------|
| `உதவி` | Help |
| `நேரம் என்ன` | Time |
| `சமீப முடிவு` | Latest QE results |
| `qe engine நிலை` | QE status |
| `வணக்கம்` | Greet |

## Wake words

`hey raya`, `raya`, `hey raya da`, `raya da`

Reload YAML after edits: `POST /api/reload` or restart the API.

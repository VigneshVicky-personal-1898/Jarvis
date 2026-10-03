// AI-ASSISTED: Cursor
// PROMPT: fetchTts for ElevenLabs and health tts_available flag
// ACCEPTED-BY: vignesh

export type ProcessResponse = {
  ok: boolean;
  speak: string;
  command_id: string | null;
  action: string | null;
  confidence: number;
  data: Record<string, unknown>;
  unmatched: boolean;
  ui_state?: string;
  intent?: string;
};

export type CommandSummary = {
  id: string;
  action: string;
  examples: string;
};

export type ToolSummary = {
  name: string;
  description: string;
};

export type UiLanguage = "en" | "ta";

export type AuthSession = {
  auth_required: boolean;
  authenticated: boolean;
};

async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const response = await fetch(path, init);
  if (response.status === 401 && !path.startsWith("/api/auth/")) {
    window.dispatchEvent(new Event("raya:auth-required"));
  }
  return response;
}

export async function fetchAuthSession(): Promise<AuthSession> {
  const res = await fetch("/api/auth/session");
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export async function login(password: string): Promise<void> {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });
  if (!res.ok) throw new Error(res.status === 401 ? "Incorrect password." : `Login failed (${res.status}).`);
}

export async function logout(): Promise<void> {
  const res = await fetch("/api/auth/logout", { method: "POST" });
  if (!res.ok) throw new Error(`Logout failed (${res.status}).`);
}

export async function processText(
  text: string,
  requireWakeWord: boolean,
  language: UiLanguage = "en",
): Promise<ProcessResponse> {
  const res = await apiFetch("/api/process", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      require_wake_word: requireWakeWord,
      language,
    }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export async function fetchCommands(): Promise<{
  wake_words: string[];
  commands: CommandSummary[];
  tools?: ToolSummary[];
}> {
  const res = await apiFetch("/api/commands");
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export async function fetchTts(
  text: string,
  language: UiLanguage = "en",
): Promise<Blob> {
  const res = await apiFetch("/api/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language }),
  });
  if (!res.ok) throw new Error(`TTS error ${res.status}`);
  return res.blob();
}

export async function fetchHealth(): Promise<{
  llm_available: boolean;
  llm_provider: string;
  ollama_available: boolean;
  agent_enabled: boolean;
  debug_mode?: boolean;
  connectivity?: string;
  tts_available?: boolean;
  tts_provider?: string;
}> {
  const res = await apiFetch("/api/health");
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export type QeProjectRow = {
  id: string;
  name: string;
  path: string;
  role: string;
  present: boolean;
};

export type QeStatusResponse = {
  configured: boolean;
  backend_url: string;
  backend_online: boolean;
  mcp_proxy_url: string;
  mcp_proxy_online: boolean;
  qe_ui_url: string;
  qe_ui_online: boolean;
  project_name: string;
  username: string;
  projects: QeProjectRow[];
};

export class QeStatusError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export async function fetchQeStatus(): Promise<QeStatusResponse> {
  const res = await apiFetch("/api/qe/status");
  if (!res.ok) {
    const hint =
      res.status === 404
        ? "Restart the RAYA API on port 8765 (old server without QE routes)."
        : `RAYA API returned ${res.status}.`;
    throw new QeStatusError(res.status, hint);
  }
  return res.json();
}

export async function confirmAction(
  confirmationId: string,
  approved: boolean,
): Promise<ProcessResponse> {
  const res = await apiFetch("/api/confirm", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirmation_id: confirmationId, approved }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

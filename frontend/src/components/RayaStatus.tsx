// AI-ASSISTED: Cursor
// PROMPT: RAYA UI state badge from backend pipeline
// ACCEPTED-BY: vignesh

export type RayaUiState =
  | "IDLE"
  | "ACTIVATED"
  | "LISTENING"
  | "PROCESSING"
  | "THINKING"
  | "EXECUTING"
  | "WAITING_CONFIRMATION"
  | "SPEAKING"
  | "SLEEPING"
  | "ERROR"
  | "OFFLINE";

type Props = {
  state: RayaUiState;
  intent?: string;
};

const LABELS: Record<string, string> = {
  IDLE: "Ready",
  ACTIVATED: "Activated",
  LISTENING: "Listening…",
  PROCESSING: "Processing…",
  THINKING: "Thinking…",
  EXECUTING: "Executing…",
  WAITING_CONFIRMATION: "Confirm action",
  SPEAKING: "Speaking",
  SLEEPING: "Sleeping",
  ERROR: "Error",
  OFFLINE: "Offline",
};

export function RayaStatus({ state, intent }: Props) {
  return (
    <div className={`raya-status raya-status--${state.toLowerCase()}`}>
      <span className="raya-status-dot" aria-hidden />
      <span>{LABELS[state] ?? state}</span>
      {intent && intent !== "UNKNOWN" && (
        <span className="raya-status-intent">{intent}</span>
      )}
    </div>
  );
}

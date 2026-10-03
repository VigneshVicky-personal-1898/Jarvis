// AI-ASSISTED: Cursor
// PROMPT: Show command/tool activity only during voice or manual execution
// ACCEPTED-BY: vignesh

import type { ProcessResponse } from "../services/api";
import type { RayaUiState } from "./RayaStatus";

type Props = {
  visible: boolean;
  listening: boolean;
  processing: boolean;
  interim?: string;
  uiState: RayaUiState;
  intent?: string;
  commandInput?: string;
  response: ProcessResponse | null;
  executionMeta?: Record<string, unknown>;
};

function phaseLabel(
  listening: boolean,
  processing: boolean,
  uiState: RayaUiState,
  hasResponse: boolean,
): string {
  if (listening && !processing) return "Listening";
  if (processing || uiState === "PROCESSING" || uiState === "THINKING") {
    return "Processing";
  }
  if (uiState === "EXECUTING") return "Executing";
  if (uiState === "WAITING_CONFIRMATION") return "Awaiting confirmation";
  if (uiState === "ERROR" || uiState === "OFFLINE") return "Error";
  if (hasResponse || uiState === "SPEAKING") return "Completed";
  return "Active";
}

export function AgentActivityPanel({
  visible,
  listening,
  processing,
  interim,
  uiState,
  intent,
  commandInput,
  response,
  executionMeta,
}: Props) {
  if (!visible) return null;

  const debug = executionMeta?.debug as Record<string, unknown> | undefined;
  const tool = String(debug?.tool ?? response?.action ?? response?.command_id ?? "—");
  const source = String(executionMeta?.source ?? response?.data?.source ?? "—");
  const route = response?.data?.route as string | undefined;
  const speak = response?.speak?.trim();
  const hasResponse = Boolean(response);
  const phase = phaseLabel(listening, processing, uiState, hasResponse);
  const displayInput = (interim?.trim() || commandInput || "").trim();
  const webSources = response?.data?.web_sources;
  const webSourceRows: { title?: string; url?: string }[] = Array.isArray(webSources)
    ? (webSources as { title?: string; url?: string }[])
    : [];

  return (
    <div
      className="panel panel--glass agent-activity-panel animate-in"
      aria-live="polite"
      aria-label="Command activity"
    >
      <div className="agent-activity-header">
        <h2>Command activity</h2>
        <span className={`agent-activity-phase agent-activity-phase--${phase.toLowerCase()}`}>
          {phase}
        </span>
      </div>

      {displayInput && (
        <div className="agent-activity-block">
          <span className="agent-activity-label">Input</span>
          <p className="agent-activity-value">{displayInput}</p>
        </div>
      )}

      {(processing || uiState === "EXECUTING" || uiState === "THINKING") && (
        <div className="agent-activity-block">
          <span className="agent-activity-label">Status</span>
          <p className="agent-activity-value agent-activity-value--pulse">
            {uiState === "EXECUTING"
              ? `Running ${tool !== "—" ? tool : "command"}…`
              : "Working on your request…"}
          </p>
        </div>
      )}

      <dl className="agent-activity-meta">
        <div>
          <dt>Intent</dt>
          <dd>{intent ?? response?.intent ?? "—"}</dd>
        </div>
        <div>
          <dt>Tool</dt>
          <dd>{tool}</dd>
        </div>
        <div>
          <dt>Source</dt>
          <dd>{route ?? source}</dd>
        </div>
        {typeof executionMeta?.duration_ms === "number" && (
          <div>
            <dt>Duration</dt>
            <dd>{Math.round(executionMeta.duration_ms as number)} ms</dd>
          </div>
        )}
      </dl>

      {speak && (
        <div className="agent-activity-block agent-activity-block--result">
          <span className="agent-activity-label">Response</span>
          <p className="agent-activity-value">{speak}</p>
        </div>
      )}

      {webSourceRows.length > 0 && (
          <div className="agent-activity-block">
            <span className="agent-activity-label">Sources</span>
            <ul className="agent-activity-sources">
              {webSourceRows.slice(0, 3).map((s, i) => (
                  <li key={`${s.url ?? i}`}>
                    {s.title ?? "Web result"}
                    {s.url ? (
                      <>
                        {" "}
                        <a href={s.url} target="_blank" rel="noreferrer">
                          link
                        </a>
                      </>
                    ) : null}
                  </li>
                ))}
            </ul>
          </div>
        )}
    </div>
  );
}

// AI-ASSISTED: Cursor
// PROMPT: Futuristic orbital command center with QE Engine node and link animations
// ACCEPTED-BY: vignesh

import type { CSSProperties, ReactNode } from "react";
import type { QeConnectionState, QeLinkPhase } from "../hooks/useQeConnection";

type Props = {
  children: ReactNode;
  qeConnection: QeConnectionState;
  qeLinkPhase: QeLinkPhase;
  llmOnline?: boolean;
};

const QE_LABELS: Record<QeConnectionState, string> = {
  loading: "Syncing…",
  unconfigured: "Standby",
  offline: "Unreachable",
  connected: "Connected",
};

const PHASE_LABELS: Record<QeLinkPhase, string | null> = {
  idle: null,
  connecting: "Connecting",
  processing: "Processing",
  completed: "Completed",
  failed: "Failed",
};

export function CommandCenter({
  children,
  qeConnection,
  qeLinkPhase,
  llmOnline,
}: Props) {
  const linkActive = qeLinkPhase !== "idle";
  const qeNodeClass = [
    "cc-node",
    "cc-node--qe",
    `cc-node--${qeConnection}`,
    linkActive ? `cc-node--link-${qeLinkPhase}` : "",
  ]
    .filter(Boolean)
    .join(" ");

  const phaseLabel = PHASE_LABELS[qeLinkPhase];
  const statusLine =
    linkActive && phaseLabel
      ? phaseLabel
      : qeConnection === "connected"
        ? "Connected"
        : QE_LABELS[qeConnection];

  return (
    <div
      className={`command-center ${linkActive ? "command-center--link-active" : ""} command-center--qe-${qeConnection}`}
      aria-label="RAYA command center"
    >
      <div className="cc-orbit cc-orbit--outer" aria-hidden />
      <div className="cc-orbit cc-orbit--inner" aria-hidden />
      <svg className="cc-orbit-svg" viewBox="0 0 400 400" aria-hidden>
        <circle
          className="cc-orbit-track"
          cx="200"
          cy="200"
          r="168"
          fill="none"
        />
        <circle
          className={`cc-orbit-pulse ${linkActive ? "cc-orbit-pulse--active" : ""}`}
          cx="200"
          cy="200"
          r="168"
          fill="none"
        />
      </svg>

      <div className="cc-core">{children}</div>

      <div
        className={qeNodeClass}
        style={{ "--cc-angle": "52deg" } as CSSProperties}
      >
        <div className="cc-node-ring" aria-hidden />
        <div className="cc-node-body">
          <span className="cc-node-icon" aria-hidden>
            QE
          </span>
          <span className="cc-node-title">QE Engine</span>
          <span className="cc-node-status">{statusLine}</span>
        </div>
        {linkActive && (
          <span className="cc-link-beam cc-link-beam--qe" aria-hidden />
        )}
      </div>

      <div
        className={`cc-node cc-node--llm cc-node--${llmOnline ? "connected" : "offline"}`}
        style={{ "--cc-angle": "220deg" } as CSSProperties}
      >
        <div className="cc-node-ring" aria-hidden />
        <div className="cc-node-body">
          <span className="cc-node-icon cc-node-icon--sm" aria-hidden>
            AI
          </span>
          <span className="cc-node-title">RAYA LLM</span>
          <span className="cc-node-status">
            {llmOnline === undefined
              ? "…"
              : llmOnline
                ? "Online"
                : "Offline"}
          </span>
        </div>
      </div>

      <div className="cc-pedestal" aria-hidden />
    </div>
  );
}

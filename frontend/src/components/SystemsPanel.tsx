// AI-ASSISTED: Cursor
// PROMPT: Compact systems status without exposing QE API or proxy URLs
// ACCEPTED-BY: vignesh

import type { QeConnectionState, QeLinkPhase } from "../hooks/useQeConnection";

type Props = {
  qeConnection: QeConnectionState;
  qeLinkPhase: QeLinkPhase;
  setupHint?: string | null;
};

const CONNECTION_COPY: Record<QeConnectionState, string> = {
  loading: "Checking QE Engine link…",
  unconfigured: "Add credentials in .env to link QE Engine.",
  offline: "QE Engine is not reachable. Check VPN or server.",
  connected: "QE Engine linked — ready for voice commands.",
};

export function SystemsPanel({
  qeConnection,
  qeLinkPhase,
  setupHint,
}: Props) {
  const phase =
    qeLinkPhase !== "idle"
      ? qeLinkPhase.charAt(0).toUpperCase() + qeLinkPhase.slice(1)
      : null;

  return (
    <div className="panel panel--glass systems-panel animate-in animate-in--delay-2">
      <h2>Systems</h2>
      <ul className="systems-list">
        <li className={`systems-row systems-row--${qeConnection}`}>
          <span className="systems-glyph" aria-hidden>
            ◉
          </span>
          <div>
            <span className="systems-name">QE Engine</span>
            <span className="systems-state">
              {phase ??
                (qeConnection === "connected" ? "Connected" : CONNECTION_COPY[qeConnection])}
            </span>
          </div>
        </li>
      </ul>
      {setupHint && qeConnection === "unconfigured" && (
        <p className="hint systems-hint">{setupHint}</p>
      )}
    </div>
  );
}

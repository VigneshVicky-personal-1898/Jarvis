// AI-ASSISTED: Cursor
// PROMPT: Safe execution metadata panel (no chain-of-thought)
// ACCEPTED-BY: vignesh

type Props = {
  enabled: boolean;
  last?: {
    intent?: string;
    source?: string;
    tool?: string;
    duration_ms?: number;
  };
};

export function ExecutionDebug({ enabled, last }: Props) {
  if (!enabled || !last) return null;
  return (
    <div className="panel panel--glass debug-panel">
      <h2>Debug</h2>
      <dl className="debug-dl">
        <dt>Intent</dt>
        <dd>{last.intent ?? "—"}</dd>
        <dt>Source</dt>
        <dd>{last.source ?? "—"}</dd>
        <dt>Tool</dt>
        <dd>{last.tool ?? "—"}</dd>
        <dt>Duration</dt>
        <dd>{last.duration_ms != null ? `${last.duration_ms} ms` : "—"}</dd>
      </dl>
    </div>
  );
}

// AI-ASSISTED: Cursor
// PROMPT: Activity log renders QE test plan result JSON from data.result
// ACCEPTED-BY: vignesh

import type { ProcessResponse } from "../services/api";

export type LogEntry = {
  id: string;
  time: string;
  input: string;
  response: ProcessResponse;
};

type Props = {
  log: LogEntry[];
};

export function ActivityLog({ log }: Props) {
  return (
    <div className="panel panel--glass log-panel animate-in animate-in--delay-3">
      <h2>Activity</h2>
      <ul className="log">
        {log.length === 0 && <li className="log-empty">No activity yet.</li>}
        {log.map((entry, index) => (
          <li
            key={entry.id}
            className={`log-item ${index === 0 ? "log-item--new" : ""}`}
          >
            <time>{entry.time}</time>
            <p className="log-in">{entry.input}</p>
            <p className="log-out">{entry.response.speak || "—"}</p>
            {entry.response.data?.result != null &&
              typeof entry.response.data.result === "object" && (
                <pre className="log-detail log-detail--pre">
                  {JSON.stringify(
                    entry.response.data.result as Record<string, unknown>,
                    null,
                    2,
                  ).slice(0, 2500)}
                </pre>
              )}
            {entry.response.data?.answer != null && (
              <p className="log-detail">
                {String(entry.response.data.answer)}
              </p>
            )}
            {entry.response.data?.answer == null &&
              entry.response.action?.startsWith("qe_") &&
              entry.response.data &&
              typeof entry.response.data === "object" &&
              "status" in (entry.response.data as Record<string, unknown>) && (
                <pre className="log-detail log-detail--pre">
                  {JSON.stringify(entry.response.data, null, 2).slice(0, 2000)}
                </pre>
              )}
          </li>
        ))}
      </ul>
    </div>
  );
}

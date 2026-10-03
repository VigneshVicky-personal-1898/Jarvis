// AI-ASSISTED: Cursor
// PROMPT: Glass panels for command and tool catalog
// ACCEPTED-BY: vignesh

import type { CommandSummary, ToolSummary } from "../services/api";

type Props = {
  commands: CommandSummary[];
  tools?: ToolSummary[];
};

export function CommandsPanel({ commands, tools }: Props) {
  return (
    <>
      {tools && tools.length > 0 && (
        <div className="panel panel--glass animate-in animate-in--delay-2">
          <h2>Agent tools</h2>
          <ul className="cmd-list">
            {tools.map((t) => (
              <li key={t.name}>
                <span className="cmd-id">{t.name}</span>
                <span className="cmd-ex">{t.description}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="panel panel--glass animate-in animate-in--delay-2">
        <h2>Commands</h2>
        <ul className="cmd-list">
          {commands.map((c) => (
            <li key={c.id}>
              <span className="cmd-id">{c.id}</span>
              <span className="cmd-ex">{c.examples}</span>
            </li>
          ))}
        </ul>
      </div>
    </>
  );
}

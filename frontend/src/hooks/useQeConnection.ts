// AI-ASSISTED: Cursor
// PROMPT: Poll QE status for command-center connection state (no URLs in UI)
// ACCEPTED-BY: vignesh

import { useCallback, useEffect, useState } from "react";
import {
  fetchQeStatus,
  QeStatusError,
  type QeStatusResponse,
} from "../services/api";

export type QeConnectionState =
  | "loading"
  | "unconfigured"
  | "offline"
  | "connected";

export type QeLinkPhase =
  | "idle"
  | "connecting"
  | "processing"
  | "completed"
  | "failed";

export function deriveConnectionState(
  status: QeStatusResponse | null,
  error: boolean,
): QeConnectionState {
  if (error && !status) return "offline";
  if (!status) return "loading";
  if (!status.configured) return "unconfigured";
  if (!status.backend_online) return "offline";
  return "connected";
}

export function useQeConnection(pollMs = 15000) {
  const [status, setStatus] = useState<QeStatusResponse | null>(null);
  const [loadError, setLoadError] = useState(false);
  const [linkPhase, setLinkPhase] = useState<QeLinkPhase>("idle");

  const refresh = useCallback(() => {
    return fetchQeStatus()
      .then((data) => {
        setStatus(data);
        setLoadError(false);
      })
      .catch((err: unknown) => {
        setLoadError(true);
        if (!(err instanceof QeStatusError && err.status === 404)) {
          setStatus(null);
        }
      });
  }, []);

  useEffect(() => {
    refresh();
    const id = window.setInterval(refresh, pollMs);
    return () => window.clearInterval(id);
  }, [pollMs, refresh]);

  const connection = deriveConnectionState(status, loadError);

  const resetLinkSoon = useCallback((delayMs = 3200) => {
    window.setTimeout(() => setLinkPhase("idle"), delayMs);
  }, []);

  return {
    status,
    connection,
    linkPhase,
    setLinkPhase,
    resetLinkSoon,
    refresh,
  };
}

export function utteranceTargetsQe(text: string): boolean {
  const t = text.toLowerCase();
  return (
    /\b(tpx|rtp|rex)-[\w-]+\b/i.test(t) ||
    /\bqe\b|workflow360|test plan|regression|mcp tool/i.test(t)
  );
}

export function isQeToolAction(action: string | null | undefined): boolean {
  if (!action) return false;
  return action.startsWith("qe_") || action.startsWith("mcp_qe");
}

// AI-ASSISTED: Cursor
// PROMPT: Wake/clap activation, ElevenLabs speak, orb voice phases
// ACCEPTED-BY: vignesh

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ActivityLog, type LogEntry } from "../components/ActivityLog";
import { BrandHeader } from "../components/BrandHeader";
import { ConfirmationModal } from "../components/ConfirmationModal";
import { AgentActivityPanel } from "../components/AgentActivityPanel";
import { ExecutionDebug } from "../components/ExecutionDebug";
import { CommandCenter } from "../components/CommandCenter";
import { RayaLogo } from "../components/RayaLogo";
import { RayaStatus, type RayaUiState } from "../components/RayaStatus";
import { Scene3D } from "../components/Scene3D";
import { MetricPanel } from "../components/MetricPanel";
import { SystemsPanel } from "../components/SystemsPanel";
import {
  isQeToolAction,
  utteranceTargetsQe,
  useQeConnection,
} from "../hooks/useQeConnection";
import {
  confirmAction,
  fetchCommands,
  fetchHealth,
  processText,
  type ProcessResponse,
  type UiLanguage as ApiLanguage,
} from "../services/api";
import { UI, type UiLanguage } from "../i18n/uiStrings";
import { useClapDetection } from "../hooks/useClapDetection";
import { resolveRayaVoicePhase } from "../voice/rayaVoicePhase";
import { useSpeech } from "../useSpeech";

function formatTime() {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function Dashboard({ onSignOut }: { onSignOut?: () => void }) {
  const [wakeMode, setWakeMode] = useState(true);
  const [armed, setArmed] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [manual, setManual] = useState("");
  const [commandSession, setCommandSession] = useState<{
    input: string;
    response: ProcessResponse | null;
  } | null>(null);
  const [wakeWords, setWakeWords] = useState<string[]>([]);
  const [log, setLog] = useState<LogEntry[]>([]);
  const [statusLine, setStatusLine] = useState("Ready");
  const [metrics, setMetrics] = useState<Record<string, number> | null>(null);
  const [llmOnline, setLlmOnline] = useState<boolean | undefined>(
    undefined,
  );
  const [uiState, setUiState] = useState<RayaUiState>("IDLE");
  const [lastIntent, setLastIntent] = useState<string | undefined>();
  const [debugMode, setDebugMode] = useState(false);
  const [debugMeta, setDebugMeta] = useState<Record<string, unknown>>({});
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmMsg, setConfirmMsg] = useState("");
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const [activated, setActivated] = useState(false);
  const [clapMode, setClapMode] = useState(true);
  const [ttsAvailable, setTtsAvailable] = useState(false);
  const sleepRef = useRef(false);
  const armedRef = useRef(armed);
  const wakeModeRef = useRef(wakeMode);
  const wakeWordsRef = useRef(wakeWords);
  const wakeHitDebounce = useRef(0);
  const triggerActivationRef = useRef<(source: "wake" | "clap") => void>(() => {});
  const speakRef = useRef<(text: string) => Promise<void>>(async () => {});
  armedRef.current = armed;
  wakeModeRef.current = wakeMode;
  wakeWordsRef.current = wakeWords;
  const [language, setLanguage] = useState<UiLanguage>(() => {
    const saved =
      localStorage.getItem("raya_lang");
    return saved === "ta" ? "ta" : "en";
  });
  const uiCopy = UI[language];
  const {
    connection: qeConnection,
    linkPhase: qeLinkPhase,
    setLinkPhase: setQeLinkPhase,
    resetLinkSoon,
  } = useQeConnection();

  const applyResponse = useCallback(
    (res: ProcessResponse, inputLabel: string) => {
      if (res.data?.sleep) {
        sleepRef.current = true;
        setArmed(false);
        setUiState("SLEEPING");
      } else if (res.ui_state) {
        setUiState(res.ui_state as RayaUiState);
      }
      setLastIntent(res.intent);
      const exec = res.data?.execution as Record<string, unknown> | undefined;
      if (exec) setDebugMeta(exec);

      if (res.data?.requires_confirmation && res.data?.confirmation_id) {
        setConfirmId(String(res.data.confirmation_id));
        setConfirmMsg(res.speak);
        setConfirmOpen(true);
        setUiState("WAITING_CONFIRMATION");
      }

      if (res.data && "cpu_percent" in res.data) {
        setMetrics(res.data as Record<string, number>);
      }

      setCommandSession((prev) => ({
        input: prev?.input ?? inputLabel,
        response: res,
      }));

      setLog((prev) => [
        {
          id: crypto.randomUUID(),
          time: formatTime(),
          input: inputLabel,
          response: res,
        },
        ...prev.slice(0, 49),
      ]);

      if (res.speak && !res.data?.requires_confirmation) {
        setUiState("SPEAKING");
        void speakRef.current(res.speak).finally(() => {
          if (sleepRef.current) return;
          setUiState("IDLE");
          setActivated(false);
          if (wakeModeRef.current) setArmed(false);
        });
      }
      if (isQeToolAction(res.action)) {
        setQeLinkPhase(res.ok ? "completed" : "failed");
        resetLinkSoon();
      }
      const source = res.data?.source as string | undefined;
      setStatusLine(
        res.unmatched
          ? "Unknown command"
          : `${res.intent ?? res.command_id ?? "—"}${source ? ` · ${source}` : ""}`,
      );
    },
    [resetLinkSoon, setQeLinkPhase],
  );

  const handleUtterance = useCallback(
    async (text: string, opts?: { skipWakeGate?: boolean }) => {
      if (processing) return;
      setCommandSession({ input: text, response: null });
      setProcessing(true);
      setStatusLine("Processing…");
      try {
        let payload = text;

        if (wakeMode && !opts?.skipWakeGate) {
          const lower = text.toLowerCase();
          const hit = wakeWords.some((w) => lower.includes(w));
          if (!armed && !hit) {
            setProcessing(false);
            return;
          }
          if (hit) {
            for (const w of wakeWords) {
              payload = payload.replace(new RegExp(w, "gi"), " ").trim();
            }
            payload = payload.replace(/\s+/g, " ").trim();
            if (!armed && !payload) {
              triggerActivationRef.current("wake");
              setProcessing(false);
              return;
            }
            setArmed(true);
            sleepRef.current = false;
          }
          if (!payload) {
            setProcessing(false);
            return;
          }
        }

        setUiState("PROCESSING");
        const qeCommand = utteranceTargetsQe(payload);
        if (qeCommand) {
          setQeLinkPhase("connecting");
          window.setTimeout(() => setQeLinkPhase("processing"), 480);
        }
        const res = await processText(payload, false, language as ApiLanguage);
        applyResponse(res, text);
      } catch {
        setUiState("ERROR");
        setStatusLine("Backend unreachable — start the API server.");
        void speakRef.current("I cannot reach the RAYA server.");
      } finally {
        setProcessing(false);
      }
    },
    [applyResponse, armed, language, processing, setQeLinkPhase, wakeMode, wakeWords],
  );

  const onInterimWake = useCallback((text: string) => {
    if (!wakeModeRef.current || armedRef.current || sleepRef.current) return;
    const lower = text.toLowerCase();
    const hit =
      /\braya\b/.test(lower) ||
      wakeWordsRef.current.some((w) => lower.includes(w.toLowerCase()));
    if (!hit) return;
    const now = Date.now();
    if (now - wakeHitDebounce.current < 2000) return;
    wakeHitDebounce.current = now;
    triggerActivationRef.current("wake");
  }, []);

  const { listening, speaking, interim, supported, micError, start, stop, speak } =
    useSpeech(handleUtterance, language, {
      onInterim: onInterimWake,
      useElevenLabs: ttsAvailable,
    });

  const triggerActivation = useCallback(
    async (source: "wake" | "clap") => {
      if (sleepRef.current) return;
      setActivated(true);
      setUiState("ACTIVATED");
      setArmed(true);
      sleepRef.current = false;
      setStatusLine(
        source === "clap"
          ? "Clap detected — say your command…"
          : "RAYA activated — say your command…",
      );
      if (!listening) await start();
      setUiState("LISTENING");
      void speak("Yes?");
    },
    [listening, speak, start],
  );

  useEffect(() => {
    triggerActivationRef.current = triggerActivation;
  }, [triggerActivation]);

  useClapDetection({
    enabled: wakeMode && clapMode && uiState !== "SLEEPING",
    onClap: () => triggerActivation("clap"),
  });

  useEffect(() => {
    if (!wakeMode || !supported) {
      stop();
      return;
    }
    let cancelled = false;
    void start().then((ok) => {
      if (cancelled || !ok) return;
      setStatusLine('Listening for “Raya” or clap…');
      setUiState("IDLE");
    });
    return () => {
      cancelled = true;
    };
  }, [wakeMode, supported, start, stop]);

  useEffect(() => {
    localStorage.setItem("raya_lang", language);
    document.documentElement.lang = language === "ta" ? "ta" : "en";
  }, [language]);

  const micErrorMessage = (() => {
    switch (micError) {
      case "unsupported":
        return "Speech recognition is not available in this browser. Use Chrome or Edge.";
      case "not-allowed":
        return "Microphone blocked. Allow mic access for this site in browser settings.";
      case "audio-capture":
        return "No microphone found. Plug in a mic or check system sound settings.";
      case "network":
        return "Speech recognition needs internet (Chrome sends audio for transcription).";
      case "unknown":
        return "Could not start the microphone. Click Start again or reload the page.";
      default:
        return null;
    }
  })();

  useEffect(() => {
    speakRef.current = speak;
  }, [speak]);

  useEffect(() => {
    fetchCommands()
      .then((d) => {
        setWakeWords(d.wake_words);
      })
      .catch(() => setStatusLine("Could not load commands from API"));
    fetchHealth()
      .then((h) => {
        setLlmOnline(h.llm_available && h.agent_enabled);
        setDebugMode(Boolean(h.debug_mode));
        setTtsAvailable(Boolean(h.tts_available));
        if (!h.llm_available) setUiState("OFFLINE");
      })
      .catch(() => setLlmOnline(undefined));
  }, []);

  const toggleMic = async () => {
    if (listening) {
      stop();
      setStatusLine("Microphone stopped");
      return;
    }
    setArmed(!wakeMode);
    setStatusLine("Requesting microphone…");
    const started = await start();
    if (started) setUiState("LISTENING");
    setStatusLine(
      started
        ? wakeMode
          ? "Say wake word…"
          : "Listening…"
        : "Microphone could not start — see message below.",
    );
  };

  const handleConfirm = async () => {
    if (!confirmId) return;
    setConfirmOpen(false);
    setUiState("EXECUTING");
    try {
      const res = await confirmAction(confirmId, true);
      applyResponse(res, "confirm");
    } finally {
      setConfirmId(null);
    }
  };

  const handleConfirmCancel = async () => {
    if (confirmId) await confirmAction(confirmId, false);
    setConfirmOpen(false);
    setConfirmId(null);
    setUiState("IDLE");
    setStatusLine("Cancelled");
    setCommandSession(null);
  };

  const submitManual = async (e: React.FormEvent) => {
    e.preventDefault();
    const t = manual.trim();
    if (!t) return;
    setManual("");
    setArmed(true);
    await handleUtterance(t, { skipWakeGate: true });
  };

  const showAgentActivity = useMemo(() => {
    if (confirmOpen || processing || listening || speaking) return true;
    if (commandSession) return true;
    const liveStates: RayaUiState[] = [
      "ACTIVATED",
      "LISTENING",
      "PROCESSING",
      "THINKING",
      "EXECUTING",
      "WAITING_CONFIRMATION",
      "SPEAKING",
      "ERROR",
    ];
    return liveStates.includes(uiState);
  }, [commandSession, confirmOpen, listening, processing, speaking, uiState]);

  useEffect(() => {
    if (processing || listening || confirmOpen) return;
    if (!commandSession) return;
    const dwellMs = commandSession.response ? 12000 : 6000;
    const t = window.setTimeout(() => setCommandSession(null), dwellMs);
    return () => window.clearTimeout(t);
  }, [commandSession, confirmOpen, listening, processing]);

  const voicePhase = resolveRayaVoicePhase({
    uiState,
    listening,
    processing,
    speaking,
    activated,
    qeLinkPhase,
  });

  const statusForOrb: RayaUiState =
    voicePhase === "activated"
      ? "ACTIVATED"
      : voicePhase === "listening"
        ? "LISTENING"
        : voicePhase === "thinking"
          ? "PROCESSING"
          : voicePhase === "executing"
            ? "EXECUTING"
            : voicePhase === "speaking"
              ? "SPEAKING"
              : uiState;

  return (
    <div className="app">
      <Scene3D />
      <div className="grid-bg" aria-hidden />
      <BrandHeader
        onSignOut={onSignOut}
        wakeMode={wakeMode}
        llmOnline={llmOnline}
        language={language}
        onLanguageChange={setLanguage}
        listening={listening}
        micSupported={supported}
        onMicToggle={toggleMic}
        clapMode={clapMode}
        onClapModeChange={setClapMode}
        ttsOnline={ttsAvailable}
        onWakeModeChange={(enabled) => {
          setWakeMode(enabled);
          setArmed(!enabled);
          if (!enabled) {
            setActivated(false);
            setClapMode(false);
          } else {
            setClapMode(true);
          }
        }}
      />

      <main
        className={`main ${showAgentActivity ? "main--triptych" : ""}`}
      >
        {showAgentActivity && (
          <aside className="rail rail--command animate-in">
            <AgentActivityPanel
              visible
              listening={listening}
              processing={processing}
              interim={interim}
              uiState={uiState}
              intent={lastIntent}
              commandInput={commandSession?.input}
              response={commandSession?.response ?? null}
              executionMeta={debugMeta}
            />
            {debugMode && (
              <ExecutionDebug
                enabled
                last={{
                  intent: String(debugMeta.intent ?? lastIntent ?? ""),
                  source: String(debugMeta.source ?? ""),
                  tool: String(
                    (debugMeta.debug as Record<string, unknown> | undefined)
                      ?.tool ?? "",
                  ),
                  duration_ms: debugMeta.duration_ms as number | undefined,
                }}
              />
            )}
          </aside>
        )}

        <section className="hero animate-in animate-in--delay-1">
          <CommandCenter
            qeConnection={qeConnection}
            qeLinkPhase={qeLinkPhase}
            llmOnline={llmOnline}
          >
            <RayaLogo phase={voicePhase} interim={interim} />
          </CommandCenter>
          <RayaStatus state={statusForOrb} intent={lastIntent} />
          <p
            className={`status ${processing ? "status--busy" : ""}`}
            key={statusLine}
          >
            {statusLine}
          </p>
          {(!supported || micErrorMessage) && (
            <p className="warn" role="alert">
              {micErrorMessage ??
                "Speech recognition needs Chromium (Chrome/Edge). Type commands below."}
            </p>
          )}
          <form
            className="manual-form animate-in animate-in--delay-3"
            onSubmit={submitManual}
          >
            <input
              value={manual}
              onChange={(e) => setManual(e.target.value)}
              placeholder={uiCopy.manualPlaceholder}
              aria-label="Manual command"
            />
            <button type="submit" className="btn btn-ghost">
              {uiCopy.send}
            </button>
          </form>
          {wakeMode && wakeWords.length > 0 && (
            <p className="hint">
              Wake words: <code>{wakeWords.join('", "')}</code>
              {armed ? " · command channel open" : ""}
            </p>
          )}
        </section>

        {showAgentActivity ? (
          <aside className="rail rail--activity animate-in">
            <ActivityLog log={log.slice(0, 8)} />
          </aside>
        ) : (
          <aside className="sidebar animate-in animate-in--delay-2">
            {metrics && <MetricPanel metrics={metrics} />}
            <SystemsPanel
              qeConnection={qeConnection}
              qeLinkPhase={qeLinkPhase}
            />
            <ExecutionDebug
              enabled={debugMode}
              last={{
                intent: String(debugMeta.intent ?? lastIntent ?? ""),
                source: String(debugMeta.source ?? ""),
                tool: String(
                  (debugMeta.debug as Record<string, unknown> | undefined)
                    ?.tool ?? "",
                ),
                duration_ms: debugMeta.duration_ms as number | undefined,
              }}
            />
          </aside>
        )}
      </main>
      <ConfirmationModal
        open={confirmOpen}
        message={confirmMsg}
        confirmationId={confirmId}
        onConfirm={handleConfirm}
        onCancel={handleConfirmCancel}
      />
    </div>
  );
}

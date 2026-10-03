// AI-ASSISTED: Cursor
// PROMPT: Pause STT during TTS playback; ElevenLabs with browser fallback
// ACCEPTED-BY: vignesh

import { useCallback, useEffect, useRef, useState } from "react";
import { fetchTts } from "./services/api";

type SpeechRecognitionCtor = new () => SpeechRecognition;

function getRecognitionCtor(): SpeechRecognitionCtor | null {
  const w = window as Window &
    typeof globalThis & {
      SpeechRecognition?: SpeechRecognitionCtor;
      webkitSpeechRecognition?: SpeechRecognitionCtor;
    };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

export type MicErrorCode =
  | "unsupported"
  | "not-allowed"
  | "network"
  | "no-speech"
  | "audio-capture"
  | "aborted"
  | "unknown";

export type SpeechLanguage = "en" | "ta";

const STT_LANG: Record<SpeechLanguage, string> = {
  en: "en-IN",
  ta: "ta-IN",
};

type UseSpeechOptions = {
  onInterim?: (text: string) => void;
  useElevenLabs?: boolean;
};

export function useSpeech(
  onFinal: (text: string) => void,
  language: SpeechLanguage = "en",
  options: UseSpeechOptions = {},
) {
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [interim, setInterim] = useState("");
  const [supported, setSupported] = useState(true);
  const [micError, setMicError] = useState<MicErrorCode | null>(null);
  const recRef = useRef<SpeechRecognition | null>(null);
  const wantListenRef = useRef(false);
  const restartingRef = useRef(false);
  const holdingRestartRef = useRef(false);
  const onFinalRef = useRef(onFinal);
  const onInterimRef = useRef(options.onInterim);
  const useElevenLabsRef = useRef(options.useElevenLabs ?? false);
  onFinalRef.current = onFinal;
  onInterimRef.current = options.onInterim;
  useElevenLabsRef.current = options.useElevenLabs ?? false;

  const attachHandlers = useCallback((rec: SpeechRecognition) => {
    rec.onresult = (event: SpeechRecognitionEvent) => {
      if (holdingRestartRef.current) return;
      setMicError(null);
      let interimText = "";
      let finalText = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalText += t;
        else interimText += t;
      }
      const interimTrim = interimText.trim();
      setInterim(interimTrim);
      if (interimTrim) onInterimRef.current?.(interimTrim);
      if (finalText.trim()) onFinalRef.current(finalText.trim());
    };

    rec.onend = () => {
      setListening(false);
      setInterim("");
      if (holdingRestartRef.current) return;
      if (!wantListenRef.current || restartingRef.current) return;
      restartingRef.current = true;
      window.setTimeout(() => {
        restartingRef.current = false;
        const r = recRef.current;
        if (!wantListenRef.current || !r) return;
        try {
          r.start();
          setListening(true);
        } catch {
          window.setTimeout(() => {
            if (!wantListenRef.current || !recRef.current) return;
            try {
              recRef.current.start();
              setListening(true);
            } catch {
              wantListenRef.current = false;
              setMicError("unknown");
            }
          }, 250);
        }
      }, 120);
    };

    rec.onerror = (event: SpeechRecognitionErrorEvent) => {
      const code = event.error as MicErrorCode;
      if (code === "aborted" && !wantListenRef.current) return;
      if (code === "no-speech" && wantListenRef.current) return;
      if (code === "not-allowed" || code === "audio-capture") {
        wantListenRef.current = false;
        setListening(false);
        setMicError(code);
        return;
      }
      if (code === "network") setMicError("network");
    };
  }, []);

  useEffect(() => {
    const Ctor = getRecognitionCtor();
    if (!Ctor) {
      setSupported(false);
      setMicError("unsupported");
      return;
    }

    const rec = new Ctor();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = STT_LANG[language];
    rec.maxAlternatives = 1;
    attachHandlers(rec);
    recRef.current = rec;

    return () => {
      wantListenRef.current = false;
      try {
        rec.abort();
      } catch {
        try {
          rec.stop();
        } catch {
          /* ignore */
        }
      }
      recRef.current = null;
    };
  }, [attachHandlers, language]);

  useEffect(() => {
    const rec = recRef.current;
    if (rec) rec.lang = STT_LANG[language];
  }, [language]);

  const ensureMicPermission = useCallback(async (): Promise<boolean> => {
    if (!navigator.mediaDevices?.getUserMedia) return true;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((t) => t.stop());
      setMicError(null);
      return true;
    } catch {
      setMicError("not-allowed");
      return false;
    }
  }, []);

  const start = useCallback(async (): Promise<boolean> => {
    if (listening || wantListenRef.current) return true;
    const Ctor = getRecognitionCtor();
    if (!Ctor) {
      setSupported(false);
      setMicError("unsupported");
      return false;
    }

    const ok = await ensureMicPermission();
    if (!ok) return false;

    if (!recRef.current) {
      const rec = new Ctor();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = STT_LANG[language];
      rec.maxAlternatives = 1;
      attachHandlers(rec);
      recRef.current = rec;
    } else {
      recRef.current.lang = STT_LANG[language];
    }

    wantListenRef.current = true;
    try {
      recRef.current.start();
      setListening(true);
      setMicError(null);
      return true;
    } catch {
      return await new Promise<boolean>((resolve) => {
        window.setTimeout(() => {
          if (!recRef.current || !wantListenRef.current) {
            resolve(false);
            return;
          }
          try {
            recRef.current.start();
            setListening(true);
            setMicError(null);
            resolve(true);
          } catch {
            wantListenRef.current = false;
            setMicError("unknown");
            resolve(false);
          }
        }, 200);
      });
    }
  }, [attachHandlers, ensureMicPermission, language, listening]);

  const stop = useCallback(() => {
    wantListenRef.current = false;
    restartingRef.current = false;
    const rec = recRef.current;
    if (rec) {
      try {
        rec.stop();
      } catch {
        try {
          rec.abort();
        } catch {
          /* ignore */
        }
      }
    }
    setListening(false);
    setInterim("");
  }, []);

  const speakBrowser = useCallback(
    (text: string) =>
      new Promise<void>((resolve) => {
        if (!window.speechSynthesis) {
          resolve();
          return;
        }
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(text);
        u.rate = 1;
        u.pitch = 0.95;
        u.lang = STT_LANG[language];
        const voices = window.speechSynthesis.getVoices();
        const voice =
          voices.find((v) => v.lang.startsWith(STT_LANG[language].slice(0, 2))) ??
          voices.find((v) => v.lang.startsWith("en"));
        if (voice) u.voice = voice;
        u.onend = () => resolve();
        u.onerror = () => resolve();
        window.speechSynthesis.speak(u);
      }),
    [language],
  );

  const resumeListeningAfterTts = useCallback(() => {
    holdingRestartRef.current = false;
    if (!wantListenRef.current || !recRef.current) return;
    try {
      recRef.current.start();
      setListening(true);
    } catch {
      window.setTimeout(() => {
        if (!wantListenRef.current || !recRef.current) return;
        try {
          recRef.current.start();
          setListening(true);
        } catch {
          /* ignore */
        }
      }, 200);
    }
  }, []);

  const speak = useCallback(
    async (text: string) => {
      if (!text.trim()) return;
      setSpeaking(true);
      holdingRestartRef.current = true;
      const rec = recRef.current;
      if (rec && wantListenRef.current) {
        try {
          rec.stop();
        } catch {
          /* ignore */
        }
      }
      try {
        if (useElevenLabsRef.current) {
          try {
            const blob = await fetchTts(text, language);
            const url = URL.createObjectURL(blob);
            await new Promise<void>((resolve, reject) => {
              const audio = new Audio(url);
              audio.onended = () => {
                URL.revokeObjectURL(url);
                resolve();
              };
              audio.onerror = () => {
                URL.revokeObjectURL(url);
                reject(new Error("audio playback failed"));
              };
              void audio.play();
            });
            return;
          } catch {
            /* fall through to browser */
          }
        }
        await speakBrowser(text);
      } finally {
        setSpeaking(false);
        resumeListeningAfterTts();
      }
    },
    [language, resumeListeningAfterTts, speakBrowser],
  );

  useEffect(() => {
    const loadVoices = () => window.speechSynthesis?.getVoices();
    loadVoices();
    window.speechSynthesis?.addEventListener("voiceschanged", loadVoices);
    return () =>
      window.speechSynthesis?.removeEventListener("voiceschanged", loadVoices);
  }, []);

  const clearMicError = useCallback(() => setMicError(null), []);

  return {
    listening,
    speaking,
    interim,
    supported,
    micError,
    clearMicError,
    start,
    stop,
    speak,
  };
}

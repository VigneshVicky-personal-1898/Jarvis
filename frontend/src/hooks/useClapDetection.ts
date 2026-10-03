// AI-ASSISTED: Cursor
// PROMPT: Background clap detection to activate RAYA listening
// ACCEPTED-BY: vignesh

import { useEffect, useRef } from "react";

type Options = {
  enabled: boolean;
  onClap: () => void;
  threshold?: number;
  cooldownMs?: number;
};

export function useClapDetection({
  enabled,
  onClap,
  threshold = 0.22,
  cooldownMs = 1800,
}: Options) {
  const onClapRef = useRef(onClap);
  onClapRef.current = onClap;

  useEffect(() => {
    if (!enabled) return;

    let ctx: AudioContext | null = null;
    let analyser: AnalyserNode | null = null;
    let stream: MediaStream | null = null;
    let raf = 0;
    let lastClap = 0;
    let prevEnergy = 0;
    let cancelled = false;

    const loop = () => {
      if (!analyser || cancelled) return;
      const buf = new Uint8Array(analyser.fftSize);
      analyser.getByteTimeDomainData(buf);
      let sum = 0;
      for (let i = 0; i < buf.length; i++) {
        const v = (buf[i] - 128) / 128;
        sum += v * v;
      }
      const rms = Math.sqrt(sum / buf.length);
      const spike = rms - prevEnergy;
      prevEnergy = rms * 0.85 + prevEnergy * 0.15;
      const now = Date.now();
      if (
        rms > threshold &&
        spike > threshold * 0.65 &&
        now - lastClap > cooldownMs
      ) {
        lastClap = now;
        onClapRef.current();
      }
      raf = requestAnimationFrame(loop);
    };

    const start = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
          },
        });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        ctx = new AudioContext();
        const source = ctx.createMediaStreamSource(stream);
        analyser = ctx.createAnalyser();
        analyser.fftSize = 2048;
        source.connect(analyser);
        raf = requestAnimationFrame(loop);
      } catch {
        /* mic may be owned by STT — clap optional */
      }
    };

    void start();

    return () => {
      cancelled = true;
      cancelAnimationFrame(raf);
      stream?.getTracks().forEach((t) => t.stop());
      void ctx?.close();
    };
  }, [enabled, threshold, cooldownMs]);
}

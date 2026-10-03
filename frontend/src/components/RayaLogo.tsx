// AI-ASSISTED: Cursor
// PROMPT: Orb animation mapped to RAYA voice lifecycle phases
// ACCEPTED-BY: vignesh

import { JarvisOrb, type JarvisState } from "jarvis-ai-web-animation";
import {
  activatedState,
  executingState,
  listeningState,
  personalRayaPalette,
  speakingState,
} from "./rayaOrbConfig";
import type { RayaVoicePhase } from "../voice/rayaVoicePhase";

type Props = {
  phase: RayaVoicePhase;
  interim?: string;
};

function orbStateForPhase(phase: RayaVoicePhase): JarvisState {
  switch (phase) {
    case "speaking":
      return speakingState;
    case "executing":
      return executingState;
    case "thinking":
      return "thinking";
    case "listening":
      return listeningState;
    case "activated":
      return activatedState;
    default:
      return "idle";
  }
}

export function RayaLogo({ phase, interim }: Props) {
  const orbState = orbStateForPhase(phase);

  return (
    <div className={`raya-orb-wrap raya-orb-wrap--${phase}`}>
      <div className="raya-orb-frame">
        <JarvisOrb
          size="hero"
          state={orbState}
          palette={personalRayaPalette}
          quality="auto"
          interactive
          breathing
          breathingIntensity={phase === "idle" ? 1.1 : 1.25}
          draggableSpin={false}
          ariaLabel={`RAYA ${phase}`}
          className="raya-orb-canvas"
        />
        <img
          className="raya-orb-emblem"
          src="/assets/raya-logo.jpg"
          alt=""
          width={72}
          height={72}
          draggable={false}
        />
      </div>
      {interim && <p className="interim">{interim}</p>}
      <div className="raya-orb-shadow" aria-hidden />
    </div>
  );
}

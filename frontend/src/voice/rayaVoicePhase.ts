// AI-ASSISTED: Cursor
// PROMPT: Map pipeline UI to orb animation phases
// ACCEPTED-BY: vignesh

import type { RayaUiState } from "../components/RayaStatus";
import type { QeLinkPhase } from "../hooks/useQeConnection";

export type RayaVoicePhase =
  | "idle"
  | "activated"
  | "listening"
  | "thinking"
  | "executing"
  | "speaking";

type Input = {
  uiState: RayaUiState;
  listening: boolean;
  processing: boolean;
  speaking: boolean;
  activated: boolean;
  qeLinkPhase: QeLinkPhase;
};

export function resolveRayaVoicePhase(input: Input): RayaVoicePhase {
  if (input.speaking || input.uiState === "SPEAKING") return "speaking";
  if (
    input.uiState === "EXECUTING" ||
    input.qeLinkPhase === "processing" ||
    input.qeLinkPhase === "connecting"
  ) {
    return "executing";
  }
  if (
    input.processing ||
    input.uiState === "PROCESSING" ||
    input.uiState === "THINKING"
  ) {
    return "thinking";
  }
  if (input.uiState === "ACTIVATED") return "activated";
  if (input.listening || input.uiState === "LISTENING") {
    return input.activated ? "listening" : "idle";
  }
  if (input.activated) return "activated";
  return "idle";
}

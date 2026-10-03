// AI-ASSISTED: Cursor
// PROMPT: RAYA orb palette and listening state (jarvis-ai-web-animation types)
// ACCEPTED-BY: vignesh

import type { JarvisPaletteValues, JarvisStateTarget } from "jarvis-ai-web-animation";

export const personalRayaPalette: JarvisPaletteValues = {
  core: 0xfff8eb,
  primary: 0xe8a838,
  secondary: 0x22d3ee,
  tertiary: 0xf5d078,
  deep: 0x0a0e14,
  fallback:
    "radial-gradient(circle at 50% 45%, #fff8eb 0%, #e8a838 30%, #22d3ee 55%, #0a0e14 78%, transparent)",
};

export const listeningState: JarvisStateTarget = {
  energy: 1.45,
  rotationSpeed: 0.65,
  particleSpeed: 1.75,
  shellRadius: 1.1,
  ringSpread: 1.05,
  filamentOpacity: 0.75,
  coreScale: 1.12,
  bloom: 0.95,
};

export const activatedState: JarvisStateTarget = {
  energy: 1.25,
  rotationSpeed: 0.85,
  particleSpeed: 1.4,
  shellRadius: 1.05,
  ringSpread: 1.02,
  filamentOpacity: 0.82,
  coreScale: 1.08,
  bloom: 0.88,
};

export const executingState: JarvisStateTarget = {
  energy: 1.6,
  rotationSpeed: 1.1,
  particleSpeed: 2.1,
  shellRadius: 1.15,
  ringSpread: 1.08,
  filamentOpacity: 0.9,
  coreScale: 1.05,
  bloom: 1.05,
};

export const speakingState: JarvisStateTarget = {
  energy: 1.35,
  rotationSpeed: 0.45,
  particleSpeed: 1.2,
  shellRadius: 1.08,
  ringSpread: 1.0,
  filamentOpacity: 0.85,
  coreScale: 1.15,
  bloom: 1.1,
};

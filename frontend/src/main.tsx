// AI-ASSISTED: Cursor
// PROMPT: React entry point for Jarvis UI
// ACCEPTED-BY: vignesh

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

// AI-ASSISTED: Cursor
// PROMPT: Vite dev server with API proxy to FastAPI
// ACCEPTED-BY: vignesh

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8765",
    },
  },
});

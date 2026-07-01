import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy /api/* to the FastAPI backend during dev so the browser makes
// same-origin calls (no CORS) and the backend keeps its plain paths.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});

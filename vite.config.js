import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api-health": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
        rewrite: () => "/",
      },
      "/auth": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
      "/project": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
      "/target": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
      "/scan": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
      "/finding": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
      "/report": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
  },
});

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Static-site friendly: relative base so the build can be served from any
// path (GitHub Pages, a subdirectory, file://, etc.).
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "dist",
    assetsDir: "assets",
  },
});

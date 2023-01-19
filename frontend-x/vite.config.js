import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import dsv from "@rollup/plugin-dsv";
import { join } from "path";

// https://vitejs.dev/config/
export default defineConfig({
  base: "./",
  plugins: [vue(), dsv()],
  resolve: {
    alias: {
      "@": join(__dirname, "src"),
    },
  },
});

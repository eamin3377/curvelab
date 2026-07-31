import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// GitHub Pages serves at https://<user>.github.io/<repo>/, so the base
// must match the repo name. Override with VITE_BASE_URL for other hosts.
const BASE = process.env.VITE_BASE_URL ?? '/curvelab/'

export default defineConfig({
  base: BASE,
  plugins: [react(), tailwindcss()],
  build: {
    chunkSizeWarningLimit: 1600,
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (id.includes('plotly.js-basic-dist-min')) return 'plotly'
          if (id.includes('katex')) return 'katex'
        },
      },
    },
  },
})

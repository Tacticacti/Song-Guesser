import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      // forward API calls to the Python backend (uvicorn)
      '/api': 'http://127.0.0.1:8000',
    },
  },
})

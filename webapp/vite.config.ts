import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { run } from 'vite-plugin-run'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    run({input: [
      {
        name: 'import data',
        run: ['npm run data'],
        pattern: ['../cache/*.json'],
      },
    ], silent: false}),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})

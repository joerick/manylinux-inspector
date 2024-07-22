import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { run } from 'vite-plugin-run'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        run({
            input: [
                {
                    name: 'import data',
                    run: ['npm run data'],
                    pattern: ['../data/**/*.json', 'import_data.py'],
                    build: false,  // don't run for build, just for dev
                },
            ],
            silent: false,
        }),
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    }
})

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from "node:url";

// https://vite.dev/config/
export default defineConfig({
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
    plugins: [vue()],
    server: {
        port: 8080,
        proxy: {
            "/api-v1": {
                logLevel: "debug",
                secure: false,
                ws: true,
                target: "http://127.0.0.1:9030",
            },
        },
    },
    //build: {
    //    sourcemap: true,
    //},
})

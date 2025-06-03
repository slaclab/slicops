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
                target: process.env.SLICOPS_VITE_TARGET || "http://localhost:9030",
                ws: true,
            },
        },
    },
    //build: {
    //    sourcemap: true,
    //},
})

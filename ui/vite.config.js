import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from "node:url";

// set in sirepo.pkcli.service via $SLICOPS_CONFIG_UI_API_VUE_PORT
const port = process.env.SLICOPS_VUE_PORT || 8008;

// https://vite.dev/config/
export default defineConfig({
    plugins: [
        vue(),
    ],
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
    server: {
        port: port,
        hmr: {
            port: port,
        },
    },
    //build: {
    //    sourcemap: true,
    //},
})

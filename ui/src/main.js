import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/services/router.js'
import "bootstrap"
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap5-toggle"
import "bootstrap5-toggle/css/bootstrap5-toggle.min.css"
import '@/style.css'

createApp(App).use(router).mount('#app')

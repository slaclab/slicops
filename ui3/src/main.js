import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Import global styles
import './assets/styles.css';

// Create Vue application
const app = createApp(App);

// Use router
app.use(router);

// Mount the app
app.mount('#app');

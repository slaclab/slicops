
import { createRouter, createWebHistory } from 'vue-router'
import VApp from '@/components/VApp.vue';

const routes = [
    {
        path: '/',
        component: VApp,
        props: { sliclet: '' },
    },
    {
        path: '/:sliclet(\\w+)',
        component: VApp,
        props: true,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
    linkActiveClass: 'active'
});

export default router;

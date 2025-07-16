
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        redirect: '/screen',
    },
    {
        path: '/:sliclet(\\w+)',
        name: 'Sliclet',
        component: () => import('@/components/VApp.vue'),
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
    linkActiveClass: 'active'
});

router.beforeEach((to, from, next) => {
    document.title = to.name;
    next();
});

export default router;

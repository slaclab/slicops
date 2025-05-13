
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        redirect: '/screen',
    },
    {
        path: '/screen',
        name: 'Screen',
        component: () => import('@/views/Screen.vue'),
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

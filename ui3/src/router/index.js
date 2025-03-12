import { createRouter, createWebHistory } from 'vue-router';
import ScreenComponent from '@/components/ScreenComponent.vue';

const routes = [
  {
    path: '/',
    redirect: '/screen'
  },
  {
    path: '/screen',
    name: 'Screen',
    component: ScreenComponent,
    meta: {
      title: 'Profile Monitor'
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'SlicOps';
  next();
});

export default router;

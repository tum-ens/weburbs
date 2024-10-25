import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      name: 'Landing',
      path: '/',
      component: () => import('@/pages/LandingPage.vue'),
    },
    {
      name: 'Login',
      path: '/login',
      component: () => import('@/pages/LoginPage.vue'),
    },
    {
      name: 'Registration',
      path: '/register',
      component: () => import('@/pages/RegistrationPage.vue'),
    },
    {
      name: 'Reset password',
      path: '/resetPassword',
      component: () => import('@/pages/ResetPasswordPage.vue'),
    },
    {
      name: 'Home',
      path: '/home',
      component: () => import('@/pages/HomePage.vue'),
    },
  ],
})

export default router

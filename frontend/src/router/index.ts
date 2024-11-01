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
      children: [
        {
          name: 'ProjectList',
          path: 'project',
          component: () => import('@/pages/ProjectListPage.vue'),
        },
        {
          name: 'CreateProject',
          path: 'project/create',
          meta: {
            parents: ['ProjectList'],
          },
          component: () =>
            import('@/pages/projectConfigs/ProjectCreatePage.vue'),
        },
        {
          name: 'Project',
          path: 'project/:projId',
          meta: {
            parents: ['ProjectList'],
          },
          component: () => import('@/pages/ProjectListPage.vue'),
        },
      ],
    },
  ],
})

export default router

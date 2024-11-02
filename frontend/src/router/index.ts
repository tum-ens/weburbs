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
          path: 'project/:proj',
          meta: {
            parents: ['ProjectList'],
          },
          component: () => import('@/pages/projectConfigs/ProjectPage.vue'),
        },
        {
          name: 'ProjectConfig',
          path: 'project/:proj/config',
          meta: {
            parents: ['ProjectList'],
          },
          component: () => import('@/pages/projectConfigs/ProjectConfig.vue'),
        },
        {
          name: 'ProjectSites',
          path: 'project/:proj/sites',
          meta: {
            parents: ['ProjectList'],
          },
          component: () => import('@/pages/projectConfigs/SiteConfig.vue'),
        },
        {
          name: 'ProjectProcess',
          path: 'project/:proj/process',
          meta: {
            parents: ['ProjectList'],
          },
          component: () => import('@/pages/projectConfigs/ProcessConfig.vue'),
        },
        {
          name: 'ProjectCommodity',
          path: 'project/:proj/commodity',
          meta: {
            parents: ['ProjectList'],
          },
          component: () => import('@/pages/projectConfigs/CommodityConfig.vue'),
        },
        {
          name: 'ProjectTransmission',
          path: 'project/:proj/transmission',
          meta: {
            parents: ['ProjectList'],
          },
          component: () =>
            import('@/pages/projectConfigs/TransmissionConfig.vue'),
        },
        {
          name: 'ProjectStorage',
          path: 'project/:proj/storage',
          meta: {
            parents: ['ProjectList'],
          },
          component: () => import('@/pages/projectConfigs/StorageConfig.vue'),
        },
        {
          name: 'ProjectDSM',
          path: 'project/:proj/dsm',
          meta: {
            parents: ['ProjectList'],
          },
          component: () => import('@/pages/projectConfigs/DSMConfig.vue'),
        },
        {
          name: 'ProjectDemand',
          path: 'project/:proj/demand',
          meta: {
            parents: ['ProjectList'],
          },
          component: () => import('@/pages/projectConfigs/DemandConfig.vue'),
        },
        {
          name: 'ProjectSuplm',
          path: 'project/:proj/suplm',
          meta: {
            parents: ['ProjectList'],
          },
          component: () => import('@/pages/projectConfigs/SuplmConfig.vue'),
        },
        {
          name: 'ProjectBuySell',
          path: 'project/:proj/buysell',
          meta: {
            parents: ['ProjectList'],
          },
          component: () =>
            import('@/pages/projectConfigs/BuySellPriceConfig.vue'),
        },
        {
          name: 'ProjectTimeVarEff',
          path: 'project/:proj/timevareff',
          meta: {
            parents: ['ProjectList'],
          },
          component: () =>
            import('@/pages/projectConfigs/TimeVarEffConfig.vue'),
        },
        {
          name: 'ProjectSimulation',
          path: 'project/:proj/simulation',
          meta: {
            parents: ['ProjectList'],
          },
          component: () => import('@/pages/simulation/SimulationPage.vue'),
        },
      ],
    },
  ],
})

export default router

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
    {
      name: 'CreateProject',
      path: '/createproj',
      component: () => import('@/pages/projectConfigs/ProjectCreatePage.vue'),
    },
    {
      name: 'Project',
      path: '/project/:proj',
      component: () => import('@/pages/ProjectPage.vue'),
      children: [
        {
          name: 'ProjectConfig',
          path: 'config',
          component: () => import('@/pages/projectConfigs/ProjectConfig.vue'),
        },
        {
          name: 'ProjectSites',
          path: 'sites',
          component: () => import('@/pages/projectConfigs/SiteConfig.vue'),
        },
        {
          name: 'ProjectProcess',
          path: 'process',
          component: () => import('@/pages/projectConfigs/ProcessConfig.vue'),
        },
        {
          name: 'ProjectCommodity',
          path: 'commodity',
          meta: {
            parents: ['advanced'],
          },
          component: () => import('@/pages/projectConfigs/CommodityConfig.vue'),
        },
        {
          name: 'ProjectTransmission',
          path: 'transmission',
          meta: {
            parents: ['advanced'],
          },
          component: () =>
            import('@/pages/projectConfigs/TransmissionConfig.vue'),
        },
        {
          name: 'ProjectStorage',
          path: 'storage',
          component: () => import('@/pages/projectConfigs/StorageConfig.vue'),
        },
        {
          name: 'ProjectDSM',
          path: 'dsm',
          meta: {
            parents: ['advanced'],
          },
          component: () => import('@/pages/projectConfigs/DSMConfig.vue'),
        },
        {
          name: 'ProjectDemand',
          path: 'demand',
          component: () => import('@/pages/projectConfigs/DemandConfig.vue'),
        },
        {
          name: 'ProjectSupIm',
          path: 'supim',
          component: () => import('@/pages/projectConfigs/SupImConfig.vue'),
        },
        {
          name: 'ProjectBuySell',
          path: 'buysell',
          meta: {
            parents: ['advanced'],
          },
          component: () =>
            import('@/pages/projectConfigs/BuySellPriceConfig.vue'),
        },
        {
          name: 'ProjectTimeVarEff',
          path: 'timevareff',
          meta: {
            parents: ['advanced'],
          },
          component: () =>
            import('@/pages/projectConfigs/TimeVarEffConfig.vue'),
        },
        {
          name: 'ProjectSimulation',
          path: 'simulation',
          meta: {
            parents: ['advanced'],
          },
          component: () => import('@/pages/simulation/SimulationPage.vue'),
        },
      ],
    },
  ],
})

export default router

import './assets/base.css'
import 'primeicons/primeicons.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router/routes'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import { VueQueryPlugin } from '@tanstack/vue-query'
import FocusTrap from 'primevue/focustrap'
import axios from 'axios'
import ToastService from 'primevue/toastservice'
import Tooltip from 'primevue/tooltip'
import { ConfirmationService } from 'primevue'

axios.defaults.withCredentials = true

fetch('/config.json')
  .then(response => response.json())
  .then(async data => {
    if (data.VUE_APP_API_URL) axios.defaults.baseURL = data.VUE_APP_API_URL

    // Obtain the CSRF cookie once before the app starts. Otherwise, on a first
    // visit, the session and CSRF queries run in parallel without a cookie,
    // each response sets a different one, and the token the app keeps may not
    // match the cookie the browser stores - so the first login can fail.
    await axios.get('/api/security/csrf/').catch(() => {})

    createApp(App)
      .use(router)
      .use(VueQueryPlugin, {
        enableDevtoolsV6Plugin: true,
      })
      .use(ToastService)
      .use(PrimeVue, {
        theme: {
          preset: Aura,
          options: {
            cssLayer: {
              name: 'primevue',
              order: 'tailwind-base, primevue, tailwind-utilities',
            },
          },
        },
      })
      .use(ConfirmationService)
      .directive('focustrap', FocusTrap)
      .directive('tooltip', Tooltip)
      .mount('#app')
  })

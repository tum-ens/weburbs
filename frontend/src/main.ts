import './assets/base.css'
import 'primeicons/primeicons.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import { VueQueryPlugin } from '@tanstack/vue-query'
import FocusTrap from 'primevue/focustrap'
import axios from 'axios'
import ToastService from 'primevue/toastservice'
import Tooltip from 'primevue/tooltip'

axios.defaults.withCredentials = true
fetch('/config.json')
  .then(response => response.json())
  .then(data => {
    axios.defaults.baseURL = data.VUE_APP_API_URL

    createApp(App)
      .use(router)
      .use(VueQueryPlugin)
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
      .directive('focustrap', FocusTrap)
      .directive('tooltip', Tooltip)
      .mount('#app')
  })

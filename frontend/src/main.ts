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

axios.defaults.baseURL = 'http://localhost:8000'
// axios.defaults.baseURL = 'http://localhost:9000'
// axios.defaults.baseURL = 'https://relaxing-griffon-absolutely.ngrok-free.app'
axios.defaults.withCredentials = true

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

import { createApp } from 'vue'
import App from './App.vue'

import './assets/main.css'
import router from './router'

const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
if (isSafari) {
    document.body.classList.add('is-safari');
}

const app = createApp(App)
app.use(router)
app.mount('#app')

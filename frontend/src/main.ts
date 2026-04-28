import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import "flyonui/flyonui";
import router from './router'

createApp(App).use(createPinia()).use(router).mount('#app')

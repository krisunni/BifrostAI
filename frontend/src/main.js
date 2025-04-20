import { createApp } from 'vue'
import App from './App.vue'
import BubbleViewer from './components/BubbleViewer.vue'

createApp(App)
    .component('BubbleViewer', BubbleViewer)
    .mount('#app')
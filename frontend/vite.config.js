import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/collection': 'http://localhost:5001',
      '/collections': 'http://localhost:5001',
      '/query': 'http://localhost:5001',
      '/query-collection': 'http://localhost:5001',  // Added this line
      '/mqtt/start': 'http://localhost:5001',
      '/mqtt/stop': 'http://localhost:5001',
      '/mqtt/status': 'http://localhost:5001'
    }
  }
})

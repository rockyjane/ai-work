import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    // 開發時把 /api 轉發到 FastAPI，前端就不會踩到 CORS
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})

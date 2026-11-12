import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// 後端 proxy 目標可用環境變數切換，示範「同契約、兩實作」：
//   npm run dev                      → Python FastAPI（8000，預設）
//   VITE_API=http://127.0.0.1:8081 npm run dev  → Java Spring Boot（8081）
// 前端程式碼完全不用改，只換 proxy 目標就切換後端。
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const target = env.VITE_API || 'http://127.0.0.1:8000'
  return {
    plugins: [vue()],
    server: {
      port: 5173,
      // 開發時把 /api 轉發到後端，前端就不會踩到 CORS
      proxy: {
        '/api': target,
      },
    },
  }
})

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const djangoProxyTarget = env.VITE_DJANGO_PROXY_TARGET || 'http://localhost:8000'
  const aiProxyTarget = env.VITE_AI_PROXY_TARGET || 'http://localhost:8001'

  return {
    plugins: [vue()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        '/api': {
          target: djangoProxyTarget,
          changeOrigin: false,
        },
        '/api-auth': {
          target: djangoProxyTarget,
          changeOrigin: false,
        },
        '/admin': {
          target: djangoProxyTarget,
          changeOrigin: false,
        },
        '/ai': {
          target: aiProxyTarget,
          changeOrigin: false,
        },
      },
    },
  }
})

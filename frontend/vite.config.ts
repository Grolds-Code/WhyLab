import { Agent } from 'node:https'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const modalAgent = new Agent({
  keepAlive: true,
  family: 4,
})

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'https://groldotieno97--whylab-mcp-mcp-app.modal.run',
        changeOrigin: true,
        agent: modalAgent,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})

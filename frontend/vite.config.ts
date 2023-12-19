import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: [
      { find: '@IuComponentLib/', replacement:  '/src/IuComponentLib/' },
      { find: '@components/', replacement:  '/src/components/' },
    ],
  },
})

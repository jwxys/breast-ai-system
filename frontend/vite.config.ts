import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: [
      'monkeycode-ai.online',
      '*.monkeycode-ai.online',
      '127.0.0.1',
      'localhost'
    ],
  },
  preview: {
    host: '0.0.0.0',
    port: 3001,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          antd: ['antd', 'dayjs'],
          charts: ['echarts', 'echarts-for-react'],
        },
      },
    },
  },
});

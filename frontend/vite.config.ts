import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: '/', // Use relative paths for production
  server: {
    host: true, // crucial for Docker: allows binding to 0.0.0.0
    port: 5173, // explicit port helps with Docker/Compose
    strictPort: true, // avoid port fallback (important if exposing specific port)
    allowedHosts: [
      'localhost',
      '5ed1-2600-4808-5931-a900-a48a-5409-62bc-5c0b.ngrok-free.app'
    ],
    headers: {
      'ngrok-skip-browser-warning': 'true'
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // Ensure relative paths for production
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name].[hash].[ext]',
        chunkFileNames: 'assets/[name].[hash].js',
        entryFileNames: 'assets/[name].[hash].js'
      }
    }
  }
});

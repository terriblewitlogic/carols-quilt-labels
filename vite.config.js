import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5199,
    proxy: {
      // In dev, route Netlify function calls to local Python server on 9999
      '/.netlify/functions': {
        target: 'http://localhost:9999',
        rewrite: path => path.replace('/.netlify/functions', ''),
      },
    },
  },
});

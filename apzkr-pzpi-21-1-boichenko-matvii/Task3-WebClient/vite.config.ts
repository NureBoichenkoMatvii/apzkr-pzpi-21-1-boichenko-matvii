import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from "node:path";

// https://vitejs.dev/config/
export default defineConfig(({command, mode}) => {
  const env = {
    ...process.env,
    ...loadEnv(process.env.REACT_APP_ENV || 'development', process.cwd(), '')
  };
  console.log(command, mode, process.env.REACT_APP_ENV);
  env.ENVIRONMENT = mode;
  env.API_URL = mode === 'production' ? 'https://matvi-nure-fastapi.azurewebsites.net' : 'http://localhost:8000';

  return {
    define: {
      'process.env': env,
    },
    plugins: [react()],
    server: {
      port: 3001
    },
    resolve: {
      alias: {
        '@pages': path.resolve(__dirname, 'src/pages'),
        '@styles': path.resolve(__dirname, 'src/styles'),
        '@stores': path.resolve(__dirname, 'src/services/stores'),
        '@utils': path.resolve(__dirname, 'src/utils'),
        '@shared': path.resolve(__dirname, 'src/shared'),
        '@hooks': path.resolve(__dirname, 'src/hooks'),
        '@api': path.resolve(__dirname, 'src/api'),
        '@components': path.resolve(__dirname, 'src/components'),
      },
    },
    build: {
      outDir: 'dist'
    }
  }
})

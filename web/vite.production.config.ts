import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';
export default defineConfig({ plugins:[react(),tailwindcss()], resolve:{alias:{'@':path.resolve(__dirname,'src')}}, build:{rollupOptions:{input:path.resolve(__dirname,'index.production.html')},sourcemap:true}, server:{host:'127.0.0.1',port:5173} });

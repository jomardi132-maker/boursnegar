import { copyFileSync } from 'node:fs';
import { build as viteBuild } from 'vite';
import { build as esbuildBuild } from 'esbuild';

await viteBuild({ configFile: 'vite.production.config.ts' });
copyFileSync('dist/index.production.html', 'dist/index.html');
await esbuildBuild({
  entryPoints: ['server.production.ts'],
  bundle: true,
  platform: 'node',
  format: 'cjs',
  packages: 'external',
  sourcemap: true,
  outfile: 'dist/server.cjs',
});
await esbuildBuild({
  entryPoints: ['server/alertWorker.ts'],
  bundle: true,
  platform: 'node',
  format: 'cjs',
  packages: 'external',
  sourcemap: true,
  outfile: 'dist/alert-worker.cjs',
});

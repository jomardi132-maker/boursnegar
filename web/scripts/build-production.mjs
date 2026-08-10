import { execFileSync } from 'node:child_process';
import { copyFileSync } from 'node:fs';
const bin = process.platform === 'win32' ? 'npx.cmd' : 'npx';
execFileSync(bin, ['vite','build','--config','vite.production.config.ts'], { stdio: 'inherit' });
copyFileSync('dist/index.production.html', 'dist/index.html');
execFileSync(bin, ['esbuild','server.production.ts','--bundle','--platform=node','--format=cjs','--packages=external','--sourcemap','--outfile=dist/server.cjs'], { stdio: 'inherit' });

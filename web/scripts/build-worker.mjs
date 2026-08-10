import{build}from'esbuild';await build({entryPoints:['server/alertWorker.ts'],bundle:true,platform:'node',format:'cjs',packages:'external',sourcemap:true,outfile:'dist/alert-worker.cjs'});

import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import { pool } from '../server/postgres';
dotenv.config();
async function main() {
  await pool.query(`CREATE TABLE IF NOT EXISTS schema_migrations(version text PRIMARY KEY,applied_at timestamptz NOT NULL DEFAULT now())`);
  for (const file of fs.readdirSync(path.resolve('migrations')).filter((f) => /^\d+.*\.sql$/.test(f)).sort()) {
    const version = file.replace(/\.sql$/, '');
    if ((await pool.query(`SELECT 1 FROM schema_migrations WHERE version=$1`, [version])).rowCount) continue;
    await pool.query(fs.readFileSync(path.join('migrations', file), 'utf8'));
    console.log(`applied ${version}`);
  }
  await pool.end();
}
main().catch((error) => { console.error(error instanceof Error ? error.message : error); process.exit(1); });

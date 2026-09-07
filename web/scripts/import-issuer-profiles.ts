import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import dotenv from "dotenv";
import pg from "pg";

dotenv.config({ quiet: true });

type EvidenceFile = { path: string; sha256: string };
type Profile = {
  symbol: string;
  legal_name: string;
  official_website_url: string | null;
  logo_url: string | null;
  source_type: string;
  source_reference: string;
  evidence_files: EvidenceFile[];
  evidence_checksum: string;
  status: string;
};

function sha256(file: string): string {
  const hash = crypto.createHash("sha256");
  hash.update(fs.readFileSync(file));
  return hash.digest("hex");
}

function validateProfile(profile: Profile, root: string): void {
  if (!profile.symbol || !profile.legal_name || profile.status !== "VERIFIED") throw new Error(`invalid verified profile: ${profile.symbol}`);
  for (const url of [profile.official_website_url, profile.logo_url, profile.source_reference]) {
    if (url && !/^https:\/\//.test(url)) throw new Error(`non-HTTPS profile URL: ${profile.symbol}`);
  }
  if (!profile.evidence_files.length || !/^[a-f0-9]{64}$/.test(profile.evidence_checksum)) throw new Error(`missing evidence checksum: ${profile.symbol}`);
  const checksums = profile.evidence_files.map((item) => {
    const file = path.resolve(root, item.path);
    if (!fs.existsSync(file) || sha256(file) !== item.sha256) throw new Error(`evidence checksum mismatch: ${item.path}`);
    return item.sha256;
  });
  if (!checksums.includes(profile.evidence_checksum)) throw new Error(`profile checksum is not an evidence checksum: ${profile.symbol}`);
}

async function main() {
  const manifestArg = process.argv[2];
  const apply = process.argv.includes("--apply");
  if (!manifestArg || manifestArg === "--help") {
    console.log("Usage: tsx scripts/import-issuer-profiles.ts MANIFEST.json [--apply]");
    return;
  }
  const manifestPath = path.resolve(manifestArg);
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8")) as { schema: string; items: Profile[] };
  if (manifest.schema !== "boursnegar-issuer-profile-v1" || !Array.isArray(manifest.items) || !manifest.items.length) throw new Error("manifest schema validation failed");
  const root = path.dirname(manifestPath);
  const symbols = new Set<string>();
  for (const profile of manifest.items) {
    if (symbols.has(profile.symbol)) throw new Error(`duplicate profile: ${profile.symbol}`);
    symbols.add(profile.symbol);
    validateProfile(profile, root);
  }
  if (!apply) {
    console.log(JSON.stringify({ mode: "dry-run", profiles: manifest.items.length, symbols: [...symbols] }, null, 2));
    return;
  }
  const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL, host: process.env.DB_HOST, port: Number(process.env.DB_PORT || 5432), database: process.env.DB_NAME, user: process.env.DB_USER, password: process.env.DB_PASSWORD });
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const locked = await client.query("SELECT pg_try_advisory_xact_lock(hashtextextended($1,0)) AS locked", ["boursnegar:issuer-profile-import"]);
    if (!locked.rows[0]?.locked) throw new Error("advisory lock is held");
    for (const profile of manifest.items) {
      const row = await client.query(`SELECT DISTINCT i.issuer_id,ir.legal_name
        FROM symbol_aliases sa JOIN instruments i ON i.id=sa.instrument_id
        JOIN issuers ir ON ir.id=i.issuer_id
        WHERE sa.symbol=$1 AND sa.valid_to IS NULL AND i.active`, [profile.symbol]);
      if (row.rowCount !== 1 || !profile.legal_name.includes(String(row.rows[0].legal_name))) throw new Error(`symbol/legal-name mismatch: ${profile.symbol}`);
      await client.query(`INSERT INTO issuer_profiles(issuer_id,official_website_url,logo_url,source_type,source_reference,evidence_checksum,status,verified_at,updated_at)
        VALUES($1,$2,$3,$4,$5,$6,'VERIFIED',now(),now())
        ON CONFLICT(issuer_id) DO UPDATE SET official_website_url=excluded.official_website_url,logo_url=excluded.logo_url,source_type=excluded.source_type,source_reference=excluded.source_reference,evidence_checksum=excluded.evidence_checksum,status='VERIFIED',verified_at=excluded.verified_at,updated_at=now()`,
      [row.rows[0].issuer_id, profile.official_website_url, profile.logo_url, profile.source_type, profile.source_reference, profile.evidence_checksum]);
    }
    await client.query("COMMIT");
    console.log(JSON.stringify({ mode: "apply", profiles: manifest.items.length, symbols: [...symbols] }));
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

main().catch((error) => { console.error(error instanceof Error ? error.message : error); process.exit(1); });

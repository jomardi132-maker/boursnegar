#!/usr/bin/env python3
"""Promote one validated normalized evidence directory through the safe gates."""
from __future__ import annotations

import argparse, hashlib, json, shlex, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def run(cmd: list[str], timeout: int = 1800) -> str:
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(cmd)}\n{p.stderr[-2000:]}")
    return p.stdout

def remote_as_root(command: str) -> str:
    """Run a remote command without sudo prompts when SSH already is root."""
    return f"if [ \"$(id -u)\" -eq 0 ]; then {command}; else sudo -n {command}; fi"

def validate_normalized_units(data: Path) -> None:
    """Reject NAV whose unit is not the per-unit IRR contract."""
    invalid = []
    for line_no, line in enumerate(data.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("fact_key") == "nav_per_share" and row.get("unit") != "IRR":
            invalid.append((line_no, row.get("unit")))
    if invalid:
        raise SystemExit(f"refusing: NAV unit gate failed ({invalid[:5]})")

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--normalized-dir", required=True)
    p.add_argument("--ssh-target", default="boursnegar")
    p.add_argument("--remote-dir", required=True)
    p.add_argument("--report", required=True)
    a = p.parse_args()
    src = Path(a.normalized_dir).resolve(); manifest = json.loads((src / "manifest.json").read_text(encoding="utf-8"))
    files = manifest.get("files", [])
    if manifest.get("source") != "browser/codal.ir" or len(files) != 1:
        raise SystemExit("refusing: manifest is not a single official browser evidence set")
    data = src / files[0]["path"]
    if not data.exists() or hashlib.sha256(data.read_bytes()).hexdigest() != files[0]["sha256"]:
        raise SystemExit("refusing: manifest checksum mismatch")
    validate_normalized_units(data)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = f"/var/backups/boursnegar/{stamp}-evidence-before.dump"
    run(["ssh", a.ssh_target, "bash", "-lc",
         shlex.quote(remote_as_root(f"install -d -m 700 $(dirname {backup}) && runuser -u postgres -- pg_dump -Fc -d boursnegar_db > {backup}"))], 1800)
    run(["ssh", a.ssh_target, "bash", "-lc", shlex.quote(remote_as_root(f"install -d -m 0750 {a.remote_dir}"))])
    remote_name = files[0]["path"]
    run(["scp", str(data), f"{a.ssh_target}:/tmp/{remote_name}"])
    run(["scp", str(src / "manifest.json"), f"{a.ssh_target}:/tmp/evidence-manifest.json"])
    run(["ssh", a.ssh_target, "bash", "-lc", shlex.quote(remote_as_root(f"mv /tmp/{remote_name} {a.remote_dir}/{remote_name}"))])
    run(["ssh", a.ssh_target, "bash", "-lc", shlex.quote(remote_as_root(f"mv /tmp/evidence-manifest.json {a.remote_dir}/manifest.json"))])
    remote_manifest = f"{a.remote_dir}/manifest.json"
    # Omit --symbol: '*' selects the notice-only branch in the standard importer.
    import_cmd = shlex.quote(remote_as_root(f"cd /var/www/boursnegar-data-current && env PYTHONPATH=. /var/www/boursnegar-runtimes/data-venv/bin/python3 scripts/codalpy_remote_import.py --manifest {remote_manifest} --batch-size 500"))
    first = run(["ssh", a.ssh_target, "bash", "-lc", import_cmd])
    second = run(["ssh", a.ssh_target, "bash", "-lc", import_cmd])
    if '"inserted": 0' not in second:
        raise SystemExit("idempotency gate failed")
    refresh = run(["ssh", a.ssh_target, "bash", "-lc", shlex.quote(remote_as_root("systemctl start --wait boursnegar-snapshot-refresh.service"))])
    ready = run(["ssh", a.ssh_target, "curl", "-fsS", "http://127.0.0.1:8001/readyz"])
    report = {"schema":"boursnegar-evidence-promotion-v1", "source":str(src), "backup":backup,
              "manifest":manifest, "first_import":first, "idempotent_replay":second,
              "refresh":refresh, "ready":ready, "status":"success"}
    out=Path(a.report); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"status":"success","report":str(out),"backup":backup},ensure_ascii=False)); return 0

if __name__ == "__main__": raise SystemExit(main())

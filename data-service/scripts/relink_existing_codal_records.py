#!/usr/bin/env python3
"""Idempotently replay existing artifacts so raw Codal rows regain symbol lineage."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", default="/var/lib/boursnegar/codalpy/daily")
    parser.add_argument("--checkpoint", default="/var/lib/boursnegar/codalpy/monthly-lineage-checkpoint.json")
    args = parser.parse_args()
    root = Path(args.artifact_root)
    checkpoint_path = Path(args.checkpoint)
    state = json.loads(checkpoint_path.read_text()) if checkpoint_path.exists() else {"completed": []}
    completed = set(state.get("completed", []))
    manifests = sorted(root.glob("**/manifest.json"))
    importer = Path(__file__).with_name("codalpy_remote_import.py")
    for manifest in manifests:
        key = str(manifest)
        if key in completed:
            continue
        try:
            metadata = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if metadata.get("schema") != "boursnegar-codalpy-jsonl-v1":
            continue
        if not metadata.get("files"):
            completed.add(key)
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            checkpoint_path.write_text(json.dumps({"completed": sorted(completed)}, ensure_ascii=False, indent=2))
            continue
        result = subprocess.run(
            [sys.executable, str(importer), "--manifest", key, "--symbol", "*", "--batch-size", "500"],
            text=True, capture_output=True, cwd=importer.parent.parent,
            env={**os.environ, "PYTHONPATH": str(importer.parent.parent)},
        )
        print(json.dumps({"manifest": key, "returncode": result.returncode,
                          "output": result.stdout[-1000:], "error": result.stderr[-1000:]}, ensure_ascii=False), flush=True)
        if result.returncode != 0:
            continue
        completed.add(key)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_path.write_text(json.dumps({"completed": sorted(completed)}, ensure_ascii=False, indent=2))
    print(json.dumps({"manifests": len(manifests), "completed": len(completed)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

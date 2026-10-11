"""Build the frontend against the live API and publish it to Amplify Hosting via a manual zip deployment.

Usage:  python scripts/deploy_frontend.py
Reads API url + Amplify app id from `terraform output` in ./infra.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import time
import zipfile

import boto3
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INFRA = os.path.join(ROOT, "infra")
FRONT = os.path.join(ROOT, "frontend")
DIST = os.path.join(FRONT, "dist")


def tf_outputs() -> dict:
    out = subprocess.check_output(["terraform", "output", "-json"], cwd=INFRA, text=True)
    return {k: v["value"] for k, v in json.loads(out).items()}


def build(api_url: str) -> None:
    env = dict(os.environ, VITE_API_URL=api_url)
    npm = "npm.cmd" if os.name == "nt" else "npm"
    subprocess.check_call([npm, "run", "build"], cwd=FRONT, env=env)


def zip_dist() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(DIST):
            for f in files:
                full = os.path.join(dirpath, f)
                z.write(full, os.path.relpath(full, DIST).replace(os.sep, "/"))
    return buf.getvalue()


def main() -> int:
    o = tf_outputs()
    api_url, app_id, region = o["api_url"], o["amplify_app_id"], o["region"]
    print(f"API: {api_url}\nAmplify app: {app_id} ({region})")
    build(api_url)
    payload = zip_dist()
    print(f"bundle: {len(payload)//1024} KB")

    amp = boto3.client("amplify", region_name=region)
    dep = amp.create_deployment(appId=app_id, branchName="main")
    req = urllib.request.Request(dep["zipUploadUrl"], data=payload, method="PUT", headers={"Content-Type": "application/zip"})
    with urllib.request.urlopen(req) as r:
        assert r.status in (200, 201), r.status
    amp.start_deployment(appId=app_id, branchName="main", jobId=dep["jobId"])
    print(f"deployment {dep['jobId']} started")
    for _ in range(60):
        job = amp.get_job(appId=app_id, branchName="main", jobId=dep["jobId"])["job"]["summary"]
        status = job["status"]
        if status in ("SUCCEED", "FAILED", "CANCELLED"):
            print("status:", status)
            break
        time.sleep(3)
    print("URL:", o["amplify_url"])
    return 0 if status == "SUCCEED" else 1


if __name__ == "__main__":
    sys.exit(main())

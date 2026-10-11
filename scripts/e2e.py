"""End-to-end test: push a specimen bill through the live API exactly like the browser does.

Usage:  python scripts/e2e.py [samples/bill_bses_delhi.jpg] [--save]
--save writes the response to frontend/src/demo/captured.json for the offline fallback.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Hindi output on a Windows console


def api_url() -> str:
    out = subprocess.check_output(["terraform", "output", "-raw", "api_url"], cwd=os.path.join(ROOT, "infra"), text=True)
    return out.strip()


def call(url: str, method: str = "GET", body: dict | None = None, data: bytes | None = None, ctype: str = "application/json") -> dict | bytes:
    payload = data if data is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(url, data=payload, method=method, headers={"content-type": ctype})
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
        return json.loads(raw) if r.headers.get("content-type", "").startswith("application/json") else raw


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    save = "--save" in sys.argv
    path = args[0] if args else os.path.join(ROOT, "samples", "bill_bses_delhi.jpg")
    base = api_url()
    print("API:", base)
    print("health:", json.dumps(call(f"{base}/health"), indent=None)[:300])

    img = open(path, "rb").read()
    t = time.time()
    ps = call(f"{base}/presign", "POST", {"contentType": "image/jpeg"})
    call(ps["url"], "PUT", data=img, ctype="image/jpeg")
    print(f"uploaded {len(img)//1024} KB -> {ps['key']} in {int((time.time()-t)*1000)} ms")

    t = time.time()
    res = call(f"{base}/analyze", "POST", {"key": ps["key"]})
    print(f"analyze: {int((time.time()-t)*1000)} ms total")
    for s in res["pipeline"]:
        print(f"  {s['service']:<20} {s['ms']:>6} ms  {'OK ' if s['ok'] else 'DEG'}  {s.get('model','')} {s['detail']}")
    x, e = res["extraction"], res["estimate"]
    print(f"  extraction[{x['source']}]: {x.get('discom')} | {x['units_consumed']} units | load {x.get('sanctioned_load_kw')} kW | Rs {x.get('bill_amount_rs')} | conf {x.get('confidence')}")
    print(f"  field boxes: {list(res['field_boxes'].keys())}")
    print(f"  estimate: {e['recommended_kw']} kW, {e['panel_count']} panels, subsidy Rs {e['subsidy_rs']:,}, net Rs {e['net_cost_rs']:,}, saves Rs {e['monthly_savings_rs']:,}/mo, payback {e['payback_years']} y")

    t = time.time()
    pr = call(f"{base}/proposal", "POST", {"id": res["id"]})["proposal"]
    print(f"proposal[{pr['source']}] {pr.get('model','')} {int((time.time()-t)*1000)} ms")
    print("  EN:", pr["english"][:160].replace("\n", " "), "...")
    print("  HI:", pr["hindi"][:120].replace("\n", " "), "...")

    got = call(f"{base}/estimates/{res['id']}")
    print("get estimate:", "ok" if got.get("id") == res["id"] else "MISMATCH")

    if save:
        out = os.path.join(ROOT, "frontend", "src", "demo", "captured.json")
        res["proposal"] = pr
        with open(out, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print("saved", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

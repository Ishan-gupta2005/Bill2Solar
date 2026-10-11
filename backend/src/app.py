"""Bill2Solar API: one Lambda, routed on path.

POST /presign           -> presigned S3 PUT url for the bill photo
POST /analyze           -> Rekognition text + Bedrock extraction + solar estimate, saved to DynamoDB
POST /proposal          -> Bedrock writes a Hindi + English proposal for a saved estimate
GET  /estimates/{id}    -> fetch a saved estimate
GET  /health            -> liveness + config echo
"""
from __future__ import annotations

import base64
import json
import logging
import os
import re
import time
import uuid
from decimal import Decimal
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from discoms import detect_discom, find_discom
from solar import estimate as solar_estimate, to_dict as estimate_to_dict

log = logging.getLogger()
log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

REGION = os.environ.get("AWS_REGION", "ap-southeast-2")
# New free-plan accounts get Bedrock inference unlocked region by region ("Operation not allowed"
# elsewhere). We try a list in order and remember the first region that answers for this container.
BEDROCK_REGIONS = [r.strip() for r in os.environ.get("BEDROCK_REGIONS", os.environ.get("BEDROCK_REGION", REGION)).split(",") if r.strip()]
BUCKET = os.environ["UPLOAD_BUCKET"]
TABLE = os.environ["ESTIMATES_TABLE"]
VISION_MODEL = os.environ.get("BEDROCK_VISION_MODEL", "amazon.nova-lite-v1:0")
TEXT_MODEL = os.environ.get("BEDROCK_TEXT_MODEL", "au.anthropic.claude-haiku-4-5-20251001-v1:0")
FALLBACKS = [m for m in os.environ.get("BEDROCK_FALLBACKS", "").split(",") if m]

_cfg = Config(retries={"max_attempts": 2, "mode": "standard"}, read_timeout=25, connect_timeout=5)
# Pin S3 to the regional endpoint: presigned URLs on the global endpoint get a 307 from
# non-us-east-1 buckets, and browsers will not replay a PUT body across that redirect.
_s3_cfg = Config(signature_version="s3v4", s3={"addressing_style": "virtual"},
                 retries={"max_attempts": 2, "mode": "standard"}, read_timeout=25, connect_timeout=5)
s3 = boto3.client("s3", region_name=REGION, endpoint_url=f"https://s3.{REGION}.amazonaws.com", config=_s3_cfg)
rek = boto3.client("rekognition", region_name=REGION, config=_cfg)
table = boto3.resource("dynamodb", region_name=REGION).Table(TABLE)

_brt_clients: dict[str, Any] = {}
_bedrock_region_ok: str | None = None


def _brt(region: str):
    if region not in _brt_clients:
        _brt_clients[region] = boto3.client("bedrock-runtime", region_name=region, config=_cfg)
    return _brt_clients[region]


def _bedrock_regions() -> list[str]:
    if _bedrock_region_ok and _bedrock_region_ok in BEDROCK_REGIONS:
        return [_bedrock_region_ok] + [r for r in BEDROCK_REGIONS if r != _bedrock_region_ok]
    return list(BEDROCK_REGIONS)


BEDROCK_BUDGET_MS = int(os.environ.get("BEDROCK_BUDGET_MS", "4500"))


def _is_region_blocked(e: Exception) -> bool:
    msg = str(getattr(e, "response", {}).get("Error", {}).get("Message", "")) if hasattr(e, "response") else str(e)
    return "Operation not allowed" in msg or "being verified" in msg


def bedrock_converse(models: list[str], content: list[dict], max_tokens: int, temperature: float) -> tuple[str | None, str | None, str | None, str | None]:
    """Try (region, model) pairs in order within a time budget. Returns (text, model, region, last_error)."""
    global _bedrock_region_ok
    last_err = None
    started = time.time()
    for region in _bedrock_regions():
        if (time.time() - started) * 1000 > BEDROCK_BUDGET_MS:
            last_err = f"budget {BEDROCK_BUDGET_MS} ms exhausted; last: {last_err}"
            break
        for model in models:
            try:
                resp = _brt(region).converse(
                    modelId=model,
                    messages=[{"role": "user", "content": content}],
                    inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
                )
                _bedrock_region_ok = region
                return "".join(c.get("text", "") for c in resp["output"]["message"]["content"]), model, region, None
            except ClientError as e:
                code = e.response.get("Error", {}).get("Code", "ClientError")
                last_err = f"{region}/{model}: {code}"
                log.warning("bedrock %s %s failed: %s", region, model, e)
                if _is_region_blocked(e):
                    break  # whole region is closed for this account; try the next region
                continue  # this model only; try the next model in the same region
            except Exception as e:  # noqa: BLE001
                last_err = f"{region}/{model}: {type(e).__name__}"
                log.warning("bedrock %s %s failed: %s", region, model, e)
                continue
    return None, None, None, last_err

SEVEN_DAYS = 7 * 24 * 3600


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
def _json_default(o: Any):
    if isinstance(o, Decimal):
        return float(o) if o % 1 else int(o)
    return str(o)


def respond(status: int, body: Any) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "content-type": "application/json",
            "access-control-allow-origin": "*",
            "access-control-allow-headers": "content-type",
            "access-control-allow-methods": "GET,POST,OPTIONS",
        },
        "body": json.dumps(body, default=_json_default),
    }


def parse_body(event: dict) -> dict:
    raw = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def to_ddb(obj: Any) -> Any:
    """DynamoDB refuses floats; round-trip through JSON to Decimal."""
    return json.loads(json.dumps(obj, default=_json_default), parse_float=Decimal)


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------
def handler(event: dict, context) -> dict:
    http = event.get("requestContext", {}).get("http", {})
    method = http.get("method", "GET")
    path = event.get("rawPath", "/")
    log.info("route %s %s", method, path)

    try:
        if method == "OPTIONS":
            return respond(204, {})
        if path == "/health":
            return respond(200, {
                "ok": True, "region": REGION, "bedrock_regions": BEDROCK_REGIONS, "bedrock_region_ok": _bedrock_region_ok,
                "bucket": BUCKET, "table": TABLE,
                "vision_model": VISION_MODEL, "text_model": TEXT_MODEL, "fallbacks": FALLBACKS,
            })
        if path == "/presign" and method == "POST":
            return presign(parse_body(event))
        if path == "/analyze" and method == "POST":
            return analyze(parse_body(event))
        if path == "/proposal" and method == "POST":
            return proposal(parse_body(event))
        if path.startswith("/estimates/") and method == "GET":
            return get_estimate(path.rsplit("/", 1)[-1])
        return respond(404, {"error": "not found", "path": path})
    except ClientError as e:
        log.exception("aws error")
        return respond(502, {"error": "aws", "code": e.response.get("Error", {}).get("Code"),
                             "message": e.response.get("Error", {}).get("Message")})
    except Exception as e:  # noqa: BLE001
        log.exception("unhandled")
        return respond(500, {"error": "internal", "message": str(e)})


def presign(body: dict) -> dict:
    content_type = body.get("contentType") or "image/jpeg"
    ext = {"image/png": "png", "image/webp": "webp"}.get(content_type, "jpg")
    key = f"bills/{time.strftime('%Y%m%d')}/{uuid.uuid4().hex}.{ext}"
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": BUCKET, "Key": key, "ContentType": content_type},
        ExpiresIn=600,
    )
    return respond(200, {"key": key, "url": url, "bucket": BUCKET, "region": REGION})


def get_estimate(est_id: str) -> dict:
    item = table.get_item(Key={"id": est_id}).get("Item")
    if not item:
        return respond(404, {"error": "not found"})
    return respond(200, item)


# ---------------------------------------------------------------------------
# The pipeline
# ---------------------------------------------------------------------------
def analyze(body: dict) -> dict:
    key = body.get("key")
    if not key:
        return respond(400, {"error": "key required"})
    roof_sqft = _num(body.get("roofSqft"))
    pipeline: list[dict] = []
    est_id = uuid.uuid4().hex[:12]

    # 1. S3: fetch bytes (needed for Bedrock vision)
    t = time.time()
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    img = obj["Body"].read()
    pipeline.append({"step": "s3", "service": "Amazon S3", "detail": f"{len(img)//1024} KB fetched",
                     "ms": _ms(t), "ok": True})

    # 2. Rekognition: every line of text with its bounding box
    t = time.time()
    lines = rekognition_lines(key)
    pipeline.append({"step": "rekognition", "service": "Amazon Rekognition", "api": "DetectText",
                     "detail": f"{len(lines)} text lines", "ms": _ms(t), "ok": True})

    ocr_text = "\n".join(l["text"] for l in lines)

    # 3. Bedrock: structured extraction (vision + OCR hints), with graceful degradation
    t = time.time()
    extraction, model_used, region_used, bedrock_err = bedrock_extract(img, ocr_text)
    if extraction is None:
        extraction = heuristic_extract(ocr_text)
        pipeline.append({"step": "bedrock", "service": "Amazon Bedrock", "api": "Converse",
                         "detail": f"unavailable ({bedrock_err}); used heuristic parser",
                         "ms": _ms(t), "ok": False, "fallback": "heuristic"})
    else:
        extraction["source"] = "bedrock"
        pipeline.append({"step": "bedrock", "service": "Amazon Bedrock", "api": "Converse",
                         "model": model_used, "region": region_used, "detail": f"structured JSON extracted · {region_used}",
                         "ms": _ms(t), "ok": True})

    extraction = normalise_extraction(extraction, ocr_text)
    field_boxes = locate_fields(extraction, lines)

    # 4. Solar economics
    est = solar_estimate(
        monthly_units=extraction["units_consumed"],
        bill_amount_rs=extraction.get("bill_amount_rs"),
        sanctioned_load_kw=extraction.get("sanctioned_load_kw"),
        roof_sqft=roof_sqft,
        tariff_hint_rs_per_unit=None if extraction.get("bill_amount_rs") else extraction.get("tariff_hint"),
    )

    # 5. DynamoDB
    t = time.time()
    now = int(time.time())
    item = {
        "id": est_id,
        "created_at": now,
        "expires_at": now + SEVEN_DAYS,
        "key": key,
        "extraction": extraction,
        "estimate": estimate_to_dict(est),
        "field_boxes": field_boxes,
        "ocr": {"lines": lines[:200]},
        "pipeline": pipeline,
    }
    table.put_item(Item=to_ddb(item))
    pipeline.append({"step": "dynamodb", "service": "Amazon DynamoDB", "api": "PutItem",
                     "detail": f"estimate {est_id} saved", "ms": _ms(t), "ok": True})
    item["pipeline"] = pipeline
    return respond(200, item)


def rekognition_lines(key: str) -> list[dict]:
    resp = rek.detect_text(Image={"S3Object": {"Bucket": BUCKET, "Name": key}})
    out = []
    for d in resp.get("TextDetections", []):
        if d.get("Type") != "LINE":
            continue
        bb = d["Geometry"]["BoundingBox"]
        out.append({
            "id": d["Id"],
            "text": d["DetectedText"],
            "confidence": round(d["Confidence"], 1),
            "box": {k.lower(): round(v, 4) for k, v in bb.items()},
        })
    out.sort(key=lambda l: (round(l["box"]["top"], 2), l["box"]["left"]))
    return out


EXTRACT_PROMPT = """You are reading a photo of an Indian residential electricity bill.
Return ONLY a JSON object, no prose, no code fences, with these keys:
{
  "discom": "name of the electricity distribution company as printed, e.g. BSES Rajdhani, Tata Power-DDL, MSEDCL, BESCOM, UPPCL",
  "state": "Indian state",
  "city": "city if visible else null",
  "billing_period": "month/period as printed, else null",
  "units_consumed": number of kWh units billed this month (integer, required; if a bi-monthly bill, halve it),
  "sanctioned_load_kw": number or null,
  "bill_amount_rs": total amount payable in rupees as a number, or null,
  "tariff_category": "e.g. Domestic / LT-1 / Residential, else null",
  "meter_type": "e.g. single phase / three phase, else null",
  "confidence": number between 0 and 1 for the units_consumed value
}
Do not include the consumer's name, address, phone, or account number.
Below is OCR text already read from the same image, use it to cross-check digits:
---
"""


def bedrock_extract(img: bytes, ocr_text: str) -> tuple[dict | None, str | None, str | None, str | None]:
    fmt = _image_format(img)
    models = [VISION_MODEL] + [m for m in FALLBACKS if m != VISION_MODEL and "micro" not in m]
    content = [
        {"image": {"format": fmt, "source": {"bytes": img}}},
        {"text": EXTRACT_PROMPT + ocr_text[:6000]},
    ]
    text, model, region, err = bedrock_converse(models, content, max_tokens=600, temperature=0.0)
    if text is None:
        return None, None, None, err
    data = _parse_json(text)
    if data and data.get("units_consumed") is not None:
        return data, model, region, None
    return None, model, region, f"{region}/{model}: unparseable response"


def heuristic_extract(ocr_text: str) -> dict:
    """Regex-only fallback so the demo never dies if Bedrock is unavailable."""
    t = ocr_text.replace(",", "")
    low = t.lower()

    def grab(patterns: list[str]) -> float | None:
        for p in patterns:
            m = re.search(p, low, flags=re.I | re.S)
            if m:
                try:
                    return float(m.group(1))
                except ValueError:
                    continue
        return None

    # Priority order matters: "consumption details" followed by a date once parsed as 1 unit.
    not_date = r"(?![\d\-/])"
    units = grab([
        r"units?\s*consumed\D{0,25}?(\d{2,5})" + not_date,
        r"(?<![\d,.])(\d{2,5})\s*(?:kwh|units)\b",
        r"(?:total\s*units|units\s*billed|billed\s*units|energy\s*consumed|net\s*units)\D{0,25}?(\d{2,5})" + not_date,
        r"consumption\s*\(?\s*(?:kwh|units)?\s*\)?\s*[:\-]?\s*(\d{2,5})" + not_date,
    ])
    if units is not None and units < 20:
        units = None
    load = grab([
        r"(?:sanctioned|contract|connected)\s*load\D{0,20}?(\d{1,2}(?:\.\d+)?)",
        r"(\d{1,2}(?:\.\d+)?)\s*kw\b",
    ])
    amount = grab([
        r"(?:total\s*amount\s*payable|amount\s*payable|net\s*payable|net\s*amount|total\s*payable|bill\s*amount|current\s*bill|amount\s*due|payable)\D{0,30}?(\d{3,7}(?:\.\d{1,2})?)",
        r"(?:rs\.?|₹|inr)\s*(\d{3,7}(?:\.\d{1,2})?)",
    ])
    d = detect_discom(low)
    out = {
        "discom": d["name"] if d else None,
        "state": d["state"] if d else None,
        "city": d["city"] if d else None,
        "billing_period": None,
        "units_consumed": units,
        "sanctioned_load_kw": load,
        "bill_amount_rs": amount,
        "tariff_category": None,
        "meter_type": None,
        "confidence": 0.5 if units else 0.0,
        "source": "heuristic" if units else "fallback",
    }
    if units is None:
        # Last resort: a representative Delhi household so the UI still renders.
        out.update({"units_consumed": 312, "bill_amount_rs": 2180, "sanctioned_load_kw": 3,
                    "discom": out["discom"] or "BSES Rajdhani Power Ltd", "state": out["state"] or "Delhi",
                    "city": out["city"] or "Delhi", "note": "Could not read units from the image; showing a representative estimate."})
    return out


def normalise_extraction(x: dict, ocr_text: str) -> dict:
    x = dict(x)
    x["units_consumed"] = _num(x.get("units_consumed")) or 0
    x["sanctioned_load_kw"] = _num(x.get("sanctioned_load_kw"))
    x["bill_amount_rs"] = _num(x.get("bill_amount_rs"))
    x["confidence"] = _num(x.get("confidence")) or 0
    d = find_discom(x.get("discom")) or detect_discom(ocr_text)
    if d:
        x["discom_code"] = d["code"]
        x["discom"] = x.get("discom") or d["name"]
        x["state"] = x.get("state") or d["state"]
        x["city"] = x.get("city") or d["city"]
        x["tariff_hint"] = d["tariff"]
        x["discom_portal"] = d["portal"]
    if x["units_consumed"] <= 0:
        x["units_consumed"] = 312
        x["note"] = "Units not readable; representative estimate shown."
        x["source"] = "fallback"
    x.setdefault("source", "bedrock")
    return x


def locate_fields(x: dict, lines: list[dict]) -> dict:
    """Map extracted values back to the OCR line that contains them, for the UI glow."""
    boxes: dict[str, dict] = {}

    def find_line(pred) -> dict | None:
        for l in lines:
            if pred(l["text"]):
                return l["box"]
        return None

    def digits(v) -> str:
        return re.sub(r"[^\d]", "", str(int(v))) if v is not None else ""

    u = digits(x.get("units_consumed"))
    if u:
        boxes["units"] = find_line(lambda s: u in s.replace(",", "") and re.search(r"unit|kwh|consum", s, re.I)) \
            or find_line(lambda s: re.search(rf"\b{u}\b", s.replace(",", "")) is not None)
    a = x.get("bill_amount_rs")
    if a:
        ad = digits(a)
        boxes["amount"] = find_line(lambda s: ad in s.replace(",", "").replace(".00", "") and re.search(r"amount|payable|total|₹|rs", s, re.I)) \
            or find_line(lambda s: ad in s.replace(",", "").replace(".00", ""))
    lk = x.get("sanctioned_load_kw")
    if lk:
        boxes["load"] = find_line(lambda s: re.search(r"load", s, re.I) is not None and re.search(rf"{lk:g}", s) is not None) \
            or find_line(lambda s: re.search(r"sanctioned|load", s, re.I) is not None)
    if x.get("discom"):
        d = find_discom(x.get("discom"))
        kws = d["keywords"] if d else [str(x["discom"]).lower()[:10]]
        boxes["discom"] = find_line(lambda s: any(k in s.lower() for k in kws))
    return {k: v for k, v in boxes.items() if v}


# ---------------------------------------------------------------------------
# Proposal generation
# ---------------------------------------------------------------------------
PROPOSAL_PROMPT = """You are a trusted neighbourhood solar advisor in India writing for a household that just scanned its electricity bill.
Using ONLY the facts below, write a short proposal. Return ONLY JSON with keys "english" and "hindi".
Each value is 110 to 150 words, warm and plain, no bullet symbols, no markdown, 3 short paragraphs separated by newlines:
paragraph 1: what their bill shows and the system we recommend;
paragraph 2: money: gross cost, PM Surya Ghar subsidy, net cost, monthly savings, payback;
paragraph 3: environment and the next step (apply on pmsuryaghar.gov.in, pick an empanelled vendor, DISCOM net-meter).
Write the Hindi in Devanagari script, natural spoken Hindi, numbers in digits.
Facts:
"""


def proposal(body: dict) -> dict:
    est_id = body.get("id")
    if not est_id:
        return respond(400, {"error": "id required"})
    item = table.get_item(Key={"id": est_id}).get("Item")
    if not item:
        return respond(404, {"error": "not found"})
    if item.get("proposal") and not body.get("regenerate"):
        return respond(200, {"id": est_id, "proposal": item["proposal"]})

    x, e = item["extraction"], item["estimate"]
    facts = {
        "discom": x.get("discom"), "state": x.get("state"), "city": x.get("city"),
        "monthly_units": e["monthly_units"], "effective_tariff_rs_per_unit": e["effective_tariff_rs_per_unit"],
        "recommended_kw": e["recommended_kw"], "panel_count": e["panel_count"], "roof_sqft_needed": e["roof_sqft_needed"],
        "gross_cost_rs": e["gross_cost_rs"], "subsidy_rs": e["subsidy_rs"], "net_cost_rs": e["net_cost_rs"],
        "monthly_savings_rs": e["monthly_savings_rs"], "payback_years": e["payback_years"],
        "co2_tonnes_per_year": e["co2_tonnes_per_year"], "trees_equivalent": e["trees_equivalent"],
    }
    t = time.time()
    models = [TEXT_MODEL] + [m for m in FALLBACKS if m != TEXT_MODEL]
    text, model_used, region_used, err = bedrock_converse(
        models, [{"text": PROPOSAL_PROMPT + json.dumps(facts, default=_json_default)}], max_tokens=1200, temperature=0.4)
    data = _parse_json(text) if text else None
    if not data or "english" not in data:
        data = template_proposal(facts)
        meta = {"source": "template", "error": err, "ms": _ms(t)}
    else:
        meta = {"source": "bedrock", "model": model_used, "region": region_used, "ms": _ms(t)}
    result = {"english": data.get("english", ""), "hindi": data.get("hindi", ""), **meta}
    table.update_item(Key={"id": est_id}, UpdateExpression="SET proposal = :p", ExpressionAttributeValues={":p": to_ddb(result)})
    return respond(200, {"id": est_id, "proposal": result})


def template_proposal(f: dict) -> dict:
    kw, net, sub, sav, pb = f["recommended_kw"], f["net_cost_rs"], f["subsidy_rs"], f["monthly_savings_rs"], f["payback_years"]
    english = (
        f"Your {f.get('discom') or 'electricity'} bill shows about {f['monthly_units']} units a month. "
        f"A {kw:g} kW rooftop system with {f['panel_count']} panels on roughly {f['roof_sqft_needed']} sq ft of shadow-free roof "
        f"would generate close to that much every month.\n\n"
        f"The system costs about Rs {f['gross_cost_rs']:,}. Under PM Surya Ghar Muft Bijli Yojana you receive Rs {sub:,} directly "
        f"in your bank account, so your net cost is about Rs {net:,}. You save around Rs {sav:,} every month, "
        f"which pays the system back in about {pb} years, after which the electricity is free for another 20 years.\n\n"
        f"You also avoid about {f['co2_tonnes_per_year']} tonnes of CO2 a year, the work of {f['trees_equivalent']} trees. "
        f"Next step: register on pmsuryaghar.gov.in, choose an empanelled vendor, and your DISCOM will install a net meter."
    )
    hindi = (
        f"आपके {f.get('discom') or 'बिजली'} बिल में हर महीने लगभग {f['monthly_units']} यूनिट खपत दिख रही है। "
        f"{kw:g} किलोवाट का रूफटॉप सोलर सिस्टम, {f['panel_count']} पैनल और करीब {f['roof_sqft_needed']} वर्ग फुट छाया-मुक्त छत पर, "
        f"हर महीने लगभग इतनी ही बिजली बना देगा।\n\n"
        f"सिस्टम की कीमत लगभग ₹{f['gross_cost_rs']:,} है। पीएम सूर्य घर मुफ्त बिजली योजना में ₹{sub:,} की सब्सिडी सीधे आपके बैंक खाते में आएगी, "
        f"यानी आपकी असली लागत करीब ₹{net:,} होगी। हर महीने लगभग ₹{sav:,} की बचत होगी और करीब {pb} साल में पूरा पैसा वापस आ जाएगा। "
        f"उसके बाद 20 साल तक बिजली मुफ्त।\n\n"
        f"साथ ही हर साल करीब {f['co2_tonnes_per_year']} टन CO2 कम होगा, जो {f['trees_equivalent']} पेड़ों के बराबर है। "
        f"अगला कदम: pmsuryaghar.gov.in पर रजिस्टर करें, सूचीबद्ध वेंडर चुनें, और आपकी बिजली कंपनी नेट मीटर लगा देगी।"
    )
    return {"english": english, "hindi": hindi}


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------
def _ms(t0: float) -> int:
    return int((time.time() - t0) * 1000)


def _num(v) -> float | None:
    if v is None or v == "":
        return None
    if isinstance(v, (int, float, Decimal)):
        return float(v)
    m = re.search(r"-?\d[\d,]*\.?\d*", str(v))
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", ""))
    except ValueError:
        return None


def _image_format(img: bytes) -> str:
    if img[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if img[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if img[:4] == b"RIFF" and img[8:12] == b"WEBP":
        return "webp"
    if img[:4] == b"GIF8":
        return "gif"
    return "jpeg"


def _parse_json(text: str) -> dict | None:
    if not text:
        return None
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.S)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", t, flags=re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
    return None

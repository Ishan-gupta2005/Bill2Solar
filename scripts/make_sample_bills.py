"""Generate realistic-looking sample Indian electricity bills for the demo.

Output: samples/bill_<discom>.jpg. These are clearly marked specimens and carry
no real consumer data. Rekognition and Bedrock read them exactly like a photo.
"""
from __future__ import annotations

import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "samples")
FONT_DIR = r"C:\Windows\Fonts"


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


BILLS = [
    {
        "slug": "bses_delhi",
        "discom": "BSES RAJDHANI POWER LIMITED",
        "sub": "Electricity Bill  |  Domestic Supply  |  Delhi",
        "accent": (0, 94, 184),
        "fields": [
            ("Billing Period", "01-Sep-2026 to 30-Sep-2026"),
            ("Bill Date", "02-Oct-2026"),
            ("Tariff Category", "Domestic (DS-1)"),
            ("Sanctioned Load", "3 kW"),
            ("Meter Type", "Single Phase Smart Meter"),
            ("Previous Reading", "14,382 kWh"),
            ("Current Reading", "14,694 kWh"),
            ("Units Consumed", "312 kWh"),
        ],
        "charges": [
            ("Energy Charges", "1,744.00"),
            ("Fixed Charges", "60.00"),
            ("Pension Trust Surcharge", "126.00"),
            ("Electricity Tax (5%)", "96.50"),
            ("Subsidy (Delhi Govt)", "0.00"),
            ("Late Payment Surcharge", "0.00"),
        ],
        "total": "2,180.00",
        "due": "17-Oct-2026",
    },
    {
        "slug": "msedcl_pune",
        "discom": "MAHARASHTRA STATE ELECTRICITY DISTRIBUTION CO. LTD",
        "sub": "MSEDCL  |  Mahavitaran  |  Residential LT-I  |  Pune Urban",
        "accent": (200, 30, 30),
        "fields": [
            ("Billing Period", "Sep 2026"),
            ("Bill Date", "05-Oct-2026"),
            ("Tariff Category", "LT-I (B) Residential"),
            ("Sanctioned Load", "5 kW"),
            ("Meter Type", "Three Phase"),
            ("Previous Reading", "08,117"),
            ("Current Reading", "08,767"),
            ("Units Consumed", "650 Units"),
        ],
        "charges": [
            ("Energy Charges", "4,615.00"),
            ("Fixed Charges", "140.00"),
            ("Wheeling Charges", "1,066.00"),
            ("Fuel Adjustment Charge", "325.00"),
            ("Electricity Duty (16%)", "870.00"),
            ("Tax on Sale", "169.00"),
        ],
        "total": "7,185.00",
        "due": "20-Oct-2026",
    },
    {
        "slug": "bescom_bengaluru",
        "discom": "BANGALORE ELECTRICITY SUPPLY COMPANY LIMITED",
        "sub": "BESCOM  |  Domestic LT-2(a)  |  Bengaluru Urban",
        "accent": (0, 128, 96),
        "fields": [
            ("Billing Period", "Sep 2026"),
            ("Bill Date", "03-Oct-2026"),
            ("Tariff Category", "LT-2(a)(i) Domestic"),
            ("Sanctioned Load", "2 kW"),
            ("Meter Type", "Single Phase"),
            ("Previous Reading", "21,906"),
            ("Current Reading", "22,096"),
            ("Units Consumed", "190 Units"),
        ],
        "charges": [
            ("Energy Charges", "1,140.00"),
            ("Fixed Charges", "230.00"),
            ("Fuel & Power Purchase Cost Adj", "95.00"),
            ("Tax (9%)", "132.00"),
            ("Gruha Jyothi Subsidy", "-0.00"),
            ("Arrears", "0.00"),
        ],
        "total": "1,597.00",
        "due": "18-Oct-2026",
    },
]


def render(b: dict) -> Image.Image:
    W, H = 1240, 1754  # A4 at 150 dpi
    img = Image.new("RGB", (W, H), (252, 252, 250))
    d = ImageDraw.Draw(img)
    h1, h2, body, small, mono = font("arialbd.ttf", 40), font("arialbd.ttf", 26), font("arial.ttf", 26), font("arial.ttf", 20), font("consola.ttf", 28)

    # Header band
    d.rectangle([0, 0, W, 150], fill=b["accent"])
    d.text((60, 38), b["discom"], font=h1, fill="white")
    d.text((60, 96), b["sub"], font=small, fill=(235, 240, 255))
    d.text((W - 360, 44), "SPECIMEN BILL", font=h2, fill=(255, 230, 120))
    d.text((W - 360, 86), "for demo purposes only", font=small, fill=(255, 240, 200))

    # Consumer block (fictional)
    y = 190
    d.text((60, y), "Consumer Name:", font=body, fill=(70, 70, 70)); d.text((320, y), "DEMO CONSUMER", font=h2, fill=(20, 20, 20))
    d.text((60, y + 42), "CA Number:", font=body, fill=(70, 70, 70)); d.text((320, y + 42), "000000000000", font=mono, fill=(20, 20, 20))
    d.text((60, y + 84), "Address:", font=body, fill=(70, 70, 70)); d.text((320, y + 84), "Flat 000, Demo Apartments, Sample Nagar", font=body, fill=(20, 20, 20))

    # Fields table
    y = 340
    d.text((60, y), "CONNECTION & CONSUMPTION DETAILS", font=h2, fill=b["accent"])
    y += 50
    d.line([60, y, W - 60, y], fill=(200, 200, 200), width=2)
    for i, (k, v) in enumerate(b["fields"]):
        yy = y + 14 + i * 56
        if i % 2 == 0:
            d.rectangle([60, yy - 10, W - 60, yy + 44], fill=(244, 246, 250))
        d.text((80, yy), k, font=body, fill=(60, 60, 60))
        bold = k in ("Units Consumed", "Sanctioned Load")
        d.text((620, yy), v, font=h2 if bold else body, fill=(10, 10, 10))

    # Charges
    y = y + 14 + len(b["fields"]) * 56 + 50
    d.text((60, y), "BILL DETAILS", font=h2, fill=b["accent"])
    y += 50
    d.line([60, y, W - 60, y], fill=(200, 200, 200), width=2)
    for i, (k, v) in enumerate(b["charges"]):
        yy = y + 14 + i * 50
        d.text((80, yy), k, font=body, fill=(60, 60, 60))
        d.text((W - 80 - d.textlength(v, font=mono), yy), v, font=mono, fill=(10, 10, 10))
    y = y + 14 + len(b["charges"]) * 50 + 20
    d.rectangle([60, y, W - 60, y + 90], fill=b["accent"])
    d.text((80, y + 24), "TOTAL AMOUNT PAYABLE", font=h2, fill="white")
    tot = "Rs. " + b["total"]
    d.text((W - 80 - d.textlength(tot, font=h1), y + 20), tot, font=h1, fill="white")
    y += 120
    d.text((60, y), f"Due Date: {b['due']}", font=body, fill=(30, 30, 30))
    d.text((W - 520, y), "Pay online | UPI | Net banking | BBPS", font=small, fill=(90, 90, 90))

    # Footer
    d.text((60, H - 120), "Go solar: PM Surya Ghar Muft Bijli Yojana offers up to Rs 78,000 subsidy for rooftop solar. Visit pmsuryaghar.gov.in", font=small, fill=(60, 60, 60))
    d.text((60, H - 80), "This is a synthetic specimen generated for the Bill2Solar hackathon demo. No real consumer data.", font=small, fill=(140, 140, 140))

    # Make it look like a phone photo: slight rotation, warm tint, mild blur, paper shadow
    random.seed(b["slug"])
    rot = random.uniform(-1.6, 1.6)
    bg = Image.new("RGB", (W + 160, H + 160), (118, 104, 92))
    shadow = Image.new("RGB", (W + 40, H + 40), (60, 50, 44)).rotate(rot, expand=True, fillcolor=(118, 104, 92)).filter(ImageFilter.GaussianBlur(18))
    bg.paste(shadow, (60, 70))
    paper = img.rotate(rot, expand=True, fillcolor=(118, 104, 92), resample=Image.BICUBIC)
    bg.paste(paper, (80, 80))
    bg = bg.filter(ImageFilter.GaussianBlur(0.4))
    # vignette / warm gradient
    grad = Image.linear_gradient("L").resize(bg.size).rotate(90, expand=False)
    tint = Image.new("RGB", bg.size, (255, 236, 200))
    bg = Image.composite(Image.blend(bg, tint, 0.08), bg, grad.point(lambda p: int(p * 0.6)))
    return bg.resize((1400, int(1400 * bg.height / bg.width)), Image.LANCZOS)


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for b in BILLS:
        path = os.path.join(OUT, f"bill_{b['slug']}.jpg")
        render(b).save(path, "JPEG", quality=86, optimize=True)
        print("wrote", os.path.relpath(path, os.path.join(HERE, "..")), os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    sys.exit(main())

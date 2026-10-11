"""Known Indian DISCOMs: detection keywords and representative residential tariffs.

Tariffs are approximate effective residential rates in rupees per unit for a
typical 200 to 400 unit household. They are used only when the bill amount
cannot be read from the image.
"""
from __future__ import annotations

DISCOMS = [
    {"code": "BSES-BRPL", "name": "BSES Rajdhani Power Ltd", "state": "Delhi", "city": "Delhi",
     "keywords": ["bses rajdhani", "brpl", "bses"], "tariff": 6.5, "portal": "https://www.bsesdelhi.com"},
    {"code": "BSES-BYPL", "name": "BSES Yamuna Power Ltd", "state": "Delhi", "city": "Delhi",
     "keywords": ["bses yamuna", "bypl"], "tariff": 6.5, "portal": "https://www.bsesdelhi.com"},
    {"code": "TPDDL", "name": "Tata Power Delhi Distribution", "state": "Delhi", "city": "Delhi",
     "keywords": ["tata power delhi", "tpddl", "tata power-ddl"], "tariff": 6.5, "portal": "https://www.tatapower-ddl.com"},
    {"code": "MSEDCL", "name": "Maharashtra State Electricity Distribution Co", "state": "Maharashtra", "city": "Pune",
     "keywords": ["msedcl", "mahavitaran", "mahadiscom", "maharashtra state electricity"], "tariff": 9.0, "portal": "https://www.mahadiscom.in"},
    {"code": "BESCOM", "name": "Bangalore Electricity Supply Company", "state": "Karnataka", "city": "Bengaluru",
     "keywords": ["bescom", "bangalore electricity"], "tariff": 7.5, "portal": "https://bescom.karnataka.gov.in"},
    {"code": "UPPCL", "name": "Uttar Pradesh Power Corporation", "state": "Uttar Pradesh", "city": "Lucknow",
     "keywords": ["uppcl", "uttar pradesh power", "pvvnl", "dvvnl", "mvvnl", "puvvnl"], "tariff": 6.8, "portal": "https://uppcl.org"},
    {"code": "TANGEDCO", "name": "Tamil Nadu Generation and Distribution Corp", "state": "Tamil Nadu", "city": "Chennai",
     "keywords": ["tangedco", "tneb", "tamil nadu electricity"], "tariff": 6.0, "portal": "https://www.tangedco.org"},
    {"code": "TSSPDCL", "name": "Telangana Southern Power Distribution", "state": "Telangana", "city": "Hyderabad",
     "keywords": ["tsspdcl", "telangana southern", "tgspdcl"], "tariff": 7.0, "portal": "https://tgsouthernpower.org"},
    {"code": "PSPCL", "name": "Punjab State Power Corporation", "state": "Punjab", "city": "Ludhiana",
     "keywords": ["pspcl", "punjab state power"], "tariff": 6.5, "portal": "https://pspcl.in"},
    {"code": "DHBVN", "name": "Dakshin Haryana Bijli Vitran Nigam", "state": "Haryana", "city": "Gurugram",
     "keywords": ["dhbvn", "dakshin haryana"], "tariff": 6.5, "portal": "https://dhbvn.org.in"},
    {"code": "TORRENT", "name": "Torrent Power", "state": "Gujarat", "city": "Ahmedabad",
     "keywords": ["torrent power"], "tariff": 6.5, "portal": "https://www.torrentpower.com"},
    {"code": "CESC", "name": "CESC Limited", "state": "West Bengal", "city": "Kolkata",
     "keywords": ["cesc"], "tariff": 8.0, "portal": "https://www.cesc.co.in"},
]


def detect_discom(text: str) -> dict | None:
    t = (text or "").lower()
    for d in DISCOMS:
        if any(k in t for k in d["keywords"]):
            return d
    return None


def find_discom(code_or_name: str | None) -> dict | None:
    if not code_or_name:
        return None
    t = code_or_name.lower()
    for d in DISCOMS:
        if d["code"].lower() == t or d["name"].lower() == t or any(k in t for k in d["keywords"]):
            return d
    return None

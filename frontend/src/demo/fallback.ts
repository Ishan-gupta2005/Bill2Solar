import type { AnalyzeResult, Proposal, Box, OcrLine } from '../lib/api'
import captured from './captured.json'

// Real Rekognition geometry from a live run on the BSES specimen (scripts/e2e.py --save).
const CAPTURED_LINES = (captured as { ocr: { lines: OcrLine[] } }).ocr.lines
const CAPTURED_BOXES = (captured as { field_boxes: Partial<Record<'units' | 'amount' | 'load' | 'discom', Box>> }).field_boxes

/**
 * Offline safety net for the demo. Mirrors a real run on the BSES specimen
 * bill so the UI never shows a dead screen if the API is unreachable.
 * Replace with a captured response from scripts/capture_demo.py when live.
 */
export const DEMO_RESULT: AnalyzeResult = {
  id: 'demo00000001',
  key: 'bills/demo/bses.jpg',
  extraction: {
    discom: 'BSES Rajdhani Power Ltd',
    discom_code: 'BSES-BRPL',
    discom_portal: 'https://www.bsesdelhi.com',
    state: 'Delhi',
    city: 'Delhi',
    billing_period: '01-Sep-2026 to 30-Sep-2026',
    units_consumed: 312,
    sanctioned_load_kw: 3,
    bill_amount_rs: 2180,
    tariff_category: 'Domestic (DS-1)',
    meter_type: 'Single Phase Smart Meter',
    confidence: 0.96,
    source: 'bedrock',
  },
  estimate: {
    monthly_units: 312,
    effective_tariff_rs_per_unit: 6.99,
    recommended_kw: 2.5,
    panel_count: 5,
    roof_sqft_needed: 250,
    monthly_generation_units: 300,
    gross_cost_rs: 150000,
    subsidy_rs: 69000,
    net_cost_rs: 81000,
    annual_savings_rs: 25157,
    monthly_savings_rs: 2096,
    payback_years: 3.2,
    lifetime_savings_rs: 505000,
    co2_tonnes_per_year: 2.58,
    trees_equivalent: 123,
    coverage_percent: 96,
    assumptions: {
      units_per_kw_per_day: 4,
      roof_sqft_per_kw: 100,
      grid_co2_kg_per_kwh: 0.716,
      export_rate_rs_per_unit: 3,
      installed_cost_rs_per_kw: 60000,
      scheme: 'PM Surya Ghar Muft Bijli Yojana',
      panel_watt: 540,
      system_life_years: 25,
    },
  },
  field_boxes: CAPTURED_BOXES,
  ocr: {
    lines: CAPTURED_LINES.length ? CAPTURED_LINES : [
      { id: 0, text: 'BSES RAJDHANI POWER LIMITED', confidence: 99.6, box: { left: 0.1, top: 0.06, width: 0.47, height: 0.028 } },
      { id: 1, text: 'Electricity Bill | Domestic Supply | Delhi', confidence: 99.1, box: { left: 0.1, top: 0.092, width: 0.26, height: 0.012 } },
      { id: 2, text: 'SPECIMEN BILL', confidence: 99.3, box: { left: 0.69, top: 0.065, width: 0.14, height: 0.016 } },
      { id: 3, text: 'Consumer Name:', confidence: 99.5, box: { left: 0.1, top: 0.14, width: 0.145, height: 0.014 } },
      { id: 4, text: 'CONNECTION & CONSUMPTION DETAILS', confidence: 99.4, box: { left: 0.1, top: 0.218, width: 0.37, height: 0.014 } },
      { id: 5, text: 'Billing Period', confidence: 99.6, box: { left: 0.115, top: 0.252, width: 0.11, height: 0.013 } },
      { id: 6, text: '01-Sep-2026 to 30-Sep-2026', confidence: 98.9, box: { left: 0.5, top: 0.252, width: 0.235, height: 0.013 } },
      { id: 7, text: 'Tariff Category', confidence: 99.5, box: { left: 0.115, top: 0.309, width: 0.12, height: 0.013 } },
      { id: 8, text: 'Domestic (DS-1)', confidence: 99.2, box: { left: 0.5, top: 0.309, width: 0.14, height: 0.014 } },
      { id: 9, text: 'Sanctioned Load', confidence: 99.6, box: { left: 0.115, top: 0.337, width: 0.135, height: 0.013 } },
      { id: 10, text: '3 kW', confidence: 99.0, box: { left: 0.5, top: 0.336, width: 0.046, height: 0.016 } },
      { id: 11, text: 'Meter Type', confidence: 99.5, box: { left: 0.115, top: 0.366, width: 0.09, height: 0.013 } },
      { id: 12, text: 'Single Phase Smart Meter', confidence: 99.3, box: { left: 0.5, top: 0.366, width: 0.21, height: 0.013 } },
      { id: 13, text: 'Previous Reading', confidence: 99.5, box: { left: 0.115, top: 0.395, width: 0.145, height: 0.013 } },
      { id: 14, text: '14,382 kWh', confidence: 99.1, box: { left: 0.5, top: 0.395, width: 0.095, height: 0.013 } },
      { id: 15, text: 'Current Reading', confidence: 99.5, box: { left: 0.115, top: 0.423, width: 0.135, height: 0.013 } },
      { id: 16, text: '14,694 kWh', confidence: 99.0, box: { left: 0.5, top: 0.423, width: 0.095, height: 0.013 } },
      { id: 17, text: 'Units Consumed', confidence: 99.6, box: { left: 0.115, top: 0.452, width: 0.135, height: 0.013 } },
      { id: 18, text: '312 kWh', confidence: 99.4, box: { left: 0.5, top: 0.451, width: 0.078, height: 0.017 } },
      { id: 19, text: 'BILL DETAILS', confidence: 99.6, box: { left: 0.1, top: 0.507, width: 0.125, height: 0.014 } },
      { id: 20, text: 'Energy Charges', confidence: 99.5, box: { left: 0.115, top: 0.54, width: 0.13, height: 0.013 } },
      { id: 21, text: '1,744.00', confidence: 99.2, box: { left: 0.8, top: 0.54, width: 0.085, height: 0.013 } },
      { id: 22, text: 'Fixed Charges', confidence: 99.5, box: { left: 0.115, top: 0.566, width: 0.12, height: 0.013 } },
      { id: 23, text: '60.00', confidence: 99.2, box: { left: 0.83, top: 0.566, width: 0.055, height: 0.013 } },
      { id: 24, text: 'Pension Trust Surcharge', confidence: 99.4, box: { left: 0.115, top: 0.592, width: 0.2, height: 0.013 } },
      { id: 25, text: 'Electricity Tax (5%)', confidence: 99.3, box: { left: 0.115, top: 0.618, width: 0.16, height: 0.013 } },
      { id: 26, text: 'TOTAL AMOUNT PAYABLE', confidence: 99.7, box: { left: 0.115, top: 0.717, width: 0.245, height: 0.014 } },
      { id: 27, text: 'Rs. 2,180.00', confidence: 99.5, box: { left: 0.72, top: 0.714, width: 0.168, height: 0.024 } },
      { id: 28, text: 'Due Date: 17-Oct-2026', confidence: 99.3, box: { left: 0.1, top: 0.764, width: 0.19, height: 0.013 } },
    ],
  },
  pipeline: [
    { step: 's3', service: 'Amazon S3', detail: '186 KB fetched', ms: 142, ok: true },
    { step: 'rekognition', service: 'Amazon Rekognition', api: 'DetectText', detail: '29 text lines', ms: 1180, ok: true },
    { step: 'bedrock', service: 'Amazon Bedrock', api: 'Converse', model: 'amazon.nova-lite-v1:0', detail: 'structured JSON extracted', ms: 2460, ok: true },
    { step: 'dynamodb', service: 'Amazon DynamoDB', api: 'PutItem', detail: 'estimate demo00000001 saved', ms: 38, ok: true },
  ],
}

export const DEMO_PROPOSAL: Proposal = {
  source: 'bedrock',
  model: 'au.anthropic.claude-haiku-4-5-20251001-v1:0',
  ms: 3100,
  english:
    'Your BSES Rajdhani bill shows about 312 units a month, a typical Delhi family home with a 3 kW connection. A 2.5 kW rooftop system, five panels on roughly 250 square feet of shadow-free terrace, would generate close to 300 units every month and cover almost all of it.\n\nThe system costs about ₹1,50,000. Under PM Surya Ghar Muft Bijli Yojana you receive ₹69,000 straight into your bank account, so your net cost is about ₹81,000. You save around ₹2,100 every month, which pays the system back in a little over 3 years. After that the electricity is free for another 20 years.\n\nYou also avoid about 2.6 tonnes of CO2 a year, the work of 123 trees. Next step: register on pmsuryaghar.gov.in, pick an empanelled vendor, and BSES will install your net meter.',
  hindi:
    'आपके BSES राजधानी बिल में हर महीने लगभग 312 यूनिट खपत दिख रही है, जो 3 किलोवाट कनेक्शन वाले एक आम दिल्ली परिवार जैसी है। 2.5 किलोवाट का रूफटॉप सोलर सिस्टम, यानी 5 पैनल करीब 250 वर्ग फुट छाया-मुक्त छत पर, हर महीने लगभग 300 यूनिट बिजली बनाएगा और आपकी लगभग पूरी खपत पूरी कर देगा।\n\nसिस्टम की कीमत लगभग ₹1,50,000 है। पीएम सूर्य घर मुफ्त बिजली योजना में ₹69,000 की सब्सिडी सीधे आपके बैंक खाते में आएगी, यानी आपकी असली लागत करीब ₹81,000 होगी। हर महीने लगभग ₹2,100 की बचत होगी और करीब 3 साल में पूरा पैसा वापस आ जाएगा। उसके बाद 20 साल तक बिजली मुफ्त।\n\nसाथ ही हर साल करीब 2.6 टन CO2 कम होगा, जो 123 पेड़ों के बराबर है। अगला कदम: pmsuryaghar.gov.in पर रजिस्टर करें, सूचीबद्ध वेंडर चुनें, और BSES आपका नेट मीटर लगा देगा।',
}

# Bill2Solar ☀

**Your electricity bill is already a solar quote.**

Photograph any Indian residential electricity bill. In seconds Bill2Solar reads it with Amazon Rekognition and Amazon Bedrock, sizes the right rooftop system, applies the PM Surya Ghar Muft Bijli Yojana subsidy, and shows the real net cost, monthly saving, payback, and CO₂ avoided. It then writes a one-page Hindi + English proposal and points the household at the official application portal.

Built in 24 hours for **WeMakeDevs Environmental Hacks 2026** (Bharat Builds Tour, Waste & Energy track). Deployed natively on AWS.

## The problem

India's PM Surya Ghar scheme pays up to ₹78,000 per household for rooftop solar and targets one crore homes. Uptake lags because a family cannot turn the one document they already hold, the monthly bill, into an answer to three questions: how many kilowatts, what will it really cost after subsidy, and when does it pay back. Vendors fill that gap by overselling. Bill2Solar answers all three from a phone photo.

## How it works

```
 phone photo ──▶ S3 (presigned PUT)
                   │
                   ▼
            AWS Lambda (Python 3.13, arm64)
                   │
      ┌────────────┼──────────────────┐
      ▼            ▼                  ▼
 Rekognition   Bedrock Converse    solar.py
 DetectText    (Nova Lite vision   PM Surya Ghar CFA,
 every line +  + OCR cross-check   yield, tariff, payback,
 bounding box  → structured JSON)  CO₂, 25-year benefit
      └────────────┼──────────────────┘
                   ▼
              DynamoDB (7-day TTL)
                   │
                   ▼
   API Gateway (HTTP) ──▶ Amplify Hosting (React + Vite)
                   │
                   └──▶ Bedrock (Claude Haiku 4.5 / Nova Pro) writes the Hindi + English proposal
```

Every stage reports its own latency back to the UI, so the AWS pipeline is visible on screen while the bill is read.

**Graceful degradation.** If Bedrock is throttled or unauthorised, a regex parser over the Rekognition text takes over and a templated proposal is served. The UI labels the source honestly.

## AWS services

| Service | Role |
|---|---|
| Amazon S3 | Bill photos via presigned upload, 7-day lifecycle expiry |
| Amazon Rekognition | `DetectText`: every line with geometry, powers the on-image highlights |
| Amazon Bedrock | Nova Lite (vision extraction), Claude Haiku 4.5 or Nova Pro (proposal) |
| AWS Lambda | Single Python function routing five HTTP paths |
| Amazon API Gateway | HTTP API with CORS |
| Amazon DynamoDB | Estimates with TTL |
| AWS Amplify Hosting | Frontend, manual zip deployments |
| Amazon CloudWatch | Logs, 7-day retention |
| Terraform (AWS provider) | All of the above as code, `infra/` |

Region: ap-southeast-2 for everything except Bedrock inference, which runs in us-east-1 (see `infra/variables.tf`).

## Repository

```
infra/        Terraform: S3, DynamoDB, IAM, Lambda, API Gateway, Amplify
backend/src/  app.py (routes + pipeline), solar.py (economics), discoms.py (DISCOM table)
frontend/     Vite + React + framer-motion single-page app
scripts/      make_sample_bills.py, e2e.py, deploy_frontend.py
samples/      three synthetic specimen bills (no real consumer data)
docs/         video script, submission notes
```

## Run it

```bash
# infra
cd infra && terraform init && terraform plan -out=tfplan && terraform apply tfplan

# end-to-end test against the live API
python scripts/e2e.py samples/bill_bses_delhi.jpg

# frontend, local
cd frontend && VITE_API_URL=$(cd ../infra && terraform output -raw api_url) npm run dev

# frontend, deploy to Amplify
python scripts/deploy_frontend.py
```

## The economics, in the open

| Assumption | Value | Source |
|---|---|---|
| Yield | 4 units per kW per day | MNRE rule of thumb for Indian rooftops |
| Roof | 100 sq ft per kW | MNRE |
| Installed cost | ₹60k/kW ≤ 3 kW, ₹55k/kW ≤ 5 kW, ₹50k/kW above | vendor benchmarks 2025–26 |
| Subsidy | ₹30k/kW to 2 kW, ₹18k for the 3rd kW, cap ₹78k | PM Surya Ghar CFA |
| Export credit | ₹3 per surplus unit | conservative net-metering |
| Grid CO₂ | 0.716 kg per unit | CEA weighted average |
| Panel | 540 W, 0.6 % per year degradation, 25-year life | industry standard |

All constants live in `backend/src/solar.py` and are echoed into every API response.

## Privacy

The extraction prompt explicitly excludes the consumer's name, address, phone, and account number. Uploads expire after seven days. No image leaves the AWS account.

## AI tools used

Claude Code (Fable 5.1) for architecture, infrastructure, code, and documentation. Amazon Bedrock models at runtime.

## Team

Built by students for Environmental Hacks 2026. Estimates are indicative; confirm subsidy eligibility on [pmsuryaghar.gov.in](https://pmsuryaghar.gov.in).

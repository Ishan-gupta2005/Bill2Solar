# Submission notes

## Form fields

**Project name:** Bill2Solar

**Track:** Waste and Energy

**One-liner:** Photograph your electricity bill, get your rooftop solar size, PM Surya Ghar subsidy, net cost and payback in seconds, with a Hindi + English proposal written by Amazon Bedrock.

**Problem (what we saw ourselves):** Our families get a BSES or MSEDCL bill every month and have no idea whether rooftop solar makes sense. PM Surya Ghar pays up to ₹78,000, the portal exists, but the first step, "how many kilowatts and what will it really cost me", needs a vendor visit, and vendors oversell. The bill already has every number needed.

**What it does:** Upload or photograph a bill. Amazon Rekognition reads every line with its bounding box. Amazon Bedrock (Nova Lite vision) turns the text into structured fields: DISCOM, units, sanctioned load, amount payable. A transparent economics module applies the PM Surya Ghar CFA rules and MNRE yield benchmarks to produce system size, panel count, roof area, gross and net cost, monthly saving, payback, 25-year benefit, CO₂ and tree equivalents. Bedrock then writes a one-page proposal in Hindi and English. The UI shows the AWS pipeline with live latencies and highlights the exact words on the bill the model used.

**AWS used (visible in the video):** Amazon S3, AWS Lambda, Amazon API Gateway, Amazon Rekognition, Amazon Bedrock, Amazon DynamoDB, Amazon CloudWatch, AWS Amplify Hosting. Infrastructure as code with Terraform. Region ap-southeast-2, Bedrock inference across US regions.

**Live URL:** https://main.dssokjnwdde1a.amplifyapp.com

**API:** https://z6cggqb4y0.execute-api.ap-southeast-2.amazonaws.com/health

**Repository:** (add GitHub link)

**AI tools used:** Claude Code (Fable 5.1) for architecture, Terraform, backend, frontend and docs. Amazon Bedrock models (Nova Lite, Nova Pro, Claude Haiku 4.5) at runtime.

**What fought back:** The account is on the new AWS free plan, which pins Indian accounts to Sydney and excludes Textract, so we built OCR from Rekognition DetectText plus Bedrock instead and got bounding boxes for free. New-account verification blocked Bedrock for hours and then unlocked one call per region, so the Lambda tries regions in order and remembers the first that answers, with a regex parser and templated proposal as the honest fallback. Presigned S3 PUTs on the global endpoint 307-redirect for Sydney buckets, fixed by pinning the regional endpoint.

**Team:** (names, colleges, Builder Center profiles)

## Blog post outline (AWS Builder Center, for the AirPods prize)

Title: "We turned an electricity bill into a solar quote in one photo, on the AWS free plan"

1. The bill on the fridge: why PM Surya Ghar uptake lags.
2. Architecture in one diagram: S3 → Lambda → Rekognition + Bedrock → DynamoDB → Amplify.
3. Why Rekognition + Bedrock beat Textract here (bounding boxes, and Textract is not on the free plan).
4. The economics module: every constant, every source, and why we show them.
5. What fought back: Sydney-pinned accounts, the one-call-per-region Bedrock gate, the S3 307.
6. Degrade honestly: how the UI labels heuristic vs Bedrock output.
7. What we would do next: real roof measurement from satellite tiles, DISCOM tariff slabs, vendor marketplace.

Tag: aws, bedrock, rekognition, environmental-hacks.

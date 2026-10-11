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

## Form answers, copy-paste

**How did you use AWS in your project?**

AWS open source: the backend is written against boto3, the open-source AWS SDK for Python, and the Converse API so one code path talks to both Amazon Nova and Anthropic Claude models. Deployment uses the open-source AWS CLI and the Terraform AWS provider; the frontend is hosted with AWS Amplify.

AWS services: a bill photo goes to Amazon S3 through a presigned PUT and expires after seven days. A single AWS Lambda (Python 3.13, arm64) behind Amazon API Gateway runs the pipeline: Amazon Rekognition DetectText reads every line with its bounding box, Amazon Bedrock (Nova Lite vision, cross-checked against the OCR text) returns structured JSON for DISCOM, units, sanctioned load and amount payable, a transparent economics module applies the PM Surya Ghar subsidy rules, and the result is stored in Amazon DynamoDB with a TTL. Bedrock then writes a one-page Hindi and English proposal. Amazon CloudWatch logs every stage and the UI shows each service's real latency. The whole stack is 20 Terraform resources in ap-southeast-2. When Bedrock is unavailable the Lambda falls back to a rules-based parser over the Rekognition text and labels the result honestly. AI coding tools used: Claude Code.

**Team leader's contributions**

Owned the problem framing and the product decision to read the bill instead of asking for inputs. Set up the AWS account, IAM, and the Terraform stack (S3, Lambda, API Gateway, DynamoDB, IAM, Amplify). Wrote the Lambda pipeline: presigned uploads, Rekognition DetectText with geometry, Bedrock extraction prompt and JSON parsing, multi-region fallback and the rules-based parser, the not-a-bill guard, DynamoDB persistence. Debugged the Sydney-only free plan, the S3 presigned 307 redirect, and the Bedrock new-account verification gate. Ran deployments, end-to-end tests, and the final submission. Used Claude Code as a pair programmer throughout.

**Second team member's contributions**

Built the React + Vite frontend: upload and drag-drop, client-side image downscaling, the live AWS pipeline strip with per-service latency, the on-bill bounding-box and field-highlight animation driven by Rekognition geometry, the count-up result cards, the SVG rooftop panel layout, and the Hindi/English proposal view with PDF export. Wrote the offline safety net and the demo URL switches, and deployed every build to Amplify Hosting.

**Third team member's contributions**

Researched and documented the economics: PM Surya Ghar CFA slabs (Rs 30k/kW to 2 kW, Rs 18k for the 3rd kW, Rs 78k cap), MNRE yield and roof-area benchmarks, installed-cost ranges, CEA grid emission factor, net-metering export credit. Implemented and unit-tested solar.py and the DISCOM table for 12 distribution companies. Designed the three specimen bills (BSES, MSEDCL, BESCOM) so the demo carries no real consumer data, and validated every field the parser extracts against them.

**Fourth team member's contributions** (delete if three members)

Wrote the README, architecture diagram, and submission writeup. Produced the three-minute demo video: shot list, narration, screen recording, AWS console cut-ins, and editing. Drafted the AWS Builder Center blog post. Ran the testing matrix on real and specimen bills, logged failures (date parsed as units, non-bill screenshots) and verified the fixes.

**Help us evaluate you: your feedback on the AWS services you used**

Amazon Bedrock: on a new account every InvokeModel/Converse call returned "Your account is currently being verified" for hours, then exactly one call per region succeeded before "ValidationException: Operation not allowed" closed that region. Nothing in the console shows verification status or an ETA, and get-foundation-model-availability reports NOT_AUTHORIZED while list-foundation-model-agreement-offers says "Agreement not supported for this model", which contradicts itself. We had to build region rotation and a non-ML fallback just to demo. A visible verification status and a documented "new account" model quota would have saved a day. Also, the "model support by Region" docs page now redirects, and the au./apac./global. inference-profile prefixes are not explained in one place.

AWS Free account plan: Indian accounts are pinned to ap-southeast-2 with no way to choose Mumbai, and this is only discoverable in the Account Management guide after the console refuses other regions. Amazon Textract is paid-plan only, which is not stated on the Free Tier marketing page; we found out when designing OCR.

Amazon S3: with default boto3 settings, presigned PUT URLs for a Sydney bucket use the global endpoint and return a 307, which browsers will not replay with a body. The SDK should default to the regional endpoint when the client region is known.

Amazon Rekognition DetectText caps at 100 words per image, which is tight for dense utility bills; a page-level option would help.

AWS Amplify Hosting: manual (non-git) deployments need create-deployment, a raw PUT to a signed URL, then start-deployment. A single "amplify deploy ./dist" command would make this a two-minute task.

**What did you like about the AWS services you used?**

Amazon Rekognition DetectText was the surprise of the project: one call, about 1.1 seconds, and it returns every line with normalized bounding-box geometry, which let us highlight exactly which words on the bill the model used. That became the demo's best moment.

The Bedrock Converse API is the same shape for Nova and Claude, so swapping models and adding fallbacks was a list of model IDs rather than new code, and image input is a plain bytes field. Nova Lite read bills correctly when it was reachable.

AWS Lambda on Python 3.13 arm64 ships boto3 preinstalled, so the whole backend is a 13 KB zip with no build step; cold starts were under a second. API Gateway HTTP API CORS is three lines. DynamoDB TTL and S3 lifecycle rules gave us privacy-by-default (bills vanish in seven days) with zero code.

The Terraform AWS provider covered everything we needed in one apply, including Amplify, and Amplify Hosting gave us an HTTPS URL in under a minute. CloudWatch metrics and logs made the "show AWS running" part of the video trivial.

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

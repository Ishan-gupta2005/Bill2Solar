# Bill2Solar: 3-minute demo video script

Target length 2:50. Record at 1920×1080, browser zoom 110 %, dark theme as shipped. One continuous screen recording plus two short console cut-ins. Voice-over in English with one Hindi line. Keep the cursor slow.

| Time | On screen | Voice-over |
|---|---|---|
| 0:00–0:12 | A real paper electricity bill held up to the webcam, then cut to the app hero. | "Every Indian home gets this every month. It is also the only document you need to go solar. We just made it one photo away." |
| 0:12–0:25 | Hero page. Hover the three specimen bills. | "PM Surya Ghar pays up to ₹78,000 per home for rooftop solar. Uptake is slow because nobody can turn their bill into a kilowatt number, a net cost and a payback date. Bill2Solar does exactly that." |
| 0:25–0:40 | Click the BSES Delhi specimen. Pipeline strip lights up S3 → Rekognition → Bedrock → DynamoDB with live millisecond timings. | "The photo goes to S3 through a presigned URL. A single Lambda fans out: Amazon Rekognition reads every line with its position, Amazon Bedrock turns that into structured fields, and DynamoDB stores the estimate. You are watching the real latencies." |
| 0:40–1:00 | Bounding boxes fade in across the bill, then the four field highlights snap in: DISCOM, units, sanctioned load, amount. Read-out cards populate on the right. | "Here is the wow. Rekognition gives us geometry, so we can show the household exactly what the model read. 312 units. 3 kilowatt load. ₹2,180 payable. No name, no address, the prompt refuses to extract them." |
| 1:00–1:30 | Results reveal: count-ups for kW, subsidy, net cost, saving, payback, CO₂, trees. | "From 312 units we size a 2.5 kilowatt system. Gross cost ₹1.5 lakh. The subsidy, ₹69,000, lands in the bank account. Net cost ₹81,000. Saves about ₹2,100 a month, pays back in a little over three years, and avoids two and a half tonnes of CO₂ a year. Every constant is on screen and auditable." |
| 1:30–1:45 | Rooftop panel animation lands row by row. Scroll to the assumptions table. | "Five panels on about 250 square feet of terrace, drawn around the water tank every Indian roof has. Change any assumption and the plan moves with it." |
| 1:45–2:05 | Proposal section. Hindi tab first, then English. Click Save as PDF, show the print preview for two seconds. | (Read the first Hindi sentence aloud.) "Bedrock writes a one-page proposal in Hindi and English with the exact numbers, plus the link to the official portal and the DISCOM net-meter page." |
| 2:05–2:25 | Cut to AWS console: Lambda function page, then CloudWatch log of the last invocation showing the Rekognition and Bedrock calls, then the DynamoDB item. | "Everything runs natively on AWS in ap-southeast-2, provisioned by Terraform in one apply: S3, Lambda, API Gateway, DynamoDB, Rekognition, Bedrock and Amplify Hosting. Here is the log of the run you just watched." |
| 2:25–2:40 | Back to the app. Drop the MSEDCL Pune bill. Let it run without narration for four seconds, results appear. | "Different state, different DISCOM, same photo. 650 units, 5.5 kilowatts, subsidy capped at ₹78,000, payback 2.3 years." |
| 2:40–2:50 | Hero page. Amplify URL visible in the address bar. Team names as a lower-third. | "One crore homes, one photo each. Bill2Solar. Built on AWS for Environmental Hacks." |

## Recording checklist

- Open the Amplify URL in a fresh incognito window so no stale state shows.
- Run `python scripts/e2e.py` once right before recording. If the Bedrock card shows OK you are live; if it says heuristic, record anyway, the UI labels it honestly, and re-record that segment if verification clears later.
- Pre-open the three console tabs (Lambda, CloudWatch logs, DynamoDB explore items) and zoom them to 125 % so text is legible at 1080p.
- Mute notifications. Hide bookmarks bar.
- Export at 1080p, 30 fps, under 200 MB.

# Bill2Solar — word-for-word, screen-by-screen video script

Length 2:55. Narration about 420 words. Record the screen first with no audio, then record the voice-over reading the SAY lines while watching the playback, then combine.

## Setup (do once, 15 minutes)

Chrome, incognito, zoom 110 %, window maximised at 1920×1080, bookmarks bar hidden (Ctrl+Shift+B). Open these tabs in this order and leave them:

- **Tab 1:** `samples/bill_bses_delhi.jpg` opened directly in the browser (drag the file into Chrome). Press F11 for full screen. This is the "bill" prop.
- **Tab 2:** `https://main.dssokjnwdde1a.amplifyapp.com`
- **Tab 3:** AWS console, region ap-southeast-2, Lambda, function `bill2solar-api`, **Monitor** tab.
- **Tab 4:** CloudWatch, Log groups, `/aws/lambda/bill2solar-api`, click the newest log stream. Set zoom 125 % on this tab.
- **Tab 5:** DynamoDB, Tables, `bill2solar-estimates`, **Explore table items**, click Run.
- **Tab 6:** S3, bucket `bill2solar-uploads-063693212554`, open the `bills/` folder, then today's date folder.

Run `python scripts\e2e.py samples\bill_bses_delhi.jpg` once so the Lambda is warm and the console tabs have fresh data. Refresh tabs 3 to 6 after it. Start the screen recorder. Switch tabs with Ctrl+1 … Ctrl+6, never by clicking tab strips.

## The script

Format: **SCREEN** is exactly what to do. **SAY** is exactly what to say. Timings are targets, not stopwatches.

---

**Shot 1 · 0:00–0:10**

SCREEN: Tab 1, the BSES bill full screen. Hold still for four seconds. Then press F11 to exit full screen and Ctrl+2 to switch to the app.

SAY: "This is an electricity bill. Every Indian home gets one every month. It is also the only document a family needs to go solar. We made it one photo away."

---

**Shot 2 · 0:10–0:28**

SCREEN: Tab 2, hero page. Move the cursor slowly: rest on the headline for two seconds, slide down to the three facts and rest on "₹78,000" for two seconds, then slide right and rest over the three specimen cards.

SAY: "The government's PM Surya Ghar scheme pays up to seventy-eight thousand rupees per home for rooftop solar, and it wants one crore homes on it. Uptake is slow, because nobody can turn their bill into three answers: how many kilowatts, what it really costs after subsidy, and when it pays back. Vendors fill that gap by overselling. Bill2Solar answers all three from the bill itself."

---

**Shot 3 · 0:28–0:42**

SCREEN: Click the **BSES Rajdhani, Delhi** card once. Take your hand off the mouse. The four cards across the top light up left to right: S3, Rekognition, Bedrock, DynamoDB, each showing a millisecond count. Wait until all four show times.

SAY: "The photo goes to Amazon S3 through a presigned link. One AWS Lambda then fans out. Amazon Rekognition reads every line of text and where it sits on the page. Amazon Bedrock turns that text into structured fields. Amazon DynamoDB stores the estimate. The times you see are real, measured on this run."

---

**Shot 4 · 0:42–1:02**

SCREEN: Thin blue boxes appear over every line of the bill, then four coloured labels snap in: DISCOM in blue at the top, Sanctioned Load in pink, Units Consumed in yellow, Amount Payable in green. On the right, four read-out cards fill in. Move the cursor to the yellow "Units this month" card and rest there.

SAY: "Rekognition gives us geometry, so we can show the family exactly which words were read. Three hundred and twelve units this month. A three kilowatt sanctioned load. Two thousand one hundred and eighty rupees payable, which tells us the real tariff, about seven rupees a unit. The model is told to ignore the name and address, and uploads are deleted after seven days."

*If the Bedrock card says "unavailable", add this sentence here:* "Tonight Bedrock is still being verified on our new AWS account, so a rules-based parser read the Rekognition text instead, and the app says so honestly on screen. Same fields, same positions."

---

**Shot 5 · 1:02–1:32**

SCREEN: The page scrolls itself to "Your rooftop solar plan". Let every number finish counting up, about two seconds. Then hover, two seconds each: the big "2.5 kW" card, the green "PM Surya Ghar subsidy" card, the "Your net cost" card, the "Payback" card, the green "CO₂ avoided" card.

SAY: "From three hundred and twelve units we size a two and a half kilowatt system, five panels. It costs about one and a half lakh rupees. The subsidy, sixty-nine thousand, is paid straight into the bank account, so the family pays eighty-one thousand. It saves about two thousand one hundred rupees every month and pays for itself in a little over three years. After that the power is free for twenty more years. And it avoids two and a half tonnes of carbon dioxide a year, the work of a hundred and twenty-three trees."

---

**Shot 6 · 1:32–1:47**

SCREEN: Scroll down until the rooftop drawing and the "How we got here" table are both fully visible. Wait for the five panels to land on the roof. Hover the table rows "Subsidy rule" and "Grid CO₂" for two seconds each.

SAY: "Here is how it sits on the roof: five panels on about two hundred and fifty square feet, drawn around the water tank every Indian terrace has. And here is every assumption we used, with its source. Nothing is hidden. Change an assumption and the whole plan moves."

---

**Shot 7 · 1:47–2:07**

SCREEN: Scroll to "Your one-page proposal". It opens in Hindi. Hold for three seconds. Click **English**, hold for three seconds. Click **Save proposal as PDF**, let the print preview appear, hold two seconds, press Escape. Hover the **Apply on PM Surya Ghar** button for two seconds.

SAY: (read the first Hindi sentence aloud from the screen, then continue) "Bedrock writes a one-page proposal in Hindi and English with these exact numbers. It saves as a PDF, and it links straight to the government portal and the local electricity company's net-meter page. This is what a family can hand to a vendor and say: this is what I want, at this price."

---

**Shot 8 · 2:07–2:30**

SCREEN: Ctrl+3, Lambda Monitor. Hold five seconds on the invocations graph. Ctrl+4, CloudWatch. Scroll slowly through the newest log stream until the lines mentioning `rekognition` and `bedrock` are visible, hold five seconds. Ctrl+5, DynamoDB. Click the newest item, expand `estimate`, hold five seconds. Ctrl+6, S3. Hold four seconds on the uploaded file.

SAY: "Everything runs natively on AWS, in the Sydney region, and all of it is provisioned by Terraform in a single apply: S3, Lambda, API Gateway, DynamoDB, Rekognition, Bedrock, CloudWatch and Amplify Hosting. This is the function. This is the log of the run you just watched, Rekognition and Bedrock in sequence. This is the item it wrote. And this is the photo it read."

---

**Shot 9 · 2:30–2:45**

SCREEN: Ctrl+2, back to the app. Scroll to the bottom, click **Scan another bill**. Click the **MSEDCL, Pune** card. Say nothing for four seconds while the pipeline runs. Speak as the plan appears.

SAY: "Different state, different electricity company, same single photo. Six hundred and fifty units a month. A five and a half kilowatt system. Subsidy capped at seventy-eight thousand. Payback in two point three years."

---

**Shot 10 · 2:45–2:55**

SCREEN: Scroll back to the top of the app so the Bill2Solar logo and the AWS services pill are both visible. Hold. Fade to a plain slide with team names, colleges, and "Environmental Hacks 2026 · Waste & Energy track".

SAY: "One crore homes. One photo each. Bill2Solar, built on AWS in a day for Environmental Hacks. Thank you."

---

## After recording

1. Record the voice-over in one quiet pass while watching the screen recording muted. Re-record single lines if you stumble.
2. In the editor, if the pipeline in shot 3 or 9 takes longer than eight seconds, cut the middle of the wait. Keep the four lit cards on screen for at least four seconds.
3. Add the team slide at the end. Export 1920×1080, 30 fps, H.264, under 200 MB. Watch it once from start to finish.
4. Upload unlisted to YouTube or Drive and open the link in an incognito window to confirm it plays.

## If something goes wrong during the take

- Nothing happens after clicking a specimen for twenty seconds: refresh the tab and click again. The second run is faster.
- "This does not look like an electricity bill" appears: you clicked while the previous upload was still running. Click Scan another bill, wait three seconds, click again.
- The Bedrock card turns to "unavailable" after it was OK earlier: the account's Bedrock regions are used up for now. Use the extra sentence in shot 4 and keep going. Everything else is unaffected.

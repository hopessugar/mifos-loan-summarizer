# GSoC 2026 — Daily Work Log
## Mifos X Loan Summarization with LLMs

**Student:** Vyas Suresh  
**Project:** Smart Contract & Loan Summarization Tool  
**Mentor:** [Mentor Name]

---

## Community Bonding Period

### Week 1 (May 1–7)

**Day 1 · May 1 (Thu)**

Started off by trying to get Fineract running locally with Docker. I was genuinely excited to dig in, but spent most of the afternoon fighting Docker Compose networking issues. Turns out I was using the wrong tenant ID — I kept passing `"mifos"` when it should've been `"default"`. Found the answer in a random community forum thread after about 3 hours of head-scratching. Gave up on local deployment for now and switched to using the demo instance at `demo.mifos.community` so I can actually move forward.

Also went through the Fineract REST API docs and jotted down all the endpoints I'll probably need. Made a small troubleshooting doc while everything was still fresh in my head.

~6 hrs · Honestly pretty frustrated, but at least I understand the architecture better now.

---

**Day 2 · May 2 (Fri)**

Today was about getting API keys sorted. Groq approved instantly, which was nice. Cerebras put me on a waitlist though, so I'll just use Groq as the fallback for now. Set up a HuggingFace account too but their free tier has a 10 req/min limit — not great, but I'll build rate limiting in from the start anyway.

Embarrassing moment: my first Groq API call returned a 401 and I spent way too long debugging before realizing I just forgot to actually set the API key in the headers. Classic.

Got a Google Gemini key as well (wasn't originally planned, but figured more options = better). Also pulled down llama3.1 through Ollama to test locally. Wrote a quick script to verify all the providers work — 3 out of 4 up and running, good enough.

~4 hrs

---

**Day 3 · May 3 (Sat)**

Went through the Mifos X GitHub — issues, PRs, CONTRIBUTING.md, the whole thing. I was trying to match their coding conventions but then realized Mifos X is a Java/Spring Boot project and mine is Python. Wasted a good chunk of time trying to force Java-style patterns into Python before it clicked that this doesn't make sense at all.

Messaged my mentor about it and they said: "Use Python best practices, just keep the API compatible with Mifos." That was a relief. So I'm going with FastAPI conventions + PEP 8 and will just make sure the REST interface plays nice with Mifos.

Sketched out the project structure and the FastAPI routes I'll need.

~3 hrs · Felt way better after my mentor cleared that up.

---

**Day 4 · May 5 (Mon)**

Started writing the technical design doc. Made architecture diagrams, listed all the entity fields I want to extract (started at 35+), designed Pydantic data models. Got a bit carried away though — my first design tried to handle every possible edge case and my mentor told me to chill: "Start simple, add complexity later."

Trimmed the field list down to about 20 core ones: loan amount, interest rate, duration, EMI, fees, etc. The more advanced stuff like collateral details and default event analysis can come in a later iteration. Also did some research on Indian MFI contract formats and found a few sample contracts online that I can test against.

~5 hrs · Feel like I have a much clearer picture of what to build first.

---

**Day 5 · May 6 (Tue)**

Worked on the extraction pipeline design — sequence diagrams, validation strategy, the whole flow. Hit a wall when I started thinking about how to actually verify what the LLM extracts. My initial idea was simple string matching but that obviously won't work for long legal clauses.

Fell down a rabbit hole reading about text similarity methods. Found that Levenshtein distance works well for short values (amounts, percentages) and TF-IDF from scikit-learn could handle semantic matching for longer text. Wrote a quick Python script to test Levenshtein on some sample contract snippets and the results were promising.

~6 hrs · Challenging but I'm genuinely excited about the technical depth here.

---

**Day 6 · May 7 (Wed)**

Finished the design doc... except it was 40 pages long. My mentor's reaction was basically "this is way too much — you're going to change half of it once you start building anyway." Fair point. Spent the rest of the day trimming it down to a 10-page essentials version and moved all the detailed specs into separate implementation notes.

Lesson learned: design docs should be guides, not contracts. I was treating it like I needed to have every answer before writing a single line of code.

~4 hrs

---

### Week 2 (May 8–14)

**Day 7 · May 8 (Thu)**

Had the kick-off call with my mentor — about an hour. Presented my architecture and got some really good (and slightly humbling) feedback. Things I hadn't thought about:

- Prompt injection attacks — hadn't even crossed my mind
- My auth approach was too weak (was just going to use basic auth)
- No rate limiting at all

They shared some resources on LLM security, including Simon Willison's prompt injection stuff which was honestly eye-opening. Spent the evening reading through it and started a security requirements doc.

~3 hrs

---

**Day 8 · May 10 (Sat)**

Deep dive into prompt engineering. Read a bunch of LangChain docs on structured extraction and tested different prompt formats with Groq. This was... humbling. My first prompts produced absolute garbage JSON. The LLM kept wrapping responses in markdown code blocks, or it would just write a paragraph explaining the fields instead of returning JSON.

The fix was being painfully explicit: "Return ONLY valid JSON. No markdown. No explanations." Also adding a JSON schema directly in the prompt and including example outputs helped a lot. Tested about 10 different prompt styles — including examples in the prompt improved accuracy by roughly 30%.

~7 hrs · LLMs are so unpredictable sometimes, it's wild.

---

**Day 9 · May 12 (Mon)**

Ran the same contract through Groq, Gemini, and Ollama to compare them. Every provider has its own quirks:

- Ollama (running locally) takes ~30 seconds per contract. Way too slow for production, but fine for dev.
- Groq is fast but sometimes times out at the 5-second mark. Need retry logic.
- Gemini gives different answers every time because temperature was too high. Setting it to 0.1 fixed that.

Wrote a basic retry decorator with exponential backoff, then ran 50 API calls to get a feel for reliability. Started keeping a provider comparison doc because there are genuinely so many little differences.

~5 hrs

---

**Day 10 · May 13 (Tue)**

Tested edge cases — very short contracts, very long ones, and contracts that mix English and Hindi. Long contracts (3000+ words) blow past Groq's context window, which I knew would be a problem eventually. Hindi text sometimes gets corrupted with encoding issues. And my token counting was wrong because I was using the wrong tokenizer (switched to tiktoken).

Starting to realize this project is more complex than I originally thought, in a good way. Need a chunking strategy for long contracts (will tackle that in Week 3) and Gemini handles Hindi way better than Groq does. Cost-wise I'm looking at about $0.05 per contract with Gemini, which is reasonable.

~6 hrs

---

### Week 3 (May 15–21)

**Day 11 · May 15 (Thu)**

Review session with my mentor. They were a bit concerned about the timeline — I've spent two full weeks on research without writing real code. Their advice: "Start building, iterate as you learn." And honestly, that's probably right. I could research forever but at some point you just have to start coding and figure things out as you go.

Set up the GitHub repo structure, initialized the FastAPI project, and made a concrete coding plan for Week 1. Feeling a bit stressed about the timeline but also ready to actually build something.

~3 hrs

---

## Phase 1 — Coding Period

### Week 1 (May 25–31)

**Day 12 · May 25 (Mon) — CODING STARTS**

Finally writing actual code! Set up the FastAPI skeleton — `main.py`, routers, services, schemas folders. Added a `/health` endpoint. Immediately ran into CORS errors when testing from the browser. Took me an embarrassingly long time (like an hour) to realize I just hadn't added the CORS middleware. Added `CORSMiddleware` with explicit origins and it worked right away.

Also set up environment variables with a `.env` file, added a request logging middleware, and wrote the first test case.

~7 hrs · It feels SO good to finally be writing code.

---

**Day 13 · May 26 (Tue)**

Built the Pydantic request/response schemas — `ContractRequest`, `AnalysisResponse` with all the fields and validation rules. Ran straight into circular import hell between schemas and routers. Python imports can be so frustrating. Fixed it by reorganizing the import order and using `from __future__ import annotations` for forward references. Took about 2 hours to sort out which is annoying but that's Python for you.

~6 hrs

---

**Day 14 · May 27 (Wed)**

Created the `/analyze` endpoint. Getting it to work with mock data was straightforward, but then I tried making actual Groq API calls and everything fell apart. The sync API calls were blocking FastAPI's event loop, which meant the whole application froze when I sent concurrent requests. 

Discovered `asyncio.to_thread()` — you can wrap sync calls in it to make them play nice with async code. Tested with 10 concurrent requests after the fix and it handled them fine. Async programming is tricky but once it clicks, it's really powerful.

~8 hrs (stayed late debugging the async stuff)

---

**Day 15 · May 28 (Thu)**

Started building the frontend with Streamlit because it seemed quick and easy. It was quick and easy... and also kind of ugly. The whole page refreshes on every interaction, you can barely customize the UI, and it looks like every other Streamlit app out there. My mentor suggested looking into React for something more production-ready.

So I spent the afternoon learning React basics and setting up a Vite project with Tailwind. Built my first component (`ContractInput`). Steep learning curve but React makes sense once you get past the initial confusion with JSX.

~9 hrs · Long day. Overwhelmed but I think switching to React was the right call.

---

**Day 16 · May 29 (Fri)**

More React work. Built out the `ContractInput` component properly, added loading states, hooked up API calls with axios. Hit CORS errors again because I forgot to add `localhost:3000` to the backend's allowed origins list. React hooks tripped me up too — I kept causing infinite re-renders because I didn't understand `useEffect` dependency arrays properly. Once I actually read the docs instead of guessing, things started working.

The UI already looks way better than Streamlit did. Tailwind makes styling so much faster.

~7 hrs

---

**Day 17 · May 30 (Sat)**

First end-to-end test: paste a contract → hit the API → see results. It mostly worked! The main issues were a state update bug in the response handler (UI wasn't refreshing), long contracts timing out (increased backend timeout to 60s), and no error messages being shown to the user. Fixed all three.

Added a "Sample Contract" button so I don't have to keep pasting text for testing, and a copy-to-clipboard feature for results. It's starting to feel like a real app.

~6 hrs · Seeing the full flow work for the first time was really satisfying.

---

**Day 18 · May 31 (Sun) — Week 1 wrap-up**

Cleanup day. Refactored the messy code from this week, wrote 15 unit tests, updated the README. Mocking async functions in pytest was a pain — the `pytest-asyncio` config was wrong and `pytest-mock` made things way easier once I found it. All tests passing now.

Also set up a basic GitHub Actions CI pipeline and created a `.env.example` file.

Week 1 done: backend skeleton ✓, frontend working ✓. Behind schedule from the community bonding delays but I have a working demo, which is what matters.

~5 hrs

---

### Week 2 (Jun 1–7)

**Day 19 · Jun 1 (Mon)**

Started building the real extraction prompts. Created `prompts.py` with the system prompt, listed all 20+ fields with instructions, included the JSON schema. First attempt: the LLM responded with "Sure! I'll help you extract those fields..." — that's NOT what I wanted. It's supposed to return JSON, not have a conversation with me.

Tried 5 different prompt variations before landing on something that works: you have to be aggressively explicit ("Return ONLY valid JSON. No explanations."), put the schema at the END of the prompt for emphasis, and include an example extraction.

Tested on 5 sample contracts — about 60% accuracy. Not great. Need more work.

~8 hrs · Prompt engineering is genuinely harder than I expected it to be.

---

**Day 20 · Jun 2 (Tue)**

Iterated on the extraction prompt. Added more detailed field descriptions, edge case examples, and specified units ("interest rate in % per annum, not monthly"). The LLM was confusing "late fee" with "late payment interest" and sometimes hallucinating fees that aren't even in the contract. 

Added disambiguation instructions and a critical rule: "If a value is not mentioned in the contract, return null — DO NOT GUESS." Tested on 10 more contracts and accuracy went up to about 75%. Getting better but still not where it needs to be.

~7 hrs

---

**Day 21 · Jun 3 (Wed)**

Built the JSON parser for LLM responses. The problem is that even with explicit instructions, LLMs sometimes wrap JSON in markdown code blocks or add explanatory text around it. My first attempt used regex to extract the JSON but it was way too brittle — broke on nested objects and arrays.

Ended up with a much simpler approach: find the first `{` and the last `}`, extract that substring, try `json.loads()`. Added error handling and logging for parse failures. Tested on 20 malformed responses and got a 95% success rate. Sometimes the simple solution is the best one.

~5 hrs

---

**Day 22 · Jun 4 (Thu)**

Tried integrating the `instructor` library for structured LLM output. It works great with OpenAI-compatible APIs like Groq, but completely breaks with Ollama and Gemini (different API formats). So now I have this split in the code: use Instructor for Groq/Cerebras, fall back to manual parsing for everything else. It's messy but functional.

Added provider detection logic so the code automatically picks the right path. Documented all the provider-specific quirks because there are a LOT of them.

~6 hrs

---

**Day 23 · Jun 5 (Fri)**

Found 15 real MFI contracts online and ran extraction on all of them. Results: about 40% have some extraction error. Contracts written entirely in Hindi fail badly. Very formal legal language also confuses the models. Added an instruction to "use context from the entire contract, not just the sentence where a value appears" which helped.

Created a proper test dataset with ground truth labels. Current numbers: precision ~85%, recall ~70%. Good enough for an MVP but there's real room for improvement.

~8 hrs · Data collection and testing is tedious but you can't skip it.

---

**Day 24 · Jun 6 (Sat)**

Built the input sanitization layer for prompt injection protection. This was trickier than I thought — my first set of regex patterns was way too aggressive. The phrase "I will repay the loan" was getting flagged as a potential injection because it starts with "I will." Had to narrow the patterns to focus on obvious attack strings like "ignore all previous instructions" while leaving legitimate contract language alone.

Ended up with a test suite of 20 injection attempts — all caught — and zero false positives on real contracts. Also added delimiter-based prompts as a second defense layer.

~6 hrs

---

**Day 25 · Jun 7 (Sun) — Week 2 wrap-up**

Connected the extraction pipeline to the `/analyze` endpoint and tested end-to-end with the frontend. Main issue: API times out on long contracts (40+ seconds) and users have no idea if it's working or frozen. Need to implement segmentation (breaking long contracts into pieces) next week, and add some kind of progress indicator in the UI.

Wrote more tests, updated docs, recorded a quick demo for my mentor.

Week 2 reflection: prompt engineering is way harder than I thought. But extraction is at 85% precision with security baked in, and multi-provider support is working. Not bad.

~5 hrs

---

### Week 3 (Jun 8–14)

**Day 26 · Jun 8 (Mon)**

Started building the segmentation module. The idea is to split long contracts into chunks so each piece fits within the LLM's context window. Wrote `segmenter.py` with header-based segmentation — regex patterns to detect "CLAUSE X", "SCHEDULE Y" type headers.

Problem: my patterns were too specific. "Article 1" wasn't detected because I was only looking for "CLAUSE." Hindi contracts have completely different header formats too. Added more patterns (Article, Section, Part), made the regex case-insensitive. Getting about 70% header detection on my test set of 10 contracts.

~6 hrs

---

**Day 27 · Jun 9 (Tue)**

Added a sentence-based fallback for when header detection fails. Used NLTK for sentence tokenization and a grouping algorithm that keeps chunks under 200 tokens. Hit a deployment gotcha: NLTK's punkt tokenizer data doesn't come pre-installed, so the app would fail on first run. Added `nltk.download('punkt')` to the startup sequence.

Also found that NLTK's sentence splitter isn't great with legal text — it splits in weird places. Bumping the segment size to 300 tokens helped a lot. The fallback chain (try headers first → fall back to sentences) feels solid.

~7 hrs

---

**Day 28 · Jun 10 (Wed)**

Spent the day researching and prototyping semantic chunking — using TF-IDF + cosine similarity to find natural topic boundaries in the text. The first version over-segmented everything (similarity threshold was set too high at 0.8, producing tiny 1-2 sentence chunks). Brought the threshold down to 0.1 and added a minimum chunk size of 50 tokens.

It works noticeably better than sentence-based chunking for unstructured contracts, but it's slower. Made it an optional feature you can toggle via config.

~8 hrs · This was a really deep work session. Semantic chunking is cool but computationally expensive.

---

**Day 29 · Jun 11 (Thu)**

Integrated segmentation into the extraction pipeline and... extraction quality actually got worse. The LLM was losing context between segments — things like "as mentioned above" or "pursuant to Clause 3" become meaningless when you've chopped the document up.

Fix: added 50-token overlap between segments and included segment labels/context in the prompt. Quality came back up, mostly. Mentor said "good enough for MVP" which is fair — there's a fundamental tension between chunking for speed and keeping context for accuracy.

~7 hrs

---

**Day 30 · Jun 12 (Fri)**

Ran segmentation on a bigger set of contracts and collected metrics — segment count, accuracy delta, processing time. Some contracts were producing 50+ segments which is way too many. Very short contracts (single page) don't need segmentation at all.

Added an adaptive strategy: only segment if the contract is longer than 2000 tokens, and cap at 20 segments max (merging the smallest ones if needed). Much more reasonable behavior now.

~6 hrs

---

**Day 31 · Jun 13 (Sat)**

Refactoring and testing day for the segmenter. Added proper docstrings everywhere. Ran pytest-cov and was at 65% coverage which is not great — missing a bunch of edge cases. Added tests for empty contracts, Unicode text, special characters, and got coverage up to 82%.

~5 hrs

---

**Day 32 · Jun 14 (Sun) — Week 3 wrap-up**

Full integration test: segmentation + extraction pipeline on 20 contracts. One nasty surprise: memory usage spiked to 600MB when using semantic chunking. That's not sustainable for production. Made semantic chunking opt-in (off by default) and recommended simple sentence-based for most users. Can optimize the memory issue later if needed.

Week 3 done. Three segmentation methods built (header, sentence, semantic). Learned a lot about the tradeoff between quality and performance.

~6 hrs

---

### Week 4 (Jun 15–21) — the hard week

**Day 33 · Jun 15 (Mon)**

Started building the validation layer — the part that checks whether the LLM's extractions actually match what's in the contract. Wrote `validator.py` and tried exact string matching first. Immediately failed: "Rs. 100000" vs "Rs. 1,00,000" vs "100000 INR" are all the same value but string matching says they're different. 70% of valid extractions were getting flagged as unverified.

Switched to fuzzy matching with Levenshtein distance and a threshold of 0.80. Way better results.

~7 hrs · Validation is turning out to be harder than extraction itself.

---

**Day 34 · Jun 16 (Tue) — the big failure day**

This was probably the worst day of the project so far. I was implementing the EMI verification calculator (to check if the LLM's extracted EMI matches the math). Used regular Python floats. Rs. 8,885 was coming out as 8884.999999999998 or sometimes 8885.0000000001. My consistency checker was flagging correct values as wrong because of floating point errors.

I spent FOUR HOURS debugging this before I realized the root cause was floating point arithmetic itself. Switched everything to Python's `Decimal` module and all the errors disappeared immediately. Then had to go back and rewrite the entire financial calculator module to use Decimal throughout.

**Lesson I will never forget: do not use floats for money.** Ever. Use `Decimal` in Python or `BigDecimal` in Java. This is non-negotiable for financial applications.

~10 hrs · Exhausted. But that's a lesson I'm glad I learned now rather than in production.

---

**Day 35 · Jun 17 (Wed)**

Implemented both the reducing balance and flat rate EMI formulas. The tricky part: contracts usually don't specify which method they use. Using the wrong formula can give you a 15% error in the calculation.

Solution: try both formulas, see which one is closer to the stated EMI, and report which method matched. Validated my results against a couple of online EMI calculators and got exact matches, so the math is right.

~7 hrs

---

**Day 36 · Jun 18 (Thu)**

Built the confidence scoring system. Combines text similarity, regex match strength, and keyword proximity into a single score. First version was useless — every single field scored between 0.85 and 0.95 regardless of actual confidence. Couldn't distinguish "I'm very sure about this" from "this is a rough guess."

Tweaked the weights (40% similarity, 35% keyword, 25% regex) and added a penalty for fields where no source clause could be found in the original text. Score distribution is much better now. Also created named confidence levels: `exact_match`, `pattern_match`, `inference`, `guess`.

~6 hrs

---

**Day 37 · Jun 19 (Fri)**

Built the risk analysis system. First version was terrible — all loans scored between 2 and 3 on a 0–10 scale. Not helpful. Looked up RBI guidelines on interest rates to set proper thresholds: above 48% is predatory, above 36% is very high risk, etc. Also added multiple risk factors beyond just interest rate (penalties, collateral requirements, etc.).

~8 hrs

---

**Day 38 · Jun 20 (Sat) — breakthrough day**

Added default clause analysis. This is where the app gets really useful for borrowers. Initially I was treating ALL default triggers (things that let the lender call the loan) as red flags, but my mentor pointed out that some are perfectly standard and protective — like "if you miss 3 payments" or "in case of fraud." Those are normal.

What's NOT normal (and is genuinely predatory) is stuff like "at lender's sole discretion" or "if borrower changes employment." So I split them into two lists: standard vs. predatory. Only the predatory ones increase the risk score. Spent the evening researching consumer protection laws and building out the detection patterns.

This feature is honestly why this project matters — it can flag the clauses that take advantage of borrowers who don't have legal expertise.

~7 hrs

---

**Day 39 · Jun 21 (Sun) — Week 4 wrap-up**

Wrote comprehensive test scenarios: standard loan, predatory loan, edge cases — 8 scenarios total. Three were failing due to math tolerance being too strict and risk score weights being off. Fixed both and everything passes now.

Also added specific tests for hallucination prevention and fee disambiguation (making sure the system doesn't confuse late fees with processing fees, etc.).

Week 4 was easily the hardest week. The Decimal lesson on Day 34 was brutal. But the validation layer is complete now with five different types of checks, and the risk analysis actually catches predatory patterns. This week is what turns the project from a demo into something genuinely useful.

~9 hrs

---

### Week 5 (Jun 22–28) — final push

**Day 40 · Jun 22 (Mon)**

Built the summary generator — `summariser.py`. Takes the validated extraction data and uses the LLM to produce a plain-language summary for borrowers. First version was generic and full of jargon. Revised the prompt to be borrower-focused, highlight warnings explicitly, and use simpler language. Tested readability with an online tool and it came in at about an 8th-grade reading level, which is good for a general audience.

~6 hrs

---

**Day 41 · Jun 23 (Tue)**

Added Hindi language support for summaries. This turned out to be simpler than expected once I figured out the right provider — Gemini handles Hindi well, Groq produces gibberish, and Ollama is even worse. So I added language-based provider selection: if the user requests Hindi, route to Gemini automatically.

Tested with mixed English-Hindi contracts and the summaries come out in the requested language correctly.

~5 hrs

---

**Day 42 · Jun 24 (Wed)**

Built the WhatsApp export format. The idea is that borrowers can share a compact loan summary via WhatsApp to get advice from family or friends. First version was 450 characters (too long for a single message). Cut it down to the essentials — amount, rate, EMI, total repayment, risk level — with emoji for quick scanning. Fits in one WhatsApp message now.

Tested on 3 different phones across WhatsApp, Telegram, and Signal. Works great. Small feature but very practical for Indian users.

~4 hrs

---

**Day 43 · Jun 25 (Thu) — Docker day from hell**

Created Dockerfiles for backend and frontend plus docker-compose.yml. Everything that could go wrong did go wrong:

1. Backend build failed because NLTK data wasn't being downloaded during the build step
2. Frontend build failed because of a Node version mismatch  
3. Containers couldn't talk to each other (networking)

Spent the ENTIRE day fixing this. Backend: added NLTK download to the Dockerfile. Frontend: pinned Node 20. Networking: switched to docker-compose bridge mode. Also added multi-stage builds for the frontend (smaller image), non-root users for security, and health checks.

~11 hrs · Should have set up Docker earlier instead of leaving it to the last week.

---

**Day 44 · Jun 26 (Fri)**

Set up CI/CD with GitHub Actions — test job, lint job, build job, pytest with coverage. Of course, tests that pass perfectly on my machine failed in CI. Missing environment variables. NLTK data download failing again. Fixed both by adding explicit setup steps in the workflow.

Also integrated Codecov and added Bandit for security scanning.

~8 hrs · Having CI/CD feels really professional though.

---

**Day 45 · Jun 27 (Sat)**

Ran the full test suite — 95 tests. Found one that was failing intermittently due to an async race condition, and another that was leaking memory in long-running tests. Took about 4 hours to track down and fix both (proper async cleanup + fixing test teardown).

Final coverage: 85%. All tests stable and passing consistently.

~9 hrs

---

**Day 46 · Jun 28 (Sun) — Phase 1 complete! 🎉**

Documentation day. Updated the README with full setup instructions (quick start, manual setup, Docker, etc.), added a table of contents because it was getting long, wrote API docs with examples, recorded a demo video.

~7 hrs

---

## Phase 1 Summary

### What got done

All planned deliverables are complete, plus a few bonus features (semantic chunking, Hindi support, WhatsApp export). 95 tests passing at 85% coverage. Production deployment working with Docker + CI/CD. Security was built in from the start rather than bolted on at the end.

### Biggest failures and what I learned from them

1. **Floating point precision disaster (Day 34):** Used `float` for money calculations. Never again. `Decimal` module exists for a reason.
2. **Async blocking (Day 14):** LLM calls froze the event loop until I learned about `asyncio.to_thread()`.
3. **Over-engineering the design doc (Day 6):** Wrote 40 pages before any code. Design docs should be living guides, not exhaustive specifications.
4. **Docker hell (Day 43):** 11 hours of debugging. Should have containerized earlier when the project was simpler.
5. **Overly strict validation (Day 33):** Exact string matching flags correct results as wrong. Fuzzy matching with Levenshtein was the answer.

### Key technical decisions and why

- **React over Streamlit:** Streamlit was faster to set up but React gives a production-quality UI that we can actually deploy.
- **Decimal for all money math:** Financial precision isn't optional. Learned this the painful way.
- **Multi-provider support:** If one LLM provider goes down or doesn't support a feature (like Hindi), we can fall back to another.
- **5-layer validation:** Extraction without verification is just guessing. Built in text matching, math consistency checks, confidence scoring, hallucination detection, and cross-reference validation.
- **Semantic chunking as opt-in:** Cool feature but uses too much memory (600MB). Default to simple sentence-based chunking.

### What I'd do differently next time

1. Start coding earlier — 3 weeks of pure research was too long
2. Test with real contract data from day 1 instead of synthetic examples
3. Set up Docker in week 1, not week 5
4. Ask my mentor for help sooner instead of debugging alone for hours

### Ready for Phase 2

Fineract integration path is clear, architecture is proven, test coverage is solid, deployment is automated. Ready to move on to production integration.

---

## Mentor Sign-off

**Mentor Comments:**  
_[Space for mentor feedback]_

**Date:** June 28, 2026

---

**Next:** Phase 2 — Fineract integration, batch processing, admin dashboard

# GSoC 2026 — Daily Work Log
## Mifos X Loan Summarization with LLMs

**Student:** Silky Vyas  
**Project:** Smart Contract & Loan Summarization Tool  


---

## Community Bonding Period

### Week 1 (May 1–7)

**Day 1 · May 1 (Thu)**

Started off by trying to get Fineract running locally with Docker. I was genuinely excited to dig in, but spent most of the afternoon fighting Docker Compose networking issues. Turns out I was using the wrong tenant ID, I kept passing `"mifos"` when it should've been `"default"`. Found the answer in a random community forum thread after about 3 hours of head-scratching. Gave up on local deployment for now and switched to using the demo instance at `demo.mifos.community` so I can actually move forward.

Also went through the Fineract REST API docs and jotted down all the endpoints I'll probably need. Made a small troubleshooting doc while everything was still fresh in my head.

~4 hrs · Honestly pretty frustrated, but at least I understand the architecture better now.

---

**Day 2 · May 2 (Fri)**

Today was about getting API keys sorted. Groq approved instantly, which was nice. Cerebras put me on a waitlist though, so I'll just use Groq as the fallback for now. Set up a HuggingFace account too but their free tier has a 10 req/min limit, not great, but I'll build rate limiting in from the start anyway.

Embarrassing moment: my first Groq API call returned a 401 and I spent way too long debugging before realizing I just forgot to actually set the API key in the headers. Classic.

Got a Google Gemini key as well (wasn't originally planned, but figured more options = better). Also pulled down llama3.1 through Ollama to test locally. Wrote a quick script to verify all the providers work — 3 out of 4 up and running, good enough.

~3 hrs

---

**Day 3 · May 3 (Sat)**

Went through the Mifos X GitHub — issues, PRs, CONTRIBUTING.md, the whole thing. I was trying to match their coding conventions but then realized Mifos X is a Java/Spring Boot project and mine is Python. Wasted a good chunk of time trying to force Java-style patterns into Python before it clicked that this doesn't make sense at all.

Sketched out the project structure and the FastAPI routes I'll need.

~3 hrs
---

**Day 4 · May 5 (Mon)**

Started writing the technical design doc. Made architecture diagrams, listed all the entity fields I want to extract (started at 35+), designed Pydantic data models. Got a bit carried away though, my first design tried to handle every possible edge case and my mentor told me to chill: "Start simple, add complexity later."

Trimmed the field list down to about 20 core ones, loan amount, interest rate, duration, EMI, fees, etc. The more advanced stuff like collateral details and default event analysis can come in a later iteration. Also did some research on Indian MFI contract formats and found a few sample contracts online that I can test against.

~5 hrs · Feel like I have a much clearer picture of what to build first.

---

**Day 5 · May 6 (Tue)**

Worked on the extraction pipeline design, sequence diagrams, validation strategy, the whole flow. Hit a wall when I started thinking about how to actually verify what the LLM extracts. My initial idea was simple string matching but that obviously won't work for long legal clauses.

Fell down a rabbit hole reading about text similarity methods. Found that Levenshtein distance works well for short values (amounts, percentages) and TF-IDF from scikit-learn could handle semantic matching for longer text. Wrote a quick Python script to test Levenshtein on some sample contract snippets and the results were promising.

~6 hrs · Challenging but I'm genuinely excited about the technical depth here.

---

**Day 6 · May 7 (Wed)**

Finished the design doc... except it was 40 pages long. Spent the rest of the day trimming it down to a  simplified version and moved all the detailed specs into separate implementation notes.

Lesson learned: design docs should be guides, not contracts. I was treating it like I needed to have every answer before writing a single line of code.

~4 hrs

---

### Week 2 (May 8–14)

**Day 7 · May 8 (Thu)**

Had the kick-off call with my mentor. Presented my architecture and got some really good (and slightly humbling) feedback.

Read some resources on LLM security, including Simon Willison's prompt injection stuff which was honestly eye-opening. Spent the evening reading through it and started a security requirements doc.

~3 hrs

---

**Day 8 · May 10 (Sat)**

Deep dive into prompt engineering. Read a bunch of LangChain docs on structured extraction and tested different prompt formats with Groq. This was... humbling. My first prompts produced absolute garbage JSON. The LLM kept wrapping responses in markdown code blocks, or it would just write a paragraph explaining the fields instead of returning JSON.

The fix was being painfully explicit: "Return ONLY valid JSON. No markdown. No explanations." Also adding a JSON schema directly in the prompt and including example outputs helped a lot. Tested about 10 different prompt styles including examples in the prompt improved accuracy by roughly 30%.

~5 hrs · LLMs are so unpredictable sometimes, it's wild.

---

**Day 9 · May 12 (Mon)**

Ran the same contract through Groq, Gemini, and Ollama to compare them. Every provider has its own quirks:

- Ollama (running locally) didnt worked due to hardware constraints.
- Groq is fast but sometimes times out at the 5-second mark. Need retry logic.
- Gemini gives different answers every time because temperature was too high. Setting it to 0.1 fixed that.

Wrote a basic retry decorator with exponential backoff, then ran 50 API calls to get a feel for reliability. Started keeping a provider comparison doc because there are genuinely so many little differences.

~5 hrs

---

**Day 10 · May 13 (Tue)**

Tested edge cases — very short contracts, very long ones, and contracts that mix English and Hindi. Long contracts (3000+ words) blow past Groq's context window, which I knew would be a problem eventually.  And my token counting was wrong because I was using the wrong tokenizer (switched to tiktoken).

Starting to realize this project is more complex than I originally thought, in a good way. Need a chunking strategy for long contracts (will tackle that in Week 3) and Gemini handles Hindi way better than Groq does. 

~6 hrs

---

### Week 3 (May 15–21)

**Day 11 · May 15 (Thu)**

Set up the GitHub repo structure, initialized the FastAPI project, and made a concrete coding plan for Week 1. Feeling a bit stressed about the timeline but also ready to actually build something.

~2 hrs

---

## Phase 1 — Coding Period

### Week 1 (May 25–31)

**Day 12 · May 25 (Mon) — CODING STARTS**

Finally writing actual code! Set up the FastAPI skeleton - `main.py`, routers, services, schemas folders. Added a `/health` endpoint. Immediately ran into CORS errors when testing from the browser. Took me an embarrassingly long time (like an hour) to realize I just hadn't added the CORS middleware. Added `CORSMiddleware` with explicit origins and it worked right away.

Also set up environment variables with a `.env` file, added a request logging middleware, and wrote the first test case.

~4 hrs · It feels SO good to finally be writing code.

---

**Day 13 · May 26 (Tue)**

Built the Pydantic request/response schemas - `ContractRequest`, `AnalysisResponse` with all the fields and validation rules. Ran straight into circular import hell between schemas and routers. Python imports can be so frustrating. Fixed it by reorganizing the import order and using `from __future__ import annotations` for forward references. Took about 2 hours to sort out which is annoying but that's Python for you.

~3 hrs

---

**Day 14 · May 27 (Wed)**

Created the `/analyze` endpoint. Getting it to work with mock data was straightforward, but then I tried making actual Groq API calls and everything fell apart. The sync API calls were blocking FastAPI's event loop, which meant the whole application froze when I sent concurrent requests. 

Discovered `asyncio.to_thread()` - you can wrap sync calls in it to make them play nice with async code. Tested with 10 concurrent requests after the fix and it handled them fine. Async programming is tricky but once it clicks, it's really powerful.

~6 hrs (stayed late debugging the async stuff)

---

**Day 15 · May 28 (Thu)**

So I spent the afternoon learning React basics and setting up a Vite project with Tailwind. Built my first component (`ContractInput`). Steep learning curve but React makes sense once you get past the initial confusion with JSX.

~4 hrs  

---

**Day 16 · May 29 (Fri)**

More React work. Built out the `ContractInput` component properly, added loading states, hooked up API calls with axios. Hit CORS errors again because I forgot to add `localhost:3000` to the backend's allowed origins list. React hooks tripped me up too, I kept causing infinite re-renders because I didn't understand `useEffect` dependency arrays properly. Once I actually read the docs instead of guessing, things started working.

The UI already looks way better. Tailwind makes styling so much faster.

~4 hrs

---

**Day 17 · May 30 (Sat)**

First end-to-end test: paste a contract → hit the API → see results. It mostly worked! The main issues were a state update bug in the response handler (UI wasn't refreshing), long contracts timing out (increased backend timeout to 60s), and no error messages being shown to the user. Fixed all three.

Added a "Sample Contract" button so I don't have to keep pasting text for testing, and a copy-to-clipboard feature for results. It's starting to feel like a real app.

~3 hrs · Seeing the full flow work for the first time was really satisfying.

---

**Day 18 · May 31 (Sun) — Week 1 wrap-up**

Cleanup day. Refactored the messy code from this week, wrote 15 unit tests, updated the README. Mocking async functions in pytest was a pain, the `pytest-asyncio` config was wrong and `pytest-mock` made things way easier once I found it. All tests passing now.

Also set up a basic GitHub Actions CI pipeline and created a `.env.example` file.

Week 1 done: backend skeleton ✓, frontend working ✓. Behind schedule from the community bonding delays but I have a working demo, which is what matters.

~5 hrs

---

### Week 2 (Jun 1–7)

**Day 19 · Jun 1 (Mon)**

Started building the real extraction prompts. Created `prompts.py` with the system prompt, listed all 20+ fields with instructions, included the JSON schema. First attempt: the LLM responded with "Sure! I'll help you extract those fields..." — that's NOT what I wanted. It's supposed to return JSON, not have a conversation with me.

Tried 5 different prompt variations before landing on something that works: you have to be aggressively explicit ("Return ONLY valid JSON. No explanations."), put the schema at the END of the prompt for emphasis, and include an example extraction.

Tested on 5 sample contracts — about 60% accuracy. Not great. Need more work.

~5 hrs · Prompt engineering is genuinely harder than I expected it to be.

---

**Day 20 · Jun 2 (Tue)**

Iterated on the extraction prompt. Added more detailed field descriptions, edge case examples, and specified units ("interest rate in % per annum, not monthly"). The LLM was confusing "late fee" with "late payment interest" and sometimes hallucinating fees that aren't even in the contract. 

Added disambiguation instructions and a critical rule: "If a value is not mentioned in the contract, return null  DO NOT GUESS." Tested on 10 more contracts and accuracy went up to about 75%. Getting better but still not where it needs to be.

~6 hrs

---

**Day 21 · Jun 3 (Wed)**

Built the JSON parser for LLM responses. The problem is that even with explicit instructions, LLMs sometimes wrap JSON in markdown code blocks or add explanatory text around it. My first attempt used regex to extract the JSON but it was way too brittle — broke on nested objects and arrays.

Ended up with a much simpler approach: find the first `{` and the last `}`, extract that substring, try `json.loads()`. Added error handling and logging for parse failures. Tested on 20 malformed responses and got a 95% success rate. Sometimes the simple solution is the best one.

~5 hrs

---

**Day 22 · Jun 4 (Thu)**

Tried integrating the `instructor` library for structured LLM output. It works great with OpenAI-compatible APIs like Groq, but completely breaks with Ollama and Gemini (different API formats). So now I have this split in the code: use Instructor for Groq/Cerebras, fall back to manual parsing for everything else. It's messy but functional.

Added provider detection logic so the code automatically picks the right path. Documented all the provider-specific quirks because there are a LOT of them.

~4 hrs

---

**Day 23 · Jun 5 (Fri)**

Found 15 real MFI contracts online and ran extraction on all of them. Results: about 40% have some extraction error. Contracts written entirely in Hindi fail badly. Very formal legal language also confuses the models. Added an instruction to "use context from the entire contract, not just the sentence where a value appears" which helped.

Created a proper test dataset with ground truth labels. Current numbers: precision ~85%, recall ~70%. Good enough for an MVP but there's real room for improvement.

~6 hrs · Data collection and testing is tedious but you can't skip it.

---

**Day 24 · Jun 6 (Sat)**

Built the input sanitization layer for prompt injection protection. This was trickier than I thought — my first set of regex patterns was way too aggressive. The phrase "I will repay the loan" was getting flagged as a potential injection because it starts with "I will." Had to narrow the patterns to focus on obvious attack strings like "ignore all previous instructions" while leaving legitimate contract language alone.

Ended up with a test suite of 20 injection attempts, all caught, and zero false positives on real contracts. Also added delimiter-based prompts as a second defense layer.

~5 hrs

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

~4 hrs

---

**Day 27 · Jun 9 (Tue)**

Added a sentence-based fallback for when header detection fails. Used NLTK for sentence tokenization and a grouping algorithm that keeps chunks under 200 tokens. Hit a deployment gotcha: NLTK's punkt tokenizer data doesn't come pre-installed, so the app would fail on first run. Added `nltk.download('punkt')` to the startup sequence.

Also found that NLTK's sentence splitter isn't great with legal text. it splits in weird places. Bumping the segment size to 300 tokens helped a lot. The fallback chain (try headers first → fall back to sentences) feels solid.

~5 hrs

---

**Day 28 · Jun 10 (Wed)**

Spent the day researching and prototyping semantic chunking using TF-IDF + cosine similarity to find natural topic boundaries in the text. The first version over-segmented everything (similarity threshold was set too high at 0.8, producing tiny 1-2 sentence chunks). Brought the threshold down to 0.1 and added a minimum chunk size of 50 tokens.

It works noticeably better than sentence-based chunking for unstructured contracts, but it's slower. Made it an optional feature you can toggle via config.

~5 hrs · Semantic chunking is cool but computationally expensive.

---

**Day 29 · Jun 11 (Thu)**

Integrated segmentation into the extraction pipeline and... extraction quality actually got worse. The LLM was losing context between segments — things like "as mentioned above" or "pursuant to Clause 3" become meaningless when you've chopped the document up.

Fix: added 50-token overlap between segments and included segment labels/context in the prompt. Quality came back up, mostly. Mentor said "good enough for MVP" which is fair — there's a fundamental tension between chunking for speed and keeping context for accuracy.

~4 hrs

---

**Day 30 · Jun 12 (Fri)**

Ran segmentation on a bigger set of contracts and collected metrics segment count, accuracy delta, processing time. Some contracts were producing 50+ segments which is way too many. Very short contracts (single page) don't need segmentation at all.

Added an adaptive strategy: only segment if the contract is longer than 2000 tokens, and cap at 20 segments max (merging the smallest ones if needed). Much more reasonable behavior now.

~3 hrs

---

**Day 31 · Jun 13 (Sat)**

Refactoring and testing day for the segmenter. Added proper docstrings everywhere. Ran pytest-cov and was at 65% coverage which is not great missing a bunch of edge cases. Added tests for empty contracts, Unicode text, special characters, and got coverage up to 82%.

~5 hrs

---

**Day 32 · Jun 14 (Sun) — Week 3 wrap-up**

Full integration test: segmentation + extraction pipeline on 20 contracts. One nasty surprise: memory usage spiked to 600MB when using semantic chunking. That's not sustainable for production. Made semantic chunking opt-in (off by default) and recommended simple sentence-based for most users. Can optimize the memory issue later if needed.

Week 3 done. Three segmentation methods built (header, sentence, semantic). Learned a lot about the tradeoff between quality and performance.

~3 hrs

---

### Week 4 (Jun 15–21) — the hard week

**Day 33 · Jun 15 (Mon)**

Started building the validation layer — the part that checks whether the LLM's extractions actually match what's in the contract. Wrote `validator.py` and tried exact string matching first. Immediately failed: "Rs. 100000" vs "Rs. 1,00,000" vs "100000 INR" are all the same value but string matching says they're different. 70% of valid extractions were getting flagged as unverified.

Switched to fuzzy matching with Levenshtein distance and a threshold of 0.80. Way better results.

~5 hrs · Validation is turning out to be harder than extraction itself.

---

**Day 34 · Jun 16 (Tue) — the big failure day**

This was probably the worst day of the project so far. I was implementing the EMI verification calculator (to check if the LLM's extracted EMI matches the math). Used regular Python floats. Rs. 8,885 was coming out as 8884.999999999998 or sometimes 8885.0000000001. My consistency checker was flagging correct values as wrong because of floating point errors.

I spent FOUR HOURS debugging this before I realized the root cause was floating point arithmetic itself. Switched everything to Python's `Decimal` module and all the errors disappeared immediately. Then had to go back and rewrite the entire financial calculator module to use Decimal throughout.

**Lesson I will never forget: do not use floats for money.** Ever. Use `Decimal` in Python. This is non-negotiable for financial applications.

~5 hrs · Exhausted. But that's a lesson I'm glad I learned now rather than in production.

---

**Day 35 · Jun 17 (Wed)**

Implemented both the reducing balance and flat rate EMI formulas. The tricky part: contracts usually don't specify which method they use. Using the wrong formula can give you a 15% error in the calculation.

Solution: try both formulas, see which one is closer to the stated EMI, and report which method matched. Validated my results against a couple of online EMI calculators and got exact matches, so the math is right.

~3 hrs

---

**Day 36 · Jun 18 (Thu)**

Built the confidence scoring system. Combines text similarity, regex match strength, and keyword proximity into a single score. First version was useless — every single field scored between 0.85 and 0.95 regardless of actual confidence. Couldn't distinguish "I'm very sure about this" from "this is a rough guess."

Tweaked the weights (40% similarity, 35% keyword, 25% regex) and added a penalty for fields where no source clause could be found in the original text. Score distribution is much better now. Also created named confidence levels: `exact_match`, `pattern_match`, `inference`, `guess`.

~4 hrs

---

**Day 37 · Jun 19 (Fri)**

Built the risk analysis system. First version was terrible, all loans scored between 2 and 3 on a 0–10 scale. Not helpful. Looked up RBI guidelines on interest rates to set proper thresholds: above 48% is predatory, above 36% is very high risk, etc. Also added multiple risk factors beyond just interest rate (penalties, collateral requirements, etc.).

~4 hrs

---

**Day 38 · Jun 20 (Sat) — breakthrough day**

Added default clause analysis. This is where the app gets really useful for borrowers. Initially I was treating ALL default triggers (things that let the lender call the loan) as red flags, but my mentor pointed out that some are perfectly standard and protective, like "if you miss 3 payments" or "in case of fraud." Those are normal.

What's NOT normal (and is genuinely predatory) is stuff like "at lender's sole discretion" or "if borrower changes employment." So I split them into two lists: standard vs. predatory. Only the predatory ones increase the risk score. Spent the evening researching consumer protection laws and building out the detection patterns.

This feature is honestly why this project matters — it can flag the clauses that take advantage of borrowers who don't have legal expertise.

~5 hrs

---

**Day 39 · Jun 21 (Sun) — Week 4 wrap-up**

Wrote comprehensive test scenarios: standard loan, predatory loan, edge cases — 8 scenarios total. Three were failing due to math tolerance being too strict and risk score weights being off. Fixed both and everything passes now.

Also added specific tests for hallucination prevention and fee disambiguation (making sure the system doesn't confuse late fees with processing fees, etc.).

Week 4 was easily the hardest week. The Decimal lesson on Day 34 was brutal. But the validation layer is complete now with five different types of checks, and the risk analysis actually catches predatory patterns. This week is what turns the project from a demo into something genuinely useful.

~2 hrs

---

### Week 5 (Jun 22–28) — final push

**Day 40 · Jun 22 (Mon)**

Built the summary generator — `summariser.py`. Takes the validated extraction data and uses the LLM to produce a plain-language summary for borrowers. First version was generic and full of jargon. Revised the prompt to be borrower-focused, highlight warnings explicitly, and use simpler language. Tested readability with an online tool and it came in at about an 8th-grade reading level, which is good for a general audience.

~4 hrs

---

**Day 41 · Jun 23 (Tue)**

Added Hindi language support for summaries. This turned out to be simpler than expected once I figured out the right provider, Gemini handles Hindi well, Groq produces gibberish, and Ollama is even worse. So I added language-based provider selection: if the user requests Hindi, route to Gemini automatically.

Tested with mixed English-Hindi contracts and the summaries come out in the requested language correctly.

~3 hrs

---

**Day 42 · Jun 24 (Wed)**

Built the WhatsApp export format. The idea is that borrowers can share a compact loan summary via WhatsApp to get advice from family or friends. First version was 450 characters (too long for a single message). Cut it down to the essentials amount, rate, EMI, total repayment, risk level — with emoji for quick scanning. Fits in one WhatsApp message now.

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

~5 hrs · Having CI/CD feels really professional though.

---

**Day 45 · Jun 27 (Sat)**

Ran the full test suite — 95 tests. Found one that was failing intermittently due to an async race condition, and another that was leaking memory in long-running tests. Took about 4 hours to track down and fix both (proper async cleanup + fixing test teardown).

Final coverage: 85%. All tests stable and passing consistently.

~5 hrs

---

**Day 46 · Jun 28 (Sun) — Phase 1 complete! 🎉**

Documentation day. Updated the README with full setup instructions (quick start, manual setup, Docker, etc.), added a table of contents because it was getting long, wrote API docs with examples, recorded a demo video.

~4 hrs

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

- **Decimal for all money math:** Financial precision isn't optional. Learned this the painful way.
- **Multi-provider support:** If one LLM provider goes down or doesn't support a feature (like Hindi), we can fall back to another.
- **5-layer validation:** Extraction without verification is just guessing. Built in text matching, math consistency checks, confidence scoring, hallucination detection, and cross-reference validation.
- **Semantic chunking as opt-in:** Cool feature but uses too much memory (600MB). Default to simple sentence-based chunking.

### What I'd do differently next time

1. Start coding earlier — 3 weeks of pure research was too long
2. Test with real contract data from day 1 instead of synthetic examples
3. Set up Docker in week 1, not week 5
4. Ask my mentor for help sooner instead of debugging alone for hours

---

## Phase 2 — Coding Period (Fineract Integration)

### Week 6 (Jun 29 – Jul 4)

**Day 47 · Jun 29 (Mon) — PHASE 2 STARTS**

Phase 2 focus: integrate directly with Apache Fineract / Mifos X. Up until now the app only took pasted text or uploaded files — but the real value for Mifos is pulling loan product data straight from their platform.

Spent the day going through the Fineract REST API docs properly this time (not just skimming like I did in the community bonding period). The key endpoints I need: `GET /loanproducts` to list all products and `GET /loanproducts/{id}` to fetch the full details of a specific one. The response JSON is massive — nested objects everywhere. Currency is a dict with `code`, `name`, `displaySymbol`. Interest rate has `interestRatePerPeriod` AND `annualInterestRate` (different fields!). Charges are an array with their own nested type objects.

Made notes on every field I'll need to map to our existing `LoanAgreementSchema`. There are a LOT of Fineract-specific fields (grace periods, arrears tolerance, transaction processing strategies) that don't have direct equivalents in our schema. Need to figure out what to do with those.

~5 hrs · Feeling that "staring at docs all day" fatigue but this needs to be right.

---

**Day 48 · Jun 30 (Tue)**

Started building the Fineract configuration layer. Added `FINERACT_URL`, `FINERACT_USER`, `FINERACT_PASSWORD`, `FINERACT_TENANT`, and `FINERACT_SSL_VERIFY` to the settings in `config.py`. The Fineract API uses HTTP Basic Auth with a tenant header, which is different from the bearer token auth I'm used to.

Got the SSL verification config working — three modes: `True` (default, use system certs), a custom CA bundle path (for self-signed certs in dev), or `False` (disabled, dev only). Added a hard block in `config.py` so SSL verification CANNOT be disabled in production. Learned this from the security reading during community bonding — you'd be shocked how many open-source projects ship with `verify=False` hardcoded.

Tested against the Mifos demo instance at `demo.mifos.community` and got my first successful 200 response. The tenant ID is `default`, not `mifos` — I made the exact same mistake as Day 1. At least this time it only took 10 minutes to figure out.

~4 hrs

---

**Day 49 · Jul 1 (Wed)**

Built the core of `fineract_service.py`. Started with `_auth_headers()` — generates the Basic Auth token from username:password and includes the `Fineract-Platform-TenantId` header. Then built a shared `httpx.AsyncClient` with connection pooling (`_get_fineract_client()`). The idea is to reuse connections instead of creating a new one for every API call — way more efficient when the frontend is making multiple requests.

Set up the client with sensible defaults: 30-second read timeout, 10-second connect timeout, max 5 keepalive connections, max 10 total connections. Hit a bug where the global client was `None` on the second call because I was recreating it every time instead of caching it. Switched to a module-level global with a lazy init pattern.

Also wrote `_get_ssl_config()` to handle the three SSL modes. Had to add a `FileNotFoundError` check for when someone configures a CA bundle path that doesn't exist — better to fail loud than silently skip verification.

~5 hrs

---

**Day 50 · Jul 2 (Thu)**

Implemented `list_loan_products()` and `get_product_as_text()`. The list endpoint is straightforward — call the API, extract just `id` and `name` from each product. The text conversion is where it gets tricky.

Wrote `_product_to_text()` which takes the raw Fineract JSON and converts it to human-readable text that our extraction pipeline can understand. The problem: Fineract wraps values in nested dicts sometimes (`{'defaultValue': 50000}`) and sometimes gives plain numbers (`50000`). Had to write a `_safe_get()` helper that handles both formats.

Tested with the demo instance — there are about 15 loan products on the demo server. The text conversion looked decent but I noticed the interest rate frequency wasn't being shown correctly. `interestRatePeriodFrequencyType` is a whole nested object with `id`, `code`, and `value`. You have to dig into `.value` to get "Per year" vs "Per month".

~4 hrs

---

**Day 51 · Jul 3 (Fri)**

Built the `/loanproducts` API router with three endpoints:

1. `GET /loanproducts` — list all products from Fineract
2. `GET /loanproducts/{product_id}` — get a specific product as text
3. `POST /loanproducts/refresh` — invalidate the cache and fetch fresh data

The error handling was the interesting part. Fineract can return 401 (bad credentials), 404 (product doesn't exist), 503 (server down), or just time out entirely. Each needs a different user-facing error message. I mapped them all to appropriate HTTP status codes with clear messages like "Authentication failed with Mifos X. Check FINERACT_USER and FINERACT_PASSWORD." instead of just forwarding the raw error.

Also added API key auth (`Depends(verify_api_key)`) to all the Fineract endpoints, same as the analysis endpoints.

~4 hrs

---

**Day 52 · Jul 4 (Sat)**

Tested the full flow: frontend → backend → Fineract demo → response. Mostly worked! But the product text wasn't detailed enough for our extraction pipeline to work well. The LLM was getting confused because the text just said "interest rate: 18" without specifying annual vs monthly, or "charges: Processing Fee — 500" without saying if that's flat or percentage.

Went back and enhanced `_product_to_text()` to include interest type (reducing vs flat), calculation period, frequency labels, charge calculation types, grace periods, and amortization type. The text went from ~5 lines to ~15 lines per product, and extraction quality improved noticeably.

Then had an "aha" moment: why am I even sending this text through the LLM for extraction? Fineract already gives me structured JSON with exact values. The LLM extraction step is UNNECESSARY for Fineract products — it only adds latency and introduces potential hallucinations. Started thinking about a completely different approach.

~5 hrs · That "aha" moment might change the whole architecture.

---

### Week 7 (Jul 6 – Jul 11)

**Day 53 · Jul 6 (Mon)**

Followed up on yesterday's insight. The problem with running Fineract products through the normal LLM extraction pipeline is:

1. We LOSE precision — Fineract gives us `interestRatePerPeriod: 18.0` and the LLM might return `18%` (losing the fact that it's per period, not annual)
2. We add hallucination risk — the LLM sometimes guesses at fields that aren't in the text representation
3. It's SLOW — unnecessary LLM call adds 3–5 seconds

The solution: build the `LoanAgreementSchema` DIRECTLY from Fineract's structured JSON, bypassing LLM extraction entirely. Every value comes from the authoritative source. Then only use the LLM for the one thing it's actually good at — generating a human-readable summary.

Spent the day mapping every Fineract field to our schema fields. Made a big spreadsheet:
- `principal` → `loan_amount.value`
- `annualInterestRate` → `interest_rate.value` (NOT `interestRatePerPeriod`!)
- `numberOfRepayments` × `repaymentEvery` → `repayment_duration.value`
- `charges[]` → various fee fields depending on `chargeTimeType`

The charge classification is especially tricky — more on that tomorrow.

~6 hrs · Excited about this approach. It's fundamentally more correct than LLM extraction.

---

**Day 54 · Jul 7 (Tue)**

Started writing `build_schema_from_fineract()` — the big function that constructs a `LoanAgreementSchema` directly from Fineract JSON. Got the core fields done: loan amount, interest rate, repayment duration.

The interest rate mapping was the trickiest part. Fineract has THREE rate-related fields: `interestRatePerPeriod` (could be monthly or yearly), `annualInterestRate` (always yearly), and `interestRateFrequencyType` (tells you what period the rate is for). Our schema expects annual percentage, so I always use `annualInterestRate` — but I log the per-period rate in the source clause for transparency.

Also mapped `interestType` codes to our schema types. Fineract uses `interestType.declining.balance` and `interestType.flat` — I map these to `reducing` and `flat` respectively. The naming difference tripped me up for a bit.

For repayment duration, I have to calculate total months from `numberOfRepayments × repaymentEvery`, and handle the case where the frequency is weeks instead of months (conversion: `weeks × 7 / 30`). Not perfectly precise but close enough.

Set all confidence scores to 0.99 and `extraction_method` to `fineract_api` — because these values are 100% accurate from the authoritative source, not guessed by an LLM.

~5 hrs

---

**Day 55 · Jul 8 (Wed)**

Tackled the charge/fee classification logic. This was way harder than I expected. Fineract's charges array is a flat list — each charge has a `chargeTimeType` (when it's applied) and a `chargeCalculationType` (how it's calculated), plus a name.

Our schema has specific fee fields: `processing_fee`, `late_fee`, `late_payment_interest`, `penalty_interest`, `prepayment_penalty`, `insurance_fee`, `administrative_fee`, `other_fee`. I need to classify each Fineract charge into the right bucket.

My classification strategy uses a combination of the charge time type code and the charge name:
- `disbursement` time type OR name contains "processing" → `processing_fee`
- `overdue` time type OR name contains "late" → `late_fee` (flat) or `late_payment_interest` (percentage)
- Name contains "prepayment" or "foreclosure" → `prepayment_penalty`
- Name contains "insurance" → `insurance_fee`
- Name contains "admin" → `administrative_fee`
- Everything else → `other_fee`

The percentage vs flat distinction matters: if `chargeCalculationType` contains "percent", it goes to the interest-based fee field. If it's flat, it goes to the flat fee field. Tested with 5 different products from the demo server and the classification was correct for all of them.

~5 hrs · Fee classification is one of those things that seems simple but has tons of edge cases.

---

**Day 56 · Jul 9 (Thu)**

Added handling for Fineract-specific features that don't have direct schema equivalents: down payments, grace periods, arrears tolerance, multi-disbursement loans, and overdue day configuration. I mapped these to `default_events` in our schema — they're not exactly "default events" in the legal sense, but they're important terms that borrowers should know about.

The down payment logic was the most involved. When `enableDownPayment` is true, the net principal (for EMI calculation) is `principal - (principal × downPaymentPercentage / 100)`. I update the `loan_amount` field to reflect the net amount and add a default event explaining the down payment requirement. Used the currency formatter to display amounts properly.

Also handled `graceOnPrincipalPayment`, `graceOnInterestPayment`, `inArrearsTolerance`, `graceOnArrearsAgeing`, and `multiDisburseLoan`. Each one becomes a `DefaultEventField` with a clear trigger description and source clause pointing back to the Fineract product config.

~4 hrs

---

**Day 57 · Jul 10 (Fri)**

Built `analyse_fineract_product()` in `ai_service.py` — a completely separate analysis function for Fineract products. Unlike `analyse_contract()`, this one:

1. Does NOT run LLM extraction (schema is pre-built from Fineract JSON)
2. Does NOT run input sanitization (data is from a trusted API, not user input)
3. DOES run the validation pipeline (risk scoring, math checks, financial calcs)
4. DOES use the LLM for summary generation (the one thing it's good at)

The key insight: validation and risk analysis are purely deterministic — they don't need the LLM at all. Only the human-readable summary benefits from LLM language generation. So we get the best of both worlds: 100% accurate data from Fineract + a helpful summary from the LLM.

Also added `get_product_raw()` to `fineract_service.py` — returns the raw Fineract JSON without converting to text. This is what `build_schema_from_fineract()` needs as input.

~5 hrs · This feels like the right architecture. Authoritative data + LLM for language only.

---

**Day 58 · Jul 11 (Sat)**

Integrated the Fineract path into the `/analyze` endpoint. The `ContractRequest` schema now accepts an optional `loan_product_id` field. The router checks: if `text` is provided, run the normal extraction pipeline. If `loan_product_id` is provided, fetch the product from Fineract, build the schema directly, and only use the LLM for the summary.

The error handling for the Fineract path needed to be more specific than the text path. I handle:
- Product not found (404) → "Loan product with ID X not found in Mifos X"
- Auth failed (401) → "Authentication failed with Mifos X. Check credentials."
- Server down (timeout/connect error) → "Cannot connect to Mifos X. Use manual paste instead."
- Unknown error → "Failed to fetch loan product. Check Fineract configuration."

Tested end-to-end with the demo server: select a product from the dropdown → backend fetches from Fineract → builds schema → validates → generates summary → returns to frontend. The whole flow takes about 2–3 seconds (vs 5–8 seconds for the LLM extraction path). Much faster because we skip the extraction LLM call entirely.

~5 hrs · Full Fineract analysis pipeline working end-to-end! 🎉

---

### Week 8 (Jul 13 – Jul 18)

**Day 59 · Jul 13 (Mon)**

Production hardening day. Added three things to `fineract_service.py`:

1. **Caching** — `list_loan_products()` now caches the result for 5 minutes (configurable `CACHE_TTL`). Loan products don't change every second, so there's no point hammering the Fineract API on every page load. Added `invalidate_products_cache()` for when you need a force-refresh.

2. **Retry logic** — Wrapped all Fineract API calls with `@retry` from the `tenacity` library. 3 attempts, exponential backoff (2s → 4s → 10s), only retries on `TimeoutException` and `ConnectError` (NOT on 401/404 — those are permanent failures, retrying won't help).

3. **Connection pooling** — The shared `httpx.AsyncClient` already handles this, but I tweaked the limits: max 5 keepalive connections, max 10 total. Good balance between connection reuse and not overwhelming the Fineract server.

Also added `before_sleep_log` to the retry decorator so retries show up in the logs with WARNING level. Super helpful for debugging flaky connections.

~4 hrs

---

**Day 60 · Jul 14 (Tue)**

Built the currency formatting utilities in `pipeline/currency.py`. The problem: our app was hardcoded to INR/Rs everywhere, but Fineract supports loans in any currency. The demo server has products in INR, USD, and several African currencies.

Created a map of 50+ ISO 4217 currency codes to their display symbols (₹, $, €, £, KSh, etc.). Then two formatting functions: `format_currency()` (whole numbers: "₹50,000") and `format_currency_precise()` (2 decimal places: "₹50,000.00"). Some currencies conventionally have a space before the number (like "KSh 500") so I handle that too.

Updated `build_schema_from_fineract()` to use these formatters everywhere instead of hardcoded "Rs." strings. Now the app handles any currency that Fineract throws at it. Tested with INR, USD, KES and the formatting looked correct.

Also added 25 realistic loan contract samples in `sample_contracts/` for testing — covering agriculture, business, housing, education, and vehicle loans. Each one is 15,000+ characters with full legal structure. Way better test data than the tiny samples I was using before.

~5 hrs

---

**Day 61 · Jul 15 (Wed)**

Built the `MifosProductPicker` React component for the frontend. It's a dropdown that loads loan products from Fineract and lets users select one for analysis (instead of pasting text).

Features:
- Auto-fetches products on mount via the `/loanproducts` endpoint
- Loading spinner while fetching
- Error state with retry and "clear & retry" buttons
- Refresh button to force-fetch fresh data (calls `/loanproducts/refresh`)
- Shows product count: "12 products available"
- Graceful fallback when Fineract is unreachable

Used the `useLoanProducts` custom hook to manage the fetch state. The error handling was important — if Fineract is down, the picker shows a friendly message instead of crashing the whole UI: "Could not connect to Mifos X. You can still paste your contract text manually."

Also hooked it up to the i18n system so all strings are translatable.

~4 hrs

---

**Day 62 · Jul 16 (Thu)**

Enhanced the `/health` endpoint to include Fineract connectivity status. It now returns:

```json
{
  "status": "ok",
  "llm_provider": "gemini",
  "fineract_reachable": true,
  "fineract_url": "https://demo.mifos.community/fineract-provider",
  "fineract_status": {
    "reachable": true,
    "status_code": 200,
    "product_count": 15,
    "error": null
  }
}
```

The `check_fineract_health()` function makes a lightweight call to the loan products endpoint and reports back. It catches `ConnectError`, `TimeoutException`, and non-200 status codes separately, so you can tell the difference between "server is down" and "credentials are wrong".

Also built the loan simulator endpoint (`/simulator`) — takes loan amount, interest rate, tenure, and interest type, and returns a full amortization schedule with month-by-month EMI breakdown. Uses `Decimal` everywhere (learned that lesson the hard way in Phase 1, Day 34). Handles both flat-to-reducing rate conversion and zero-interest edge cases.

~4 hrs

---

**Day 63 · Jul 17 (Fri)**

Testing day. Wrote the `test_fineract_service.py` test suite — 444 lines covering:

- **SSL configuration tests** (4 tests): default enabled, disabled returns false, valid CA bundle, missing CA bundle raises `FileNotFoundError`
- **Shared HTTP client tests** (4 tests): client creation, reuse on subsequent calls, timeout configuration, connection pool limits
- **Auth headers tests** (2 tests): correct format with Basic Auth + tenant header, base64 encoding verification
- **API function tests** (3 tests): successful product list, HTTP error handling, empty response handling
- **Product-to-text tests** (3 tests): complete data, minimal data, missing name fallback
- **Health check tests** (3 tests): success returns reachable=true, connection error returns false, non-200 status

All mocked with `unittest.mock` — no real Fineract calls needed. The mocking for async functions (`AsyncMock`) was tricky at first but makes the tests fast and reliable.

One annoying issue: had to reset the global `_fineract_client` in `setup_method` for every test class, otherwise the singleton would leak state between tests. Added `teardown_method` cleanup too.

~5 hrs

---

**Day 64 · Jul 18 (Sat)**

Wrote `test_integration_fineract.py` — 416 lines of integration-style tests (still mocked, but testing the full flow through the service layer). Covers:

- Listing products (success, empty list, auth error, network error)
- Getting a specific product (success, not found)
- Analysing a Fineract product through the pipeline (with mocked LLM)
- SSL verification behaviour
- Custom CA bundle
- Timeout handling
- Invalid JSON response
- Authentication headers verification

Used a realistic `MOCK_LOAN_PRODUCT` fixture with all the nested Fineract JSON structure (currency, interest type, repayment frequency, charges). Tests that need a real Fineract instance are marked with `@pytest.mark.integration` and skipped by default — you have to explicitly opt in with `RUN_INTEGRATION_TESTS=1`.

Ran the full test suite — all passing. Coverage for `fineract_service.py` is at ~90%.

~5 hrs

---

### Week 9 (Jul 20 – Jul 21)

**Day 65 · Jul 20 (Mon)**

Docker and deployment day. Updated `docker-compose.yml` to pass through all the Fineract environment variables to the backend container. Had to be careful with the Ollama URL — when running Ollama on the host and the backend in Docker, localhost doesn't work. Set the default to `http://host.docker.internal:11434` which Docker Desktop resolves to the host machine.

Added the `PYTHONIOENCODING=utf-8` environment variable to the Docker config because emoji characters in the logger were causing `UnicodeEncodeError` on Windows hosts with cp1252 encoding. Took a while to track down.

Also added a commented-out Ollama service block in docker-compose for users who want to run everything in Docker. Included GPU support instructions (NVIDIA and AMD) and model auto-pull on first start.

Updated security checks: production mode now requires both `FINERACT_SSL_VERIFY=true` and a non-empty `API_KEY`. If either is missing, the app refuses to start with a clear error message.

~4 hrs

---

**Day 66 · Jul 21 (Tue) — today**

Documentation day. Rewrote the entire README from scratch with proper step-by-step setup instructions — Docker quick start (5 steps), manual installation (with OS-specific instructions for Windows PowerShell, Command Prompt, macOS, and Linux), LLM provider setup for all 5 providers, Tesseract OCR setup, API usage examples with curl, troubleshooting FAQ with 10 common issues, and a full configuration reference table.

Also updated the project structure section and architecture diagram to reflect all the Fineract integration work.

~3 hrs

---

### Week 10 (Jul 22 – Jul 25)

**Day 67 · Jul 22 (Wed)**

Started work on proper Ollama integration. We had Ollama listed as a provider since Day 2 but the implementation was a basic stub — it just wrapped the OpenAI-compatible `/v1` endpoint and broke constantly because Ollama's OpenAI compatibility layer doesn't handle `instructor` well at all. The structured JSON output would randomly fail, or the model would hallucinate extra fields that didn't match the Pydantic schema.

Decided to rewrite `ollama_provider.py` from scratch. The new `OllamaProvider` class (325 lines) takes a completely different approach — instead of pretending Ollama is OpenAI, it uses Ollama's **native HTTP API** directly via `httpx`. Three core methods:

1. `generate_native()` — streaming text generation via `/api/generate`
2. `generate_json()` — structured JSON output using Ollama's `format: "json"` parameter
3. The OpenAI-compatible client is still there (`raw_client`) as a fallback for anything that needs it

The `generate_native()` method uses streaming (`httpx.stream`) to handle long responses without timeout issues. Each chunk from Ollama is a JSON line with a `response` field — I accumulate them until `done: true`. Set a 120-second timeout because local models on CPU can be SLOW.

Also set `supports_instructor` to `False` so the extraction pipeline knows to skip the instructor path and go straight to native generation.

~6 hrs · This felt like the right call. Fighting instructor compatibility was a losing battle.

---

**Day 68 · Jul 23 (Thu)**

Built the `generate_json()` method — this was the key piece for reliable extraction. Ollama has a native JSON mode where you pass `"format": "json"` in the request body, and the model is constrained to output valid JSON. This is WAY more reliable than asking the model to "please return JSON" in the prompt and hoping for the best.

The implementation mirrors `generate_native()` (streaming via httpx) but adds the `format` parameter and a JSON validation step at the end. If the response somehow isn't valid JSON (rare but possible with smaller models), it falls back to `generate_native()` with a warning log. Belt and suspenders.

Also added auto-model-pull: when `OllamaProvider.__init__()` runs, it calls `_ensure_model_available()` which checks if the configured model (e.g. `llama3.2:latest`) is actually downloaded. If not, it auto-pulls from the Ollama registry with streaming progress logs. This is important for first-time setup — users just set `OLLAMA_MODEL=llama3.2:latest` in `.env` and the app handles the rest. The pull has a 10-minute timeout for large models (7B+ can be several GB).

The model name matching is fuzzy — `llama3.2` matches `llama3.2:latest` because users might not include the tag.

~5 hrs

---

**Day 69 · Jul 24 (Fri)**

Integrated Ollama into the extraction pipeline (`pipeline/extractor.py`). The extraction flow now has three tiers:

1. **Instructor path** (Groq, Cerebras, HF) — structured output via the instructor library
2. **Native JSON path** (Ollama, Gemini) — `generate_json()` for reliable structured output
3. **Raw OpenAI path** — fallback for anything else

The key change: when the extractor detects an Ollama provider (checks `provider.__class__.__name__`), it immediately skips the instructor attempt and goes to the native path. Before, it would try instructor, fail, catch the exception, and THEN fall back — wasting 5–10 seconds on every request. Now it's instant.

For Ollama specifically, I prefer `generate_json()` over `generate_native()` because the JSON mode constraint dramatically reduces parse failures. In my testing with llama3.2, `generate_json()` produced valid JSON on 95%+ of calls, vs maybe 70% with `generate_native()` + prompt-based JSON instructions.

Also set the Ollama timeout to 120 seconds (vs 60 for cloud providers) because local inference is inherently slower, especially on CPU-only machines.

Did the same integration in `pipeline/summariser.py` — the summary chain now uses `generate_native()` for Ollama, which is better for free-text generation (no JSON constraint needed for summaries).

~5 hrs

---

**Day 70 · Jul 25 (Sat)**

Health check and monitoring day. Added Ollama-specific logic to the `/health` endpoint in `routers/health.py`. The health check now:

1. Detects if Ollama is the active provider (`settings.LLM_PRIMARY == 'ollama'`)
2. Skips the API key check (Ollama doesn't need one — it's local)
3. Reports `OLLAMA_MODEL` instead of `LLM_MODEL` in the response
4. Calls `health_check_detailed()` for rich status info

The `health_check_detailed()` method on `OllamaProvider` returns a detailed status dict:

```json
{
  "running": true,
  "base_url": "http://localhost:11434",
  "model": "llama3.2:latest",
  "model_available": true,
  "available_models": ["llama3.2:latest", "phi3:mini"]
}
```

If Ollama isn't running, it returns `running: false` with a helpful error message telling the user to start it. If it's running but the model isn't downloaded, `model_available` is false — the frontend can use this to show a "model not found" warning.

Also updated the `provider_configured` check — previously it only checked for API keys (Gemini, Groq, etc.), so Ollama would always show as "not configured". Now `is_ollama` is an explicit override.

~4 hrs

---

### Week 11 (Jul 27 – Jul 29)

**Day 71 · Jul 27 (Mon)**

Error handling hardening for Ollama. Local LLM inference has failure modes that cloud APIs don't — the server can be down, the model can be missing, the machine can run out of RAM mid-generation. Went through every Ollama code path and made sure each failure produces a clear, actionable error message:

- `httpx.ConnectError` → "Cannot connect to Ollama at http://localhost:11434. Please ensure Ollama is running: 1. Install: ollama.com/download, 2. Start: ollama serve, 3. Pull model: ollama pull llama3.2"
- `httpx.TimeoutException` → "Ollama generation timed out after 120s. The model 'llama3.2' may be too large for your hardware. Try a smaller model like 'llama3.2:1b' or 'phi3:mini'."
- HTTP 404 from Ollama → model not found, triggers auto-pull
- Invalid JSON from `generate_json()` → graceful fallback to `generate_native()` with a warning log

The timeout suggestion is genuinely helpful — I tested on a machine with 8GB RAM and llama3.1:8b would OOM halfway through generation. The error message now explicitly suggests smaller alternatives.

Also added `ConnectError` detection by class name as a catch-all, because sometimes httpx wraps the connection error in a generic Exception.

~4 hrs

---

**Day 72 · Jul 28 (Tue)**

Configuration and Docker day. Updated `.env.example` with a comprehensive Ollama section. Added a table of recommended models sorted by size: llama3.2:1b (fastest, good for testing), llama3.2:latest (balanced), phi3:mini, mistral:latest, qwen2.5:7b, llama3.1:8b, gemma2:9b. Each with param count and a one-liner description. Made it dead simple to switch — just change two lines (`LLM_PRIMARY=ollama` and `OLLAMA_MODEL=llama3.2:latest`).

Added `OLLAMA_BASE_URL` (default `http://localhost:11434`) and `OLLAMA_MODEL` (default `llama3.2:latest`) to the config. The base URL is important for Docker — when the backend runs in a container but Ollama runs on the host, you need `http://host.docker.internal:11434` instead of localhost. Documented this in the env file.

Updated `schemas/request.py` to include `'ollama'` in the `VALID_PROVIDERS` literal type, and made sure the provider registry has the lazy import (`_import_ollama`) so Ollama dependencies only load when actually needed — users who don't use Ollama shouldn't need `langchain-ollama` installed.

Also added `langchain-ollama>=0.1.3` to `requirements.txt` for the LangChain integration path (though we primarily use the native API now).

~4 hrs

---

**Day 73 · Jul 28 (Tue) — continued**

Provider fallback and summary routing. Fixed a subtle bug in `ai_service.py` where the summary generation step would always default to the Gemini provider, even when extraction succeeded with Ollama. The issue was in the `summary_provider` resolution line — it checks if the `provider_used` string contains "llama" (case-insensitive) to route to Ollama for summarization. Without this, you'd extract with Ollama but summarize with Gemini, which fails if the user doesn't have a Gemini API key.

The fix: `ProviderRegistry.get('ollama' if 'llama' in provider_used.lower() else 'gemini')`. Not the prettiest code, but it works. The provider name from Ollama contains the model name (e.g., "llama3.2:latest"), so checking for "llama" catches most cases. If someone uses a non-llama model through Ollama (like mistral or phi3), the `'/'` split handles the `ollama/mistral` format.

Also tested the full end-to-end flow with Ollama as both primary and fallback provider. Works well — you can set `LLM_PRIMARY=ollama` and `LLM_FALLBACK=gemini` to use local inference by default but fall back to cloud if Ollama is down. The provider registry singleton pattern means the Ollama client is only initialized once.

~3 hrs

---

**Day 74 · Jul 29 (Tue) — today**

Testing and documentation for the Ollama integration. Updated `test_integration_providers.py` and `test_extractor.py` to cover Ollama-specific paths — mocked the `OllamaProvider` with `generate_json()` and `generate_native()` responses, tested the instructor skip logic, tested timeout handling, and tested the auto-model-pull flow.

Key test scenarios:
- Ollama provider skips instructor and goes straight to native JSON path
- `generate_json()` produces valid extraction output
- `generate_json()` failure falls back to `generate_native()`
- Connection refused produces actionable error message
- Timeout produces hardware suggestion
- Health check returns detailed status when Ollama is active
- Provider registry lazy-loads Ollama only when requested

Also updated the README with Ollama setup instructions — install Ollama, pull a model, set two env vars, done. Added a "Why Ollama?" section explaining the benefits: no API key needed, data stays local (important for sensitive loan documents), no rate limits, works offline. Listed the trade-offs too: slower than cloud APIs, needs decent hardware, smaller models = lower quality extraction.

~4 hrs


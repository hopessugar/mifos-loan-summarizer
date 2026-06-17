# Implementation Plan - Feature Roadmap

## ✅ COMPLETED - Critical Bug Fixes (Audit Report)

### P0 Fixes (DONE)
- ✅ **Config environment variables** - All fields now read from .env properly
- ✅ **HF Inference provider** - Now uses OpenAI-compatible API  
- ✅ **Error handling** - Better logging in extractor
- ✅ **max_tokens** - Now uses settings (2000 for extraction, 600 for summary)
- ✅ **Groq hardcoded model** - Now reads from LLM_MODEL setting
- ✅ **Cerebras SSL** - Only disabled in development
- ✅ **Response schema** - Added extraction_method field
- ✅ **Duplicate return** - Removed from extractor.py

### Current Status
- Backend rebuilt and running with all fixes
- New Groq API key configured
- Environment variables properly loaded
- All providers now compatible

---

## 🎯 NEXT STEPS - Feature Implementation Priority

Due to the extensive scope (7 tiers, 20+ features), I recommend implementing in phases:

### **Phase 1: Foundation & Trust (Week 1)**  
**Priority: CRITICAL** - These directly fix the "returns nothing" issue

#### 1.1 Decimal Precision ✅ (Can implement now)
- File: `backend/schemas/loan_schema.py`
- Change all `float` to `Decimal`
- Time: 30 minutes

#### 1.2 Multi-Model Consensus (⚠️ Complex)
- File: `backend/pipeline/extractor.py`  
- Parallel extraction with multiple providers
- Consensus resolution logic
- Time: 3-4 hours

#### 1.3 Numerical Source Verification (⚠️ Complex)
- New file: `backend/pipeline/verification.py`
- Regex-based number extraction
- Source clause matching
- Time: 2-3 hours

### **Phase 2: Intelligence & UI (Week 2)**

#### 2.1-2.2 Confidence Indicators & Source Tracing
- File: `frontend/src/components/AnalysisReport.jsx`
- Traffic light UI (🟢🟡🔴)
- Collapsible source clauses
- Time: 2 hours

#### 2.3 Missing Terms Detector
- File: `backend/pipeline/analysis.py`
- Check for None fields
- Generate user-friendly warnings
- Time: 1 hour

#### 2.4 Predatory Pattern Database
- New file: `backend/services/predatory_detector.py`
- Global lending benchmarks (APR >36%, etc.)
- Rule engine for flags
- Time: 3 hours

### **Phase 3: Financial Tools (Week 3)**

#### 3.1 Repayment Simulator
- New file: `backend/routers/simulator.py`
- POST /api/simulate endpoint
- What-if scenarios
- Time: 2 hours

#### 3.2 Amortization Schedule
- POST /api/amortization endpoint
- Month-by-month breakdown
- Time: 2 hours

#### 3.4 Flat-to-Reducing Converter
- Add to main analysis response
- Formula implementation
- Time: 1 hour

### **Phase 4: AI Innovation (Week 4)**

#### 5.1 Self-Verification Chain
- Second LLM call for verification
- Quote-based confirmation
- Time: 2 hours

#### 5.2 Severity Scoring
- 1-10 scores per clause
- Reasoning tree JSON
- Time: 2-3 hours

#### 5.3 Contract Anomaly Detection
- Statistical boundary checks
- Time: 2 hours

#### 5.5 Smart Contract Chunking
- LangChain semantic chunking
- Pre-split before extraction
- Time: 2 hours

### **Phase 5: Visionary Features (Week 5)**

#### 7.1 Borrower Protection Score (BPS)
- Aggregate all risk factors
- 0-100 weighted formula
- Time: 2 hours

#### 7.2 Contract Negotiation Assistant
- Suggested counter-language
- For high-severity clauses
- Time: 3 hours

---

## 📊 Estimated Total Time

| Phase | Features | Time |
|-------|----------|------|
| Phase 1 | Foundation fixes | 6-8 hours |
| Phase 2 | Trust & UI | 6 hours |
| Phase 3 | Financial tools | 5 hours |
| Phase 4 | AI innovation | 8 hours |
| Phase 5 | Visionary | 5 hours |
| **TOTAL** | **20+ features** | **30-32 hours** |

---

## 🚀 RECOMMENDED APPROACH

Given the scope, I suggest:

### Option A: **Quick Win** (2 hours)
Implement just the most critical features to get extraction working:
1. Fix any remaining extraction issues
2. Add missing terms detector
3. Improve error messages
4. Test with real contracts

### Option B: **Foundation First** (8 hours)
Complete Phase 1 entirely:
1. Decimal precision
2. Multi-model consensus  
3. Numerical verification
4. Thorough testing

### Option C: **Full Implementation** (30+ hours)
Implement all 5 phases over multiple sessions

---

## 🎬 WHAT SHOULD WE DO NOW?

**IMMEDIATE PRIORITIES:**

1. **Test the current fixes** - Verify extraction works with new config
2. **Choose implementation path** - Option A, B, or C?
3. **Start with highest ROI features** - Decimal precision + missing terms

**My Recommendation:**
Start with **Option A** (Quick Win) to get the app working well, then incrementally add Phase 1-5 features based on user feedback.

---

## ⚡ Quick Start - Next 30 Minutes

If you want to proceed immediately, I can implement:

1. **Decimal precision** (loan_schema.py) - 15 min
2. **Missing terms detector** - 15 min

These two alone will significantly improve the app without major refactoring.

**Shall I proceed with these two quick wins?**

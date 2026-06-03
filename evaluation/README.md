# RAGAS Evaluation Framework

## Overview
This directory contains the RAGAS (Retrieval Augmented Generation Assessment) evaluation framework for the Mifos Loan Summarizer. The framework evaluates LLM extraction quality across multiple providers using standardized metrics.

## Directory Structure

```
evaluation/
├── README.md                    # This file
├── contracts/                   # Test loan contracts
│   ├── simple/                 # Simple contracts (5 contracts)
│   ├── medium/                 # Medium complexity (10 contracts)
│   ├── complex/                # Complex contracts (10 contracts)
│   └── ground_truth.json       # Annotated expected outputs
├── scripts/                     # Evaluation scripts
│   ├── run_evaluation.py       # Main evaluation runner
│   ├── generate_report.py      # Report generator
│   └── compare_providers.py    # Provider comparison
├── scores/                      # Evaluation results
│   ├── provider_scores/        # Per-provider results
│   └── comparison_report.md    # Comparison summary
└── config/                      # Evaluation configuration
    └── evaluation_config.yaml  # Metrics and thresholds
```

## Evaluation Metrics

### 1. Faithfulness (0-1)
Measures if extracted values are grounded in the source contract.
- **Method:** Compare extracted values against source text using hallucination detection
- **Target:** ≥ 0.85

### 2. Answer Relevancy (0-1)
Measures if extracted information is relevant to loan analysis.
- **Method:** Check if extracted fields are financial entities
- **Target:** ≥ 0.90

### 3. Context Precision (0-1)
Measures accuracy of extracted values.
- **Method:** Compare against ground truth annotations
- **Target:** ≥ 0.80

### 4. Context Recall (0-1)
Measures completeness of extraction.
- **Method:** Check if all annotated fields were extracted
- **Target:** ≥ 0.75

### 5. Extraction Accuracy (0-1)
Custom metric for exact value matching.
- **Method:** Exact match of numerical values
- **Target:** ≥ 0.70

## Test Dataset

### Contract Distribution
- **Simple (5 contracts):** Basic loan agreements with clear terms
- **Medium (10 contracts):** Standard contracts with multiple fees
- **Complex (10 contracts):** Detailed contracts with collateral, guarantors, etc.

### Ground Truth Annotations
Each contract has annotated expected outputs:
- Loan amount
- Interest rate
- Repayment duration
- Monthly payment
- Fees and charges
- Risk factors
- Default events

## Provider Testing

### Supported Providers
1. **HuggingFace Inference** (llama-3.1-8b-instant)
2. **Ollama** (llama3.1:8b)
3. **Groq** (llama-3.1-8b-instant)
4. **Cerebras** (llama3.1-8b)
5. **Mistral** (mistral-small-latest)
6. **OpenRouter** (meta-llama/llama-3.1-8b-instruct)

### Evaluation Matrix
25 contracts × 6 providers = 150 evaluations

## Running Evaluations

### Quick Start
```bash
cd evaluation
python scripts/run_evaluation.py --provider all --contracts all
```

### Single Provider
```bash
python scripts/run_evaluation.py --provider groq --contracts all
```

### Specific Contract Set
```bash
python scripts/run_evaluation.py --provider all --contracts simple
```

### Generate Report
```bash
python scripts/generate_report.py --output scores/comparison_report.md
```

## Interpreting Results

### Score Ranges
- **0.90-1.00:** Excellent - Production ready
- **0.80-0.89:** Good - Minor improvements needed
- **0.70-0.79:** Fair - Significant improvements needed
- **<0.70:** Poor - Not recommended for production

### Key Metrics to Watch
1. **Faithfulness:** Most critical - prevents hallucinations
2. **Extraction Accuracy:** Ensures correct values
3. **Context Recall:** Ensures completeness

## Configuration

Edit `config/evaluation_config.yaml` to adjust:
- Metric weights
- Score thresholds
- Provider settings
- Timeout values

## Troubleshooting

### Provider Timeouts
Increase timeout in config:
```yaml
providers:
  timeout_seconds: 300  # Default: 120
```

### Missing Ground Truth
Add annotations to `contracts/ground_truth.json`

### Low Scores
1. Check contract quality
2. Verify ground truth accuracy
3. Review provider configuration
4. Check prompt engineering

## Contributing

### Adding New Contracts
1. Place contract in appropriate complexity folder
2. Add ground truth annotation to `ground_truth.json`
3. Run evaluation to verify

### Adding New Metrics
1. Implement metric in `scripts/run_evaluation.py`
2. Add to configuration
3. Update documentation

## References

- [RAGAS Documentation](https://docs.ragas.io/)
- [LangChain Evaluation](https://python.langchain.com/docs/guides/evaluation/)
- [Technical Design Document](../DECISIONS.md)

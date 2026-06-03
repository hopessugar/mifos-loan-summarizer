"""
RAGAS Evaluation Runner for Mifos Loan Summarizer

This script evaluates LLM extraction quality across multiple providers using:
- Faithfulness: Are extracted values grounded in source?
- Answer Relevancy: Is extracted information relevant?
- Context Precision: How accurate are the values?
- Context Recall: How complete is the extraction?
- Extraction Accuracy: Do numerical values match exactly?

Usage:
    python run_evaluation.py --provider all --contracts all
    python run_evaluation.py --provider groq --contracts simple
    python run_evaluation.py --provider ollama --contracts contract_001
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
import asyncio

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.ai_service import analyse_contract
from backend.providers.registry import ProviderRegistry


# ============================================================================
# CONFIGURATION
# ============================================================================

CONTRACTS_DIR = Path(__file__).parent.parent / "contracts"
GROUND_TRUTH_FILE = CONTRACTS_DIR / "ground_truth.json"
SCORES_DIR = Path(__file__).parent.parent / "scores"
PROVIDER_SCORES_DIR = SCORES_DIR / "provider_scores"

PROVIDERS = ["hf_inference", "ollama", "groq", "cerebras"]  # Start with 4 available
COMPLEXITY_LEVELS = ["simple", "medium", "complex"]


# ============================================================================
# METRICS CALCULATION
# ============================================================================

def calculate_faithfulness(extracted: Dict, contract_text: str, ground_truth: Dict) -> float:
    """
    Calculate faithfulness score (0-1).
    Measures if extracted values are grounded in source text.
    """
    from backend.pipeline.validator import check_hallucination
    
    score_sum = 0
    count = 0
    
    # Check key financial fields
    fields_to_check = [
        ('loan_amount', extracted.get('entities', {}).get('loan_amount', {}).get('value')),
        ('interest_rate', extracted.get('entities', {}).get('interest_rate', {}).get('value')),
        ('monthly_payment', extracted.get('entities', {}).get('monthly_payment', {}).get('value')),
        ('repayment_duration', extracted.get('entities', {}).get('repayment_duration', {}).get('value')),
    ]
    
    for field_name, value in fields_to_check:
        if value is not None:
            result = check_hallucination(str(value), contract_text)
            if result['is_verified']:
                score_sum += result['similarity']
            count += 1
    
    return score_sum / count if count > 0 else 0.0


def calculate_answer_relevancy(extracted: Dict, ground_truth: Dict) -> float:
    """
    Calculate answer relevancy score (0-1).
    Measures if extracted information is relevant to loan analysis.
    """
    # Check if extracted fields are financial entities
    entities = extracted.get('entities', {})
    
    relevant_fields = [
        'loan_amount', 'interest_rate', 'repayment_duration',
        'monthly_payment', 'processing_fee', 'late_fee'
    ]
    
    relevant_count = sum(1 for field in relevant_fields if field in entities and entities[field].get('value') is not None)
    total_extracted = len([e for e in entities.values() if e.get('value') is not None])
    
    if total_extracted == 0:
        return 0.0
    
    return relevant_count / total_extracted


def calculate_context_precision(extracted: Dict, ground_truth: Dict) -> float:
    """
    Calculate context precision score (0-1).
    Measures accuracy of extracted values against ground truth.
    """
    entities = extracted.get('entities', {})
    gt = ground_truth['ground_truth']
    
    matches = 0
    total = 0
    tolerance = 0.05  # 5% tolerance for numerical values
    
    # Check numerical fields
    numerical_fields = [
        ('loan_amount', 'loan_amount'),
        ('interest_rate', 'interest_rate'),
        ('repayment_duration', 'repayment_duration'),
        ('monthly_payment', 'monthly_payment'),
        ('processing_fee', 'processing_fee'),
        ('late_fee', 'late_fee'),
    ]
    
    for extracted_field, gt_field in numerical_fields:
        if gt_field in gt and gt[gt_field] is not None:
            total += 1
            extracted_value = entities.get(extracted_field, {}).get('value')
            gt_value = gt[gt_field]
            
            if extracted_value is not None and gt_value is not None:
                # Check if within tolerance
                if abs(extracted_value - gt_value) / gt_value <= tolerance:
                    matches += 1
    
    return matches / total if total > 0 else 0.0


def calculate_context_recall(extracted: Dict, ground_truth: Dict) -> float:
    """
    Calculate context recall score (0-1).
    Measures completeness of extraction.
    """
    entities = extracted.get('entities', {})
    gt = ground_truth['ground_truth']
    
    # Required fields that should be extracted
    required_fields = [
        'loan_amount', 'interest_rate', 'repayment_duration', 'monthly_payment'
    ]
    
    # Optional fields
    optional_fields = [
        'processing_fee', 'late_fee', 'prepayment_penalty', 'penalty_interest'
    ]
    
    # Count extracted required fields
    required_extracted = sum(
        1 for field in required_fields
        if field in entities and entities[field].get('value') is not None
    )
    
    # Count extracted optional fields (if they exist in ground truth)
    optional_extracted = sum(
        1 for field in optional_fields
        if gt.get(field) is not None and field in entities and entities[field].get('value') is not None
    )
    
    # Count total fields that should be extracted
    total_required = len(required_fields)
    total_optional = sum(1 for field in optional_fields if gt.get(field) is not None)
    
    # Weighted score: required fields are more important
    required_score = required_extracted / total_required if total_required > 0 else 0
    optional_score = optional_extracted / total_optional if total_optional > 0 else 0
    
    # 80% weight to required, 20% to optional
    return 0.8 * required_score + 0.2 * optional_score


def calculate_extraction_accuracy(extracted: Dict, ground_truth: Dict) -> float:
    """
    Calculate extraction accuracy score (0-1).
    Custom metric for exact value matching.
    """
    entities = extracted.get('entities', {})
    gt = ground_truth['ground_truth']
    
    exact_matches = 0
    total = 0
    
    # Check all numerical fields for exact match
    fields_to_check = [
        'loan_amount', 'interest_rate', 'repayment_duration',
        'monthly_payment', 'processing_fee', 'late_fee'
    ]
    
    for field in fields_to_check:
        if gt.get(field) is not None:
            total += 1
            extracted_value = entities.get(field, {}).get('value')
            gt_value = gt[field]
            
            if extracted_value == gt_value:
                exact_matches += 1
    
    return exact_matches / total if total > 0 else 0.0


# ============================================================================
# EVALUATION RUNNER
# ============================================================================

async def evaluate_contract(
    contract_file: Path,
    ground_truth: Dict,
    provider: str
) -> Dict[str, Any]:
    """
    Evaluate a single contract with a single provider.
    """
    print(f"  Evaluating {contract_file.name} with {provider}...")
    
    # Read contract
    contract_text = contract_file.read_text(encoding='utf-8')
    
    # Run analysis
    start_time = time.time()
    try:
        result = await analyse_contract(
            text=contract_text,
            language='en',
            provider_override=provider
        )
        processing_time = time.time() - start_time
        
        # Convert result to dict for evaluation
        extracted = {
            'entities': {k: v.dict() for k, v in result.entities.items()},
            'math_check': result.math_check.dict(),
            'financial_summary': result.financial_summary.dict(),
            'risk_analysis': result.risk_analysis.dict(),
            'default_events': [e.dict() for e in result.default_events],
            'summary': result.summary,
        }
        
        # Calculate metrics
        faithfulness = calculate_faithfulness(extracted, contract_text, ground_truth)
        relevancy = calculate_answer_relevancy(extracted, ground_truth)
        precision = calculate_context_precision(extracted, ground_truth)
        recall = calculate_context_recall(extracted, ground_truth)
        accuracy = calculate_extraction_accuracy(extracted, ground_truth)
        
        # Calculate weighted overall score
        weights = {
            'faithfulness': 0.30,
            'relevancy': 0.20,
            'precision': 0.25,
            'recall': 0.15,
            'accuracy': 0.10,
        }
        
        overall_score = (
            faithfulness * weights['faithfulness'] +
            relevancy * weights['relevancy'] +
            precision * weights['precision'] +
            recall * weights['recall'] +
            accuracy * weights['accuracy']
        )
        
        return {
            'contract_id': ground_truth['id'],
            'provider': provider,
            'success': True,
            'processing_time': processing_time,
            'metrics': {
                'faithfulness': round(faithfulness, 3),
                'answer_relevancy': round(relevancy, 3),
                'context_precision': round(precision, 3),
                'context_recall': round(recall, 3),
                'extraction_accuracy': round(accuracy, 3),
                'overall_score': round(overall_score, 3),
            },
            'extracted': extracted,
        }
        
    except Exception as e:
        print(f"    ERROR: {str(e)}")
        return {
            'contract_id': ground_truth['id'],
            'provider': provider,
            'success': False,
            'error': str(e),
            'processing_time': time.time() - start_time,
        }


async def run_evaluation(
    providers: List[str],
    contracts: List[str],
    output_dir: Path
) -> Dict[str, Any]:
    """
    Run evaluation across providers and contracts.
    """
    # Load ground truth
    with open(GROUND_TRUTH_FILE, 'r', encoding='utf-8') as f:
        ground_truth_data = json.load(f)
    
    # Filter contracts
    if contracts != ['all']:
        ground_truth_data['contracts'] = [
            c for c in ground_truth_data['contracts']
            if c['id'] in contracts or c['complexity'] in contracts
        ]
    
    print(f"\n{'='*70}")
    print(f"RAGAS EVALUATION - Mifos Loan Summarizer")
    print(f"{'='*70}")
    print(f"Providers: {', '.join(providers)}")
    print(f"Contracts: {len(ground_truth_data['contracts'])}")
    print(f"{'='*70}\n")
    
    # Run evaluations
    results = []
    for provider in providers:
        print(f"\n[Provider: {provider}]")
        
        for contract_data in ground_truth_data['contracts']:
            contract_file = CONTRACTS_DIR / contract_data['file']
            
            if not contract_file.exists():
                print(f"  WARNING: {contract_file} not found, skipping...")
                continue
            
            result = await evaluate_contract(contract_file, contract_data, provider)
            results.append(result)
    
    # Save results
    output_file = output_dir / f"evaluation_results_{int(time.time())}.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.time(),
            'providers': providers,
            'total_evaluations': len(results),
            'results': results,
        }, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*70}\n")
    
    # Print summary
    print_summary(results)
    
    return results


def print_summary(results: List[Dict]):
    """Print evaluation summary."""
    print("\n" + "="*70)
    print("EVALUATION SUMMARY")
    print("="*70)
    
    # Group by provider
    by_provider = {}
    for result in results:
        provider = result['provider']
        if provider not in by_provider:
            by_provider[provider] = []
        by_provider[provider].append(result)
    
    # Print per-provider summary
    for provider, provider_results in by_provider.items():
        print(f"\n[{provider.upper()}]")
        
        successful = [r for r in provider_results if r['success']]
        failed = [r for r in provider_results if not r['success']]
        
        print(f"  Total: {len(provider_results)}")
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(failed)}")
        
        if successful:
            # Calculate average metrics
            avg_metrics = {}
            for metric in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall', 'extraction_accuracy', 'overall_score']:
                values = [r['metrics'][metric] for r in successful]
                avg_metrics[metric] = sum(values) / len(values)
            
            print(f"\n  Average Metrics:")
            print(f"    Faithfulness:        {avg_metrics['faithfulness']:.3f}")
            print(f"    Answer Relevancy:    {avg_metrics['answer_relevancy']:.3f}")
            print(f"    Context Precision:   {avg_metrics['context_precision']:.3f}")
            print(f"    Context Recall:      {avg_metrics['context_recall']:.3f}")
            print(f"    Extraction Accuracy: {avg_metrics['extraction_accuracy']:.3f}")
            print(f"    Overall Score:       {avg_metrics['overall_score']:.3f}")
            
            # Avg processing time
            avg_time = sum(r['processing_time'] for r in successful) / len(successful)
            print(f"\n  Avg Processing Time: {avg_time:.2f}s")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Run RAGAS evaluation')
    parser.add_argument(
        '--provider',
        type=str,
        default='all',
        help='Provider to evaluate (all, hf_inference, ollama, groq, cerebras)'
    )
    parser.add_argument(
        '--contracts',
        type=str,
        default='all',
        help='Contracts to evaluate (all, simple, medium, complex, or specific contract ID)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=str(PROVIDER_SCORES_DIR),
        help='Output directory for results'
    )
    
    args = parser.parse_args()
    
    # Parse providers
    if args.provider == 'all':
        providers = PROVIDERS
    else:
        providers = [args.provider]
    
    # Parse contracts
    if args.contracts == 'all':
        contracts = ['all']
    else:
        contracts = args.contracts.split(',')
    
    # Run evaluation
    output_dir = Path(args.output)
    asyncio.run(run_evaluation(providers, contracts, output_dir))


if __name__ == '__main__':
    main()

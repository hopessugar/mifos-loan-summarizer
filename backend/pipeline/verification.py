"""
Numerical Source Verification Module

This module verifies that extracted numerical values actually appear in the source contract.
It uses regex to find numbers in the exact source clause and compares them to extracted values.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import List, Tuple, Optional
from schemas.loan_schema import LoanAgreementSchema, EntityField, InterestField, FeeField


def extract_numbers_from_text(text: str) -> List[Decimal]:
    """
    Extract all numerical values from text using regex.
    Supports formats: 1,00,000 | 100000 | 1.5 | 10.5% | Rs. 50,000
    """
    if not text:
        return []
    
    numbers = []
    
    # Pattern matches: 1,00,000 or 100,000 or 1000 or 10.5 or .5
    # Also handles Rs., INR, ₹ prefixes and % suffixes
    pattern = r'(?:Rs\.?|INR|₹)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*%?'
    
    matches = re.finditer(pattern, text, re.IGNORECASE)
    
    for match in matches:
        num_str = match.group(1).replace(',', '')  # Remove commas
        try:
            numbers.append(Decimal(num_str))
        except (ValueError, InvalidOperation):
            continue
    
    return numbers


def verify_numerical_value(
    extracted_value: Optional[Decimal],
    source_clause: Optional[str],
    tolerance: Decimal = Decimal('0.01')
) -> Tuple[bool, float, List[Decimal]]:
    """
    Verify that the extracted value appears in the source clause.
    
    Args:
        extracted_value: The value extracted by LLM
        source_clause: The text clause from which value was supposedly extracted
        tolerance: Acceptable difference for fuzzy matching (default 1%)
    
    Returns:
        (is_verified, similarity_score, candidate_numbers)
    """
    if extracted_value is None or not source_clause:
        return False, 0.0, []
    
    # Extract all numbers from source clause
    candidate_numbers = extract_numbers_from_text(source_clause)
    
    if not candidate_numbers:
        return False, 0.0, []
    
    # Check for exact match
    for candidate in candidate_numbers:
        if candidate == extracted_value:
            return True, 1.0, candidate_numbers
    
    # Check for close match (within tolerance)
    best_similarity = 0.0
    for candidate in candidate_numbers:
        if extracted_value == 0:
            similarity = 0.0
        else:
            diff = abs(candidate - extracted_value) / extracted_value
            similarity = max(0.0, 1.0 - float(diff))
            
            if diff <= tolerance:
                best_similarity = max(best_similarity, similarity)
    
    is_verified = best_similarity >= 0.99  # 99% match threshold
    
    return is_verified, best_similarity, candidate_numbers


def verify_numerical_values(
    schema: LoanAgreementSchema,
    contract_text: str
) -> LoanAgreementSchema:
    """
    Verify all numerical fields in the schema against the contract text.
    Updates the 'is_verified' and 'similarity' fields for each entity.
    """
    
    # Helper function to verify and update an entity field
    def verify_entity(entity: EntityField, field_name: str) -> EntityField:
        if entity.value is not None and entity.source_clause:
            is_verified, similarity, candidates = verify_numerical_value(
                entity.value,
                entity.source_clause
            )
            entity.is_verified = is_verified
            entity.similarity = similarity
            
            if not is_verified and candidates:
                print(f"⚠️  {field_name}: Extracted {entity.value}, but found {candidates} in source")
        
        return entity
    
    def verify_interest(interest: InterestField, field_name: str) -> InterestField:
        if interest.value is not None and interest.source_clause:
            is_verified, similarity, candidates = verify_numerical_value(
                interest.value,
                interest.source_clause
            )
            interest.is_verified = is_verified
            interest.similarity = similarity
            
            if not is_verified and candidates:
                print(f"⚠️  {field_name}: Extracted {interest.value}%, but found {candidates} in source")
        
        return interest
    
    def verify_fee(fee: FeeField, field_name: str) -> FeeField:
        if fee.value is not None and fee.source_clause:
            is_verified, similarity, candidates = verify_numerical_value(
                fee.value,
                fee.source_clause
            )
            fee.is_verified = is_verified
            fee.similarity = similarity
            
            if not is_verified and candidates:
                print(f"⚠️  {field_name}: Extracted {fee.value}, but found {candidates} in source")
        
        return fee
    
    # Verify core financial fields
    schema.loan_amount = verify_entity(schema.loan_amount, "loan_amount")
    schema.repayment_duration = verify_entity(schema.repayment_duration, "repayment_duration")
    schema.monthly_payment = verify_entity(schema.monthly_payment, "monthly_payment")
    schema.total_cost = verify_entity(schema.total_cost, "total_cost")
    
    # Verify interest rate
    schema.interest_rate = verify_interest(schema.interest_rate, "interest_rate")
    
    # Verify fees
    schema.late_fee = verify_fee(schema.late_fee, "late_fee")
    schema.late_payment_interest = verify_fee(schema.late_payment_interest, "late_payment_interest")
    schema.penalty_interest = verify_fee(schema.penalty_interest, "penalty_interest")
    schema.prepayment_penalty = verify_fee(schema.prepayment_penalty, "prepayment_penalty")
    schema.processing_fee = verify_fee(schema.processing_fee, "processing_fee")
    schema.insurance_fee = verify_fee(schema.insurance_fee, "insurance_fee")
    schema.administrative_fee = verify_fee(schema.administrative_fee, "administrative_fee")
    schema.other_fee = verify_fee(schema.other_fee, "other_fee")
    
    return schema


def add_missing_verified_fields(schema: LoanAgreementSchema) -> LoanAgreementSchema:
    """
    Add is_verified and similarity fields to entities that don't have them.
    This ensures backward compatibility with existing code.
    """
    
    def ensure_verified_fields(entity):
        if hasattr(entity, 'value') and entity.value is not None:
            if not hasattr(entity, 'is_verified') or entity.is_verified is None:
                entity.is_verified = False
            if not hasattr(entity, 'similarity') or entity.similarity is None:
                entity.similarity = 0.0
        return entity
    
    # Add to all entity fields
    for field_name in ['loan_amount', 'repayment_duration', 'monthly_payment', 'total_cost']:
        field = getattr(schema, field_name)
        setattr(schema, field_name, ensure_verified_fields(field))
    
    # Add to interest rate
    schema.interest_rate = ensure_verified_fields(schema.interest_rate)
    
    # Add to all fees
    for fee_field in ['late_fee', 'late_payment_interest', 'penalty_interest', 
                      'prepayment_penalty', 'processing_fee', 'insurance_fee',
                      'administrative_fee', 'other_fee']:
        fee = getattr(schema, fee_field)
        setattr(schema, fee_field, ensure_verified_fields(fee))
    
    return schema

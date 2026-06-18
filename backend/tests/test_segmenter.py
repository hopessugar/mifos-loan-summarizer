import pytest
from pipeline.segmenter import (
    segment_contract,
    segment_by_headers,
    segment_by_sentences,
    segments_to_dict,
)

HEADER_CONTRACT = """
CLAUSE 1 LOAN AMOUNT
The borrower shall receive a loan of Rs. 50,000.

CLAUSE 2 INTEREST RATE
The interest rate shall be 24% per annum on a reducing balance basis.

CLAUSE 3 REPAYMENT
The loan shall be repaid in 24 equal monthly instalments of Rs. 2,500 each.

CLAUSE 4 DEFAULT
In the event of default, a penalty of 2% per month shall apply.
"""

HEADERLESS_CONTRACT = """
This loan agreement is entered into between the lender and the borrower.
The principal amount is Rs. 25,000 to be disbursed on 01/06/2026.
The interest rate applicable is 18% per annum on flat basis.
Monthly instalments of Rs. 1,500 are due on the 5th of every month.
Late payment will attract a penalty of Rs. 250 per month.
The borrower agrees to repay the full amount within 24 months.
"""


def test_header_contract_uses_header_path():
    segments = segment_by_headers(HEADER_CONTRACT)
    assert len(segments) >= 2


def test_header_contract_labels():
    segments = segment_by_headers(HEADER_CONTRACT)
    labels = [s.label for s in segments]
    assert any('CLAUSE' in label for label in labels)


def test_headerless_falls_back_to_sentences():
    segments = segment_by_sentences(HEADERLESS_CONTRACT)
    assert len(segments) >= 1
    for s in segments:
        assert s.token_count <= 200


def test_segment_contract_returns_segments():
    segments = segment_contract(HEADER_CONTRACT)
    assert len(segments) > 0


def test_segment_contract_headerless():
    segments = segment_contract(HEADERLESS_CONTRACT)
    assert len(segments) > 0


def test_segments_to_dict_shape():
    segments = segment_contract(HEADER_CONTRACT)
    result = segments_to_dict(segments)
    for item in result:
        assert 'id' in item
        assert 'label' in item
        assert 'text' in item
        assert 'char_start' in item
        assert 'char_end' in item
        assert 'token_count' in item


def test_empty_contract_raises():
    with pytest.raises(Exception):
        segment_contract('')

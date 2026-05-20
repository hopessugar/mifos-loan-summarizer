from pydantic import BaseModel, model_validator
from typing import Literal


class ContractRequest(BaseModel):
    text: str | None = None
    loan_product_id: int | None = None
    language: Literal['en', 'hi'] = 'en'
    provider: str | None = None

    @model_validator(mode='after')
    def exactly_one_input(self):
        if not self.text and not self.loan_product_id:
            raise ValueError('Provide either text or loan_product_id')
        if self.text and self.loan_product_id:
            raise ValueError('Provide either text or loan_product_id, not both')
        if self.text and len(self.text) < 50:
            raise ValueError('Contract text too short (minimum 50 characters)')
        return self

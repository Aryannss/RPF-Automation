from pydantic import BaseModel
from typing import List, Optional

class RFPUploadResponse(BaseModel):
    rfp_id: str
    filename: str
    status: str

class ExtractedRequirement(BaseModel):
    id: int
    text: str

class SKUHit(BaseModel):
    sku_id: str
    sku_name: str
    score: float

class PricingBreakdown(BaseModel):
    sku_id: str
    sku_name: str
    unit_price: float
    quantity: int
    testing_cost: float
    margin_pct: float
    total: float

class RFPResult(BaseModel):
    rfp_id: str
    requirements: List[ExtractedRequirement]
    sku_matches: dict  # requirement_id -> List[SKUHit]
    pricing: List[PricingBreakdown]
    compiled_doc_path: Optional[str]

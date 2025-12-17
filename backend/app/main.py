from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.utils import save_upload, extract_text_from_pdf, UPLOAD_DIR
from app.agents import SalesAgent, TechnicalAgent, PricingAgent, MasterAgent
from app.schemas import RFPUploadResponse, RFPResult
import os
import shutil
import uuid

app = FastAPI(title="RFP Agent Prototype")

BASE_DIR = os.path.dirname(__file__)
SKU_DB = os.path.join(BASE_DIR, "sku_db.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# init agents
sales_agent = SalesAgent()
technical_agent = TechnicalAgent(sku_db_path=SKU_DB)
pricing_agent = PricingAgent()
master_agent = MasterAgent()

# In-memory store for demo (replace with DB)
STORE = {}

@app.post("/upload_rfp", response_model=RFPUploadResponse)
async def upload_rfp(file: UploadFile = File(...)):
    content = await file.read()
    path, rfp_id = save_upload(content, file.filename)
    STORE[rfp_id] = {"status": "uploaded", "path": path, "filename": file.filename}
    return {"rfp_id": rfp_id, "filename": file.filename, "status": "uploaded"}

@app.post("/process/{rfp_id}", response_model=RFPResult)
def process_rfp(rfp_id: str):
    if rfp_id not in STORE:
        raise HTTPException(status_code=404, detail="RFP not found")
    r = STORE[rfp_id]
    rfp_text = extract_text_from_pdf(r["path"])
    # Sales discovery
    meta = sales_agent.discover(rfp_text)
    # Technical
    requirements = technical_agent.extract_requirements(rfp_text)
    sku_matches = technical_agent.match_skus(requirements, top_k=3)
    # Pricing
    pricing = pricing_agent.estimate_pricing(sku_matches)
    # Master compilation
    out_pdf = os.path.join(OUTPUT_DIR, f"{rfp_id}_response.pdf")
    master_agent.compile_response(meta["title"], requirements, sku_matches, pricing, out_pdf)
    STORE[rfp_id].update({
        "status": "processed",
        "requirements": requirements,
        "sku_matches": sku_matches,
        "pricing": pricing,
        "compiled_doc": out_pdf
    })
    return {
        "rfp_id": rfp_id,
        "requirements": [{"id": i, "text": t} for i, t in enumerate(requirements)],
        "sku_matches": sku_matches,
        "pricing": pricing,
        "compiled_doc_path": out_pdf
    }

@app.get("/download/{rfp_id}")
def download_response(rfp_id: str):
    rec = STORE.get(rfp_id)
    if not rec or rec.get("status") != "processed":
        raise HTTPException(status_code=404, detail="No processed response")
    return FileResponse(rec["compiled_doc"], media_type="application/pdf", filename=os.path.basename(rec["compiled_doc"]))

@app.get("/status/{rfp_id}")
def status(rfp_id: str):
    return STORE.get(rfp_id, {"status": "unknown"})

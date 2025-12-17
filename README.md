Quick local run (without Docker)


Create two virtualenvs (backend & frontend) or one and install both sets of requirements.


Backend:
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
uvicorn app.main:app --reload --port 8000



Frontend:
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py



Open Streamlit UI at http://localhost:8501. Backend runs at http://localhost:8000.


Run with Docker Compose


Ensure Docker is installed.


From repository root:
docker-compose up --build



Access UI at http://localhost:8501.



How the prototype maps to the PPT agents


Sales Agent (SalesAgent.discover) — very light: pulls a title/metadata for the RFP.


Technical Agent (TechnicalAgent) — extracts requirement lines, computes embeddings, matches to sku_db.csv.


Pricing Agent (PricingAgent) — simple deterministic pricing rule (unit_price + testing + margin) to produce totals.


Master Agent (MasterAgent) — compiles everything into a PDF response you can download.



Extension ideas (what to add next — quick checklist for EY-level polish)


Replace simple text extraction with robust OCR + layout parsing for PDFs.


Use a message queue (Redis + RQ/Celery) for async processing of heavy embedding work.


Add user authentication + role-based UI (Sales, Technical, Pricing, Management).


Add an approvals workflow (human-in-the-loop) with edit/accept buttons.


Use a persistent DB (Postgres) + object store (S3/minio) for files.


Improve SKU DB with more fields: lead times, min order qty, alternative SKUs.


Add unit tests for each agent (pytest).


Improve matching: use contextual prompts or reranking with a small LLM for final verification.


Add telemetry/metrics in the dashboard (processing time, avg match scores, projected ROI).



Quick sanity checks & troubleshooting


If sentence-transformers tries to download models when running inside restricted network, make sure your host has internet (or pre-download model). For local hackathon/demo you'll likely have internet.


If PDF text extraction returns empty, try converting the PDF to text manually and use .txt text upload for demo.


If memory is tight, reduce embedding batch sizes.



Final notes & next steps


Copy the files above into the directory structure I provided.


Run locally with uvicorn + streamlit or docker-compose — either works.


Once you have the prototype running, tell me which part you want improved first (better extraction, better matching, nicer UI, multi-agent orchestration, or making it production-like). I’ll then produce the Architecture Diagram, Flowchart, and Wireframes targeted to your hackathon slides.

from typing import List, Dict
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

MODEL_NAME = "all-MiniLM-L6-v2"  # change if desired

class SalesAgent:
    def discover(self, rfp_text: str) -> Dict:
        # Minimal metadata extraction
        title = rfp_text.strip().split("\n")[0][:120]
        return {"title": title, "raw": rfp_text}

class TechnicalAgent:
    def __init__(self, sku_db_path: str):
        self.sku_db = pd.read_csv(sku_db_path)
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2)
        )

        self.sku_texts = (
            self.sku_db["sku_name"].fillna("") + " " +
            self.sku_db["description"].fillna("")
        ).tolist()

        # Fit once on SKU data
        self.sku_vectors = self.vectorizer.fit_transform(self.sku_texts)

    def extract_requirements(self, rfp_text: str):
        lines = [l.strip() for l in rfp_text.splitlines() if l.strip()]
        keywords = ["require", "spec", "specification", "quantity", "qty", "material", "finish"]
        reqs = [l for l in lines if any(k in l.lower() for k in keywords)]

        if not reqs:
            reqs = lines[:6]

        # Deduplicate
        seen = set()
        unique = []
        for r in reqs:
            if r not in seen:
                seen.add(r)
                unique.append(r)
        return unique

    def match_skus(self, requirements, top_k=3):
        req_vectors = self.vectorizer.transform(requirements)
        similarity_matrix = cosine_similarity(req_vectors, self.sku_vectors)

        results = {}
        for i, row in enumerate(similarity_matrix):
            top_indices = row.argsort()[::-1][:top_k]
            hits = []
            for idx in top_indices:
                hits.append({
                    "sku_id": str(self.sku_db.iloc[idx]["sku_id"]),
                    "sku_name": str(self.sku_db.iloc[idx]["sku_name"]),
                    "score": float(row[idx]),
                    "unit_price": float(self.sku_db.iloc[idx].get("unit_price", 0) or 0)
                })
            results[i] = hits
        return results
        
class PricingAgent:
    def estimate_pricing(self, sku_hits: Dict[int, List[Dict]]) -> List[Dict]:
        pricing = []
        for req_id, hits in sku_hits.items():
            # choose top hit as default
            top = hits[0]
            unit_price = top.get("unit_price", 100.0) or 100.0
            qty = 1
            testing_cost = 0.05 * unit_price  # 5% testing placeholder
            margin_pct = 0.2  # 20% margin default
            total = qty * (unit_price + testing_cost) * (1 + margin_pct)
            pricing.append({
                "sku_id": top["sku_id"],
                "sku_name": top["sku_name"],
                "unit_price": unit_price,
                "quantity": qty,
                "testing_cost": testing_cost,
                "margin_pct": margin_pct,
                "total": total
            })
        return pricing

class MasterAgent:
    def compile_response(self, rfp_title: str, requirements: List[str], sku_matches: Dict[int, List[Dict]], pricing: List[Dict], out_path: str):
        # Creates a simple PDF report
        c = canvas.Canvas(out_path, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 40, f"RFP Response: {rfp_title}")
        c.setFont("Helvetica", 10)
        y = height - 70
        c.drawString(40, y, "Requirements & Matched SKUs:")
        y -= 20
        for i, req in enumerate(requirements):
            c.setFont("Helvetica-Bold", 9)
            c.drawString(50, y, f"{i+1}. {req[:120]}")
            y -= 14
            for hit in sku_matches.get(i, []):
                c.setFont("Helvetica", 9)
                c.drawString(64, y, f"- SKU: {hit['sku_name']} (id: {hit['sku_id']}), score: {hit['score']:.3f}, unit_price: {hit.get('unit_price',0)}")
                y -= 12
            y -= 6
            if y < 120:
                c.showPage()
                y = height - 40
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, "Pricing Summary:")
        y -= 18
        c.setFont("Helvetica", 9)
        for p in pricing:
            c.drawString(50, y, f"- {p['sku_name']} | unit: {p['unit_price']:.2f} | qty: {p['quantity']} | testing: {p['testing_cost']:.2f} | margin%: {p['margin_pct']*100:.0f} | total: {p['total']:.2f}")
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 40
        c.save()
        return out_path

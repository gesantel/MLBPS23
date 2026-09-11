import logging
import pickle
import time
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Logging setup — this is what lets you point to real request/latency logs
# in interviews, matching the "serving latency, throughput" language
# already in your consulting resume bullets.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("mlb-run-predictor")

MODEL_PATH = Path(__file__).parent / "pipeline.pkl"

app = FastAPI(
    title="MLB Postseason Run Predictor",
    description="Predicts team runs from in-game hitting statistics using a trained scikit-learn Pipeline.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Load model once at startup, not per-request
# ---------------------------------------------------------------------------
pipeline = None


@app.on_event("startup")
def load_model():
    global pipeline
    with open(MODEL_PATH, "rb") as f:
        pipeline = pickle.load(f)
    logger.info("Model loaded from %s", MODEL_PATH)


# ---------------------------------------------------------------------------
# Request schema — mirrors the exact columns the pipeline was trained on.
# Pydantic validates types and required fields before the model ever runs.
# ---------------------------------------------------------------------------
class GameStats(BaseModel):
    doubles: float
    triples: float
    home_runs: float
    strike_outs: float
    walks: float
    stolen_bases: float
    left_on_base: float
    slug: float
    ops: float
    obp: float
    at_bats: float
    extra_base_hits: float
    xbh_rate: float
    walk_rate: float

    class Config:
        json_schema_extra = {
            "example": {
                "doubles": 6,
                "triples": 1,
                "home_runs": 2,
                "strike_outs": 9,
                "walks": 4,
                "stolen_bases": 1,
                "left_on_base": 7,
                "slug": 0.452,
                "ops": 0.781,
                "obp": 0.329,
                "at_bats": 34,
                "extra_base_hits": 9,
                "xbh_rate": 0.264,
                "walk_rate": 0.105,
            }
        }


class PredictionResponse(BaseModel):
    predicted_runs: float
    latency_ms: float


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": pipeline is not None}


@app.post("/predict", response_model=PredictionResponse)
def predict(stats: GameStats):
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start = time.perf_counter()
    df = pd.DataFrame([stats.model_dump()])

    try:
        prediction = pipeline.predict(df)[0]
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {e}")

    latency_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "Prediction served | predicted_runs=%.3f | latency_ms=%.2f",
        prediction, latency_ms,
    )

    return PredictionResponse(predicted_runs=round(float(prediction), 3), latency_ms=round(latency_ms, 2))

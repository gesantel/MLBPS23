# MLB Postseason Run Predictor API

A FastAPI service wrapping a trained scikit-learn `Pipeline`
(`ColumnTransformer` + `RandomForestRegressor`) that predicts team runs
from in-game hitting statistics. Built, containerized, and deployed
end-to-end as a portfolio project demonstrating the full path from a
trained model to a live production endpoint.

**Live API:** https://mlb-predictor-240528909633.us-central1.run.app
**Interactive docs:** https://mlb-predictor-240528909633.us-central1.run.app/docs
**Docker image:** [gesantel/mlb-predictor](https://hub.docker.com/r/gesantel/mlb-predictor) on Docker Hub

---

## What it does

Given a set of in-game hitting statistics (doubles, home runs, OBP, OPS,
etc.), the API returns a predicted number of runs for that game. The
underlying model was trained on 2023–2025 MLB postseason offensive data
and correctly predicted 82% of 2025 postseason results with an average
run error of ~1.2 per team.

## Try it live

```bash
curl -X POST https://mlb-predictor-240528909633.us-central1.run.app/predict \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": 1, "doubles": 6, "triples": 1, "home_runs": 2,
    "strike_outs": 9, "walks": 4, "stolen_bases": 1, "left_on_base": 7,
    "slug": 0.452, "ops": 0.781, "obp": 0.329, "at_bats": 34,
    "extra_base_hits": 9, "xbh_rate": 0.264, "walk_rate": 0.105
  }'
```

Expected response:
```json
{"predicted_runs": 8.16, "latency_ms": 36.53}
```

Or skip curl entirely and use the [interactive Swagger UI](https://mlb-predictor-240528909633.us-central1.run.app/docs)
to send requests from the browser.

## Endpoints

| Method | Path       | Description                                   |
|--------|------------|------------------------------------------------|
| GET    | `/health`  | Confirms the service is up and the model loaded |
| POST   | `/predict` | Returns a predicted run count for a game's stats |

---

## How it was built and deployed

1. **Model** — trained offline in `notebooks/MLB23_PS_Offense.ipynb`,
   serialized with `pickle` as `api/pipeline.pkl`.
2. **API** — wrapped the pipeline in FastAPI (`api/main.py`), with
   Pydantic request validation and structured request logging
   (latency, predicted value, per-request `game_id`) for observability.
3. **Containerized** — built with Docker, verified locally on Apple
   Silicon (ARM64), then explicitly rebuilt for `linux/amd64` to match
   Cloud Run's target architecture:
   ```bash
   docker build --platform linux/amd64 -t mlb-predictor .
   ```
4. **Published** — pushed the image to Docker Hub as a public repository:
   ```bash
   docker tag mlb-predictor gesantel/mlb-predictor:latest
   docker push gesantel/mlb-predictor:latest
   ```
5. **Deployed** — to Google Cloud Run, pulling directly from Docker Hub:
   ```bash
   gcloud run deploy mlb-predictor \
     --image docker.io/gesantel/mlb-predictor:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8000 \
     --memory 512Mi
   ```
6. **Verified** — identical predictions confirmed across all four
   environments: local Python, local Docker (ARM64), local Docker
   (AMD64 under emulation), and the live Cloud Run deployment.

## Viewing logs

```bash
gcloud run services logs read mlb-predictor --region us-central1
```

Or via the [Cloud Console log viewer](https://console.cloud.google.com/run/detail/us-central1/mlb-predictor/logs?project=mlb-predictor-gsantel).

## Local development

```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Known limitation

`game_id` is currently a required model input because it was included
as a numeric feature during training. It's likely non-predictive (a
database identifier rather than a real statistic) and is a candidate
for removal in a future retraining pass.

# MLB Postseason Run Predictor API

A FastAPI service wrapping a trained scikit-learn `Pipeline`
(`ColumnTransformer` + `RandomForestRegressor`) that predicts team runs
from in-game hitting statistics.

Already tested end-to-end in this environment:
- `GET /health` → confirms the model loaded
- `POST /predict` → returns a prediction for a valid payload
- Missing/invalid fields correctly return `422`

---

## Step 3 — Run and test locally (no Docker yet)

```bash
cd mlb-api
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI — you
can send test requests from the browser using the built-in example payload.

Or from the command line:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": 1, "doubles": 6, "triples": 1, "home_runs": 2,
    "strike_outs": 9, "walks": 4, "stolen_bases": 1, "left_on_base": 7,
    "slug": 0.452, "ops": 0.781, "obp": 0.329, "at_bats": 34,
    "extra_base_hits": 9, "xbh_rate": 0.264, "walk_rate": 0.105
  }'
```

Expected: `{"predicted_runs": 8.16, "latency_ms": ...}`

---

## Step 3b — Build and run with Docker

```bash
docker build -t mlb-predictor .
docker run -p 8000:8000 mlb-predictor
```

Then hit the same `curl` command above — it should return an identical
prediction. If it does, the containerized environment matches your local
one and you're ready to push.

**Troubleshooting:**
- If `docker build` fails installing scikit-learn, check your Docker
  daemon has internet access and isn't behind a restrictive proxy.
- If predictions differ from your local run, check for a scikit-learn
  version mismatch — this Dockerfile pins `scikit-learn==1.7.2` to match
  what `pipeline.pkl` was trained on.

---

## Step 4 — Push to a registry

**Option A: Docker Hub (simplest)**
```bash
docker login
docker tag mlb-predictor YOUR_DOCKERHUB_USERNAME/mlb-predictor:latest
docker push YOUR_DOCKERHUB_USERNAME/mlb-predictor:latest
```

**Option B: Google Artifact Registry (if heading straight to Cloud Run)**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

gcloud artifacts repositories create mlb-predictor-repo \
  --repository-format=docker \
  --location=us-central1

docker tag mlb-predictor \
  us-central1-docker.pkg.dev/YOUR_PROJECT_ID/mlb-predictor-repo/mlb-predictor:latest

gcloud auth configure-docker us-central1-docker.pkg.dev

docker push \
  us-central1-docker.pkg.dev/YOUR_PROJECT_ID/mlb-predictor-repo/mlb-predictor:latest
```

---

## Step 5 — Deploy to Google Cloud Run

```bash
gcloud run deploy mlb-predictor \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/mlb-predictor-repo/mlb-predictor:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi
```

This returns a public HTTPS URL. Test it the same way:

```bash
curl -X POST https://YOUR-CLOUD-RUN-URL/predict \
  -H "Content-Type: application/json" \
  -d '{ ... same payload ... }'
```

**Notes:**
- `--allow-unauthenticated` makes it publicly callable, which you want for
  a portfolio demo. Remove it if you'd rather require an auth token.
- Cloud Run scales to zero when idle, so it stays within the free tier for
  demo-level traffic.
- `--memory 512Mi` is usually enough for a RandomForestRegressor of modest
  size; increase if the container fails to start with an OOM error.

---

## Step 6 — Logging and monitoring (already built in)

`main.py` logs every prediction with `game_id`, the predicted value, and
latency in milliseconds. On Cloud Run, these logs flow automatically into
**Cloud Logging** — no extra setup needed. To view them:

```bash
gcloud run services logs read mlb-predictor --region us-central1
```

This is the concrete evidence behind resume language like "evaluating
serving latency" — you can point to real logs from a real deployment.

---

## Step 7 — What to update afterward

**GitHub README** (this file, adapted): document the API, Docker, and
Cloud Run setup so anyone can reproduce the deployment.

**Resume bullet** (suggested rewrite once live):

> Deployed the trained regression model as a containerized FastAPI service
> on Google Cloud Run, replacing local-only inference with a public
> HTTPS prediction endpoint; added structured request logging for latency
> and throughput monitoring.

---

## Known caveat to resolve before showing this off

`game_id` is currently a required input field because it's part of the
pipeline's numeric features. If it's a database identifier rather than a
meaningful predictor, it's worth retraining without it — an ID shouldn't
influence a run prediction, and its presence may raise a question in an
interview. Worth checking your original training notebook.

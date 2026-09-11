# MLB Postseason Run Prediction

Predicting team runs from in-game hitting statistics using a random
forest regression model, trained on 2023–2025 MLB postseason offensive
data and deployed as a live production API.

**Live API:** https://mlb-predictor-240528909633.us-central1.run.app
**Interactive docs:** https://mlb-predictor-240528909633.us-central1.run.app/docs
**Docker image:** [gesantel/mlb-predictor](https://hub.docker.com/r/gesantel/mlb-predictor)

---

## The story

This started as a question: why did the 2023 Arizona Diamondbacks have
such an effective run-generating offense during their World Series run,
and could the same approach help predict outcomes in the 2025
postseason?

The project grew from a data exploration notebook into a fully deployed
service:

1. **Data** ([`data/`](data/)) — hitting statistics pulled from the MLB
   StatsAPI for postseason teams.
2. **Modeling** ([`notebooks/`](notebooks/)) — exploratory analysis,
   feature engineering, and training a `RandomForestRegressor` inside a
   scikit-learn `Pipeline`, evaluated with MSE. The model predicted 82%
   of 2025 postseason results correctly, with an average run error of
   ~1.2 per team.
3. **Interactive demo** ([`streamlit_app/`](streamlit_app/)) — a
   Streamlit app for exploring predictions and team comparisons in the
   browser.
4. **Production API** ([`api/`](api/)) — the trained model wrapped in a
   FastAPI service, containerized with Docker, and deployed to Google
   Cloud Run with an automated CI/CD pipeline via GitHub Actions. Every
   push to `main` that touches `api/` rebuilds, re-tests, and
   redeploys automatically — see
   [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).

## Project structure

```
MLBPS23/
├── data/                    # Raw and processed hitting statistics (CSV)
├── notebooks/               # Exploratory analysis and model training
│   ├── MLB23_PS_Offense.ipynb
│   └── postseason.py        # Helper functions used by the notebook
├── streamlit_app/           # Interactive browser demo
│   ├── app.py
│   └── requirements.txt
├── api/                     # Production FastAPI service
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pipeline.pkl
│   └── README.md            # API-specific docs, endpoints, deployment details
├── .github/workflows/
│   └── deploy.yml           # CI/CD: build, push, deploy on every push to main
└── README.md                # you are here
```

## Try the live model

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

Full endpoint documentation, local dev setup, and deployment details are
in [`api/README.md`](api/README.md).

## Tech stack

Python, scikit-learn, pandas, FastAPI, Docker, Google Cloud Run,
GitHub Actions, Streamlit, MLB StatsAPI.

## How this was built

The model and data pipeline were built and trained independently. The
deployment infrastructure — Docker, Cloud Run, and the GitHub Actions
CI/CD pipeline — was built with AI assistance (Claude) as a way to
learn DevOps practices hands-on: debugging real errors, understanding
each tool's purpose, and verifying every step rather than copying
commands blindly.

## Known limitation

`game_id` is currently included as a model feature; it's likely a
non-predictive identifier rather than a meaningful statistic and is a
candidate for removal in a future retraining pass.

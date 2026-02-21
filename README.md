# Cloud Cost Spike Detector (FinOps ML)

An end-to-end Machine Learning system designed to detect abnormal cloud cost spikes, forecast spending, and empower FinOps and DevOps teams with proactive cost intelligence.

This project demonstrates modern ML engineering, time-series anomaly detection, and business-focused decision systems.

⸻

# Why this project?

Cloud costs are unpredictable and often increase due to:
• Auto-scaling misconfigurations
• Deployment errors
• Resource leaks
• Overprovisioning
• Pricing model mismatches

Most organizations detect cost spikes too late, leading to budget overruns.

This system enables:
• Early detection
• Forecasting
• Business-level insights
• Cost accountability

⸻

# Key Capabilities

✔️ Executive Dashboard
• Spend trends
• Forecasting and burn rate
• Budget risk visibility
• Service-level breakdown
• FinOps metrics

✔️ ML-powered Anomaly Detection
• Isolation Forest model
• Time-series feature engineering
• Rolling statistical baselines
• Cost deviation detection
• Explainable anomaly scoring

✔️ FinOps Intelligence
• Forecast monthly spend
• Detect abnormal spikes
• Estimate financial impact
• Recommend optimization actions

✔️ Enterprise Ready
• REST APIs for integration
• Dockerized deployment
• CI/CD pipeline ready
• Scalable architecture

⸻

# Machine Learning Design

This system uses:
• Time-series feature engineering
• Rolling mean and standard deviation
• Percent change and deviation signals
• Isolation Forest anomaly detection
• Business explainability layer

# Why Isolation Forest?

It is:
• Scalable
• Robust to outliers
• Suitable for cloud cost anomaly detection
• Efficient for real-time use

# System Architecture:

flowchart TB
%% =======================
%% Cloud Cost Spike Detector (FinOps ML)
%% =======================

subgraph Sources[Cloud Billing Sources]
A1[AWS CUR / Cost & Usage Report]
A2[Azure Cost Export]
A3[GCP Billing Export]
end

subgraph Ingestion[Ingestion & Storage]
B1[Batch Loader / ETL\n(Pandas / Airflow optional)]
B2[(Object Storage)\nS3 / GCS / Blob]
B3[(Analytics Store)\nPostgres / DuckDB]
end

subgraph ML[ML + Feature Engineering]
C1[Feature Builder\nRolling stats, pct-change, seasonality]
C2[Model Service\nIsolation Forest + thresholds]
C3[Explainability\nImpact vs baseline, top services]
end

subgraph API[Serving Layer]
D1[FastAPI\n/detect\n/detect/summary]
D2[Schema Validation\nPydantic]
end

subgraph UI[Executive Dashboard]
E1[Streamlit UI\nKPIs + Trends + Breakdowns]
E2[Recommendations\nRightsizing / Tag hygiene / Spot checks]
end

subgraph Observability[Ops & Observability]
F1[Logs\nStructured JSON]
F2[Metrics\nLatency, errors, anomaly rate]
F3[Tracing\nAPI request traces]
end

subgraph CICD[Delivery]
G1[GitHub Actions\nTests + Lint + Build]
G2[Docker Images\nAPI + UI]
G3[Deploy\nVM / K8s / Cloud Run]
end

Sources --> B1 --> B2
B2 --> B3
B3 --> C1 --> C2 --> C3
C3 --> D1
D2 --> D1
D1 --> E1 --> E2

D1 --> F1
D1 --> F2
D1 --> F3

G1 --> G2 --> G3

## 🧩 System Design (Production-ready)

### Goals

- Detect abnormal spend spikes quickly and reliably
- Provide executive-level spend visibility (KPIs, forecast, budget risk)
- Explain “what changed” (service-level impact, baseline comparison)
- Support integration via API for FinOps automation

### Non-Goals (for MVP)

- Real-time streaming ingestion (batch is enough)
- Fully automated remediation (recommendations first)

---

## 🔁 Data Flow

1. **Ingestion**
   - Billing exports (AWS/Azure/GCP) are ingested as CSV (MVP)
   - Production: scheduled ETL loads into storage + analytics DB

2. **Feature Engineering**
   - Rolling mean/std, percent change, deviation from baseline
   - Optional: day-of-week and monthly seasonality features

3. **ML Detection**
   - Isolation Forest predicts anomaly points per service/day
   - Post-processing converts model output into business events:
     - spike magnitude
     - baseline comparison
     - estimated impact ($ above baseline)

4. **Serving**
   - FastAPI exposes:
     - `POST /detect` returns anomaly table
     - `POST /detect/summary` returns executive summary

5. **Dashboard**
   - Streamlit consumes API outputs and shows:
     - Total spend, burn rate, forecast
     - Service breakdown
     - Spike table (ranked by impact)
     - Recommended actions

---

## 📈 Scaling Strategy

### Compute

- For small/medium datasets: Pandas is sufficient
- For large billing data:
  - Replace Pandas with Polars/Spark
  - Pre-aggregate daily spend per service in DB
  - Cache results for repeated dashboard queries

### Storage

- Store raw exports in object storage (S3/GCS/Blob)
- Store cleaned daily aggregates in Postgres/DuckDB
- Optional: time-series DB if real-time telemetry is added

### API

- Stateless FastAPI containers behind a load balancer
- Horizontal scaling based on CPU/RPS
- Add request size limits and timeouts for safety

---

## 🛡️ Reliability & Resilience

- Input validation (schema + required columns)
- Graceful handling of:
  - empty files
  - missing columns
  - parse errors
  - invalid dates/cost values
- Timeouts + error messages surfaced cleanly in UI
- Health endpoint `/health` for service readiness

---

## 🔐 Security Considerations

- Never log raw billing data in plaintext logs
- For production:
  - AuthN/AuthZ (JWT/OAuth)
  - TLS everywhere
  - Secrets via vault (not in repo)
  - Rate limiting on API endpoints
  - Data retention policy (FinOps compliance)

---

## 🔎 Observability (Production)

Track:

- API latency p50/p95
- error rate
- anomaly rate per day
- top impacted services
- model drift signals (baseline shifts)

Logs:

- structured JSON logs (request_id, file_id, row_count, anomaly_count)

---

## 🧠 Model Monitoring & Drift

Production failure modes:

- seasonal billing patterns cause false positives
- one-time large purchases may appear as anomalies
- missing tags can shift service attribution

Mitigations:

- allow service-level thresholds
- compare to seasonal baseline (DOW / monthly)
- monitor anomaly rate trends and re-tune parameters

---

## ⚖️ Trade-offs (Design Decisions)

- Isolation Forest chosen for:
  - simplicity + robustness
  - fast inference
  - minimal training requirements
- Batch detection chosen for MVP:
  - aligns with billing export cadence
  - easier to deploy and demo to leadership
- UI separated from API:
  - independent scaling
  - secure API integration path

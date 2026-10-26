# ChurnGuard — End-to-End MLOps + DevSecOps Platform

A production-grade machine learning service that predicts customer churn, deployed on AWS with a full MLOps lifecycle and security baked into every stage. Built end-to-end: data → model → API → container → CI/CD → Kubernetes → monitoring → drift detection.

**Live prediction service** served from a 2-replica Kubernetes deployment on Amazon EKS, behind an AWS load balancer, with Prometheus/Grafana observability and Evidently-based data-drift detection.

---

## Architecture

```
Developer ──push──> GitHub ──triggers──> GitHub Actions CI/CD
                                              │
                    ┌─────────────────────────┤
                    │  train → test → Bandit   │
                    │  gitleaks → Trivy → build │
                    └─────────────────────────┘
                                              │
                                        docker push
                                              ▼
                                      Amazon ECR (scan-on-push)
                                              │
                                        image pull
                                              ▼
┌──────────────────── Amazon EKS (Kubernetes) ────────────────────┐
│                                                                  │
│   AWS Load Balancer ──> churnguard Service ──> 2x Pods (FastAPI) │
│                                                       │          │
│                                                  /metrics        │
│                                                       ▼          │
│              Prometheus ──scrape──> Grafana (dashboards)         │
│                                                                  │
└────────────────────────────────────────────────────────────────────┘

Offline: Evidently data-drift report (training vs production distribution)
Infra:   Terraform (VPC, subnets, NAT, EKS cluster, ECR, IAM, KMS)
```

## Tech Stack

| Layer | Tools |
|-------|-------|
| **ML** | scikit-learn (Gradient Boosting), MLflow (experiment tracking + registry) |
| **Serving** | FastAPI, Pydantic validation, Uvicorn |
| **Container** | Docker (non-root, healthcheck), Amazon ECR |
| **CI/CD** | GitHub Actions |
| **Security** | Bandit (SAST), Gitleaks (secrets), Trivy (image CVEs), Checkov-ready IaC, ECR scan-on-push |
| **Infra as Code** | Terraform (VPC + EKS + ECR modules) |
| **Orchestration** | Amazon EKS (Kubernetes 1.31) |
| **Monitoring** | Prometheus, Grafana (kube-prometheus-stack) |
| **ML Monitoring** | Evidently (data-drift detection) |

## Model

- **Dataset:** IBM Telco Customer Churn (7,043 customers, 19 features)
- **Algorithm:** Gradient Boosting Classifier in a scikit-learn Pipeline (preprocessing + model as one artifact, so serving applies identical transforms to training)
- **Performance:** ROC-AUC 0.84, Accuracy 0.80

## MLOps Lifecycle

1. **Train** — `src/train.py` cleans data, trains the pipeline, logs params/metrics to MLflow, saves the model artifact.
2. **Serve** — `src/app.py` loads the model and exposes `/predict`, `/health`, and `/metrics` (Prometheus) endpoints.
3. **CI/CD** — every push runs tests + four security scans, then builds and (on the runner) validates the image.
4. **Provision** — Terraform stands up the VPC and EKS cluster reproducibly.
5. **Deploy** — Kubernetes Deployment (2 replicas, liveness/readiness probes, resource limits, non-root securityContext) + LoadBalancer Service.
6. **Monitor** — Prometheus scrapes the API via a ServiceMonitor; Grafana dashboards show request rate, latency (p50/p95), and error rate.
7. **Detect drift** — `src/drift_check.py` compares production-shaped data against the training distribution and flags drifted features.

## Security (DevSecOps)

Security is enforced at every stage, not bolted on:

- **Code** — Bandit static analysis on every push
- **Secrets** — Gitleaks scans git history for leaked credentials
- **Dependencies & image** — Trivy scans the container for HIGH/CRITICAL CVEs; ECR re-scans on push
- **Runtime** — containers run as a non-root user (UID 1000), `allowPrivilegeEscalation: false`, enforced resource limits
- **Cloud** — IAM instance role (no long-lived keys on disk), KMS-encrypted EKS secrets, IMDSv2 required on nodes
- **Supply chain** — MLflow's skops-based model-integrity check on save

## Repository Layout

```
churnguard-mlops/
├── src/
│   ├── train.py           # training + MLflow logging
│   ├── app.py             # FastAPI serving + Prometheus metrics
│   └── drift_check.py     # Evidently data-drift report
├── tests/
│   └── test_app.py        # API tests (run in CI)
├── k8s/
│   ├── deployment.yaml     # 2 replicas, probes, securityContext
│   ├── service.yaml        # LoadBalancer
│   └── servicemonitor.yaml # Prometheus scrape config
├── infra/
│   ├── main.tf            # ECR repository
│   └── eks.tf             # VPC + EKS cluster
├── .github/workflows/
│   └── ci.yml             # test + security scans + build
├── Dockerfile             # non-root, healthcheck
└── requirements.txt
```

## Running It

**Train the model:**
```bash
python src/train.py
```

**Serve locally:**
```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000
```

**Predict:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"gender":"Female","SeniorCitizen":0,"Partner":"Yes",...}'
# -> {"churn_probability": 0.63, "churn": true}
```

**Provision infra:**
```bash
cd infra && terraform init && terraform apply
```

**Deploy to EKS:**
```bash
kubectl apply -f k8s/
```

## Author

**Syed Muhammad Tahoor Ali** — DevOps & Cloud Engineer
GitHub: [github.com/tahoorshah](https://github.com/tahoorshah) · Medium: [medium.com/@tahoorshah](https://medium.com/@tahoorshah)

# Reproducibility Guide & Benchmark Execution Instructions

This document provides exact, deterministic commands to reproduce all unit tests, model benchmarks, accuracy evaluations, agent queries, and full pipeline executions.

---

## 1. Environment Setup

### Prerequisites
- OS: Ubuntu Linux (22.04 LTS or newer)
- GPU: NVIDIA GPU with CUDA 12.x / 13.x (e.g. RTX 4000 Ada / RTX 4080 SUPER)
- Python 3.12 with `uv` package manager installed
- Node.js & `pnpm` (for web frontend)
- FFmpeg 7.x installed at `~/.local/bin/ffmpeg` or on system PATH
- Ollama running locally at `http://127.0.0.1:11434` with model `llama3.1:latest`

### Python Virtual Environment & Dependencies
```bash
cd /home/vu-lab03-pc17/sports_analytics/Sports_Analytics
# Sync dependencies
uv sync --extra cpu
# Ensure onnxruntime-gpu is installed
uv pip install onnxruntime-gpu onnx onnxscript
```

### Environment Configuration (`.env`)
Verify `.env` contains:
```ini
BAI_YOUTUBE_INGEST=true
BAI_LLM_PROVIDER=local
BAI_LOCAL_LLM_URL=http://127.0.0.1:11434/v1
BAI_LOCAL_LLM_MODEL=llama3.1:latest
BAI_LOCAL_LLM_KEY=ollama
BAI_PROFILE=gpu-rtx4000
BAI_CORS_ORIGINS=["*"]
```

---

## 2. Running Test Suites

### Backend Unit & Integration Tests (115 tests)
```bash
uv run pytest -v
```
Expected output: `115 passed, 1 warning` in ~40 seconds.

### Frontend Unit Tests (23 vitest tests)
```bash
cd apps/web && pnpm test
```
Expected output: `5 passed (5 files), 23 passed (23 tests)` in ~1.5 seconds.

---

## 3. Running Hardware & Model Latency Benchmarks
Measures decode throughput, per-model inference latency (p50, p95, p99), and integrated pipeline throughput on the GPU:
```bash
uv run python docs/testing/run_benchmarks.py
```
Output artifact generated: `docs/testing/benchmark_results.json`.

---

## 4. Running Ground-Truth Accuracy Evaluation
Compares platform rally segmentation and winner attribution against manual reference annotations (`Test1_Full_rev.csv`) and validates BWF scoring state invariants:
```bash
uv run python docs/testing/eval_ground_truth.py
```
Output artifact generated: `docs/testing/accuracy_results.json`.

---

## 5. Running AI Analyst Grounding & Adversarial Suite
Executes 7 standard and adversarial prompts against the local Llama 3.1 8B LLM to test grounding, tool calling, and hallucination resistance:
```bash
uv run python docs/testing/eval_agent.py
```
Output artifact generated: `docs/testing/agent_evaluation_results.json`.

---

## 6. Running End-to-End Server & Cloudflare Tunnel

### Start Backend Server
```bash
uv run bai serve --port 8000
```

### Start Cloudflare Tunnel (in background)
```bash
cloudflared tunnel --url http://127.0.0.1:8000
```
Extract public URL from logs:
```bash
grep -i "trycloudflare.com" <tunnel_log>
```

---

## 7. Submitting Real Match Videos for Analysis

### Upload Local Video
```bash
curl -X POST http://127.0.0.1:8000/api/sessions \
  -F "file=@legacy/pipeline/vjepa_setup/sample_rally1.mp4" \
  -F "title=SampleRally"
```

### Ingest YouTube Match Video
```bash
curl -X POST http://127.0.0.1:8000/api/sessions/youtube \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=oFktPRzCxMo", "title": "BWF Match"}'
```

### Poll Analysis Status
```bash
curl http://127.0.0.1:8000/api/sessions/<SESSION_ID>
```
Wait until `status: "analysed"`.

# Self-hosted RAG Platform — learning project

A practice project to learn **local LLM inference** and **RAG fundamentals** from an infrastructure-first angle. Small scale (one user, laptop CPU, tiny model), production-style patterns (containerized, orchestrated, monitored, auto-deployed).

> Production-*like*, not production. Learning scale: single node, small model,
> no real users. The value is in learning the stack hands-on.

## Quick start

```bash
cp .env.example .env
make install
make start
```

`make install` installs Ollama, pulls the model, and creates a venv with dependencies. `make start` launches the model and the service (waiting for the model to become ready).

Then, in another terminal, you can ask questions:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"is it raining today or what is the weather"}' \
  http://localhost:8000/ask
```

The model's behavior is controlled by the system prompt in `./service/prompts/system.txt` — edit the file and restart the service for changes to take effect.

Interactive API documentation is available at `http://localhost:8000/docs`.

## What it does

Answers questions over a given knowledge base. A small open LLM plus a vector database (RAG), all containerized and orchestrated in Kubernetes, with monitoring and automated deployment.

TODO: Better define the goal (which knowedge base? what info? what is the desired flow?)

## Constraints

- Laptop, 16 GB RAM, no GPU — model runs on CPU, model size ~3–8B params, quantized (≈2–5 GB). Infra around it is size-independent.
- Goal is the stack and the engineering around it, not a smart model.

## Layers

Each layer is a finished result on its own.

- [x] **0 — Local model** — LLM inference basics
- [x] **1 — Service** — service design, config separate from code (FastAPI)
- [ ] **2 — RAG** — embeddings, vector search ← *minimal useful version*
- [ ] **3 — Containerization** — Docker, images, volumes
- [ ] **4 — Kubernetes** — real orchestration
- [ ] **5 — Observability** — operating an LLM workload
- [ ] **6 — Evaluation** — measuring LLM answer quality
- [ ] **7 — Deploy automation** — CI/CD, GitOps, IaC

**Minimal useful version:** layers 0–2 (model + RAG, runs locally).
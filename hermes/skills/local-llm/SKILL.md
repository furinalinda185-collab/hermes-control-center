---
name: local-llm
description: "Install and run local GGUF models with llama.cpp."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [llama.cpp, GGUF, local-models, CUDA]
    related_skills: []
---

# Local LLM Skill

Install and run local GGUF models under llama.cpp, sized to the machine's actual RAM/VRAM budget.

## When to Use

- User asks to install, run, serve, or upgrade a local model via llama.cpp.
- Debugging llama.cpp load failures (CUDA out-of-memory) or choosing a quantization level.
- Don't use for: cloud/API models, training or fine-tuning, or other runners (Ollama, vLLM) — different tooling.

## Standing Preference

- Bias to action: pick the reasonable option and install it. Do not run extended model comparisons unless asked.

## Procedure

1. Inventory the machine with `terminal`: `free -h` (available RAM), `nvidia-smi` (free VRAM plus the process list), `df -h` (disk). Done when all three numbers are recorded.
2. Set the budget: resident RAM is roughly file GiB minus GPU-offloaded GiB plus KV cache and context, and must stay under available RAM with margin to spare. When VRAM is small, prefer a MoE with few active parameters and a small KV cache per token. Done when one candidate file is named with its size in GiB.
3. Get exact file sizes from the Hub API tree endpoint (`/api/models/<org>/<repo>/tree/main?recursive=true`) and divide bytes by 2**30. Done when the candidate filename and GiB size are confirmed.
4. Confirm the installed llama.cpp build supports the model's architecture: read `general.architecture` from the GGUF header (range-fetch the first bytes) and check that string appears in the installed `libllama.so` via `strings`. Done when the arch string matches.
5. Download with `scripts/download_gguf.py` (multi-way, resume-aware) as a background `terminal` process and poll the parts directory until assembly completes. Done when the assembled size equals the HEAD Content-Length.
6. Verify with a single-shot run: `llama-cli -m MODEL -ngl N -c 4096 -p "<probe>" -n 60 --seed 42 -st --simple-io` (confirm the non-interactive flags in `--help` first — they drift between builds). Start `-ngl` high and reduce on `cudaMalloc failed`. Done when the run prints generated text plus a tok/s line.
7. Leave a launcher wrapper (e.g. `~/.local/bin/llama-<model>`) defaulting `-ngl` and `-c` via environment overrides. Done when the wrapper exists and is executable.

## Pitfalls

- Check the `nvidia-smi` process list before concluding a model is too big — transient VRAM hogs (games, browsers) masquerade as an undersized GPU, so reduce `-ngl` instead of abandoning the model.
- Context size consumes VRAM: a `-ngl` value that loads at `-c 4096` can OOM at `-c 8192`, so tune both together.
- Chunked downloaders must resume with `Range: bytes=<start+have>-<end>` in append mode — restarting partial chunks silently re-downloads gigabytes.
- Compare sizes in GiB (bytes divided by 2**30): model hubs quote decimal GB while system tools report GiB, and the gap matters at 30+ GiB.
- Never assume llama-cli flags across builds: probe `--help` for the single-shot flags on the installed binary before scripting a verification run.

## Hermes integration

- Read the Hermes provider skill and live provider docs before configuring. Use `hermes config set`, never hand-edit its YAML.
- Serve at least 64K context per slot for Hermes; use `-c 65536 -np 1 --jinja`. A 4K chat launcher is not agent-ready. Verify `/v1/models` reports the actual context rather than merely pinning a larger client limit.
- On constrained NVIDIA hardware, recent llama-server builds support `-ngl auto --fit-target 1536` and quantized KV caches. Check installed help first; fit settings can retain MoE experts on CPU while keeping VRAM headroom.
- Bind to 127.0.0.1 and restrict CORS to localhost. Prefer an on-demand user service and a launcher that checks `/health` before starting Hermes, rather than consuming GPU memory automatically at login.
- Verify an actual Hermes tool-use/tool-result round trip, not just generated text or exit code zero. Local models can fabricate a result despite working tool support; require explicit execution and inspect the event stream.

## Verification

- The model file exists at its final path with the expected byte size.
- A probe run completes with generated text and a reported tok/s rate.
- The launcher wrapper runs the same configuration hands-free.

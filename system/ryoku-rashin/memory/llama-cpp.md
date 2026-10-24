# llama.cpp on this machine

User-local install (no sudo needed). Installed 2026-09-30, switched to CUDA 2026-10-01.

## Layout

- Binaries: `~/.local/opt/llama.cpp/<build>/`, stable path
  `~/.local/opt/llama.cpp/current` -> currently `b11146-cuda` (v0.5.0-dev).
  Prebuilt releases from `ggml-org/llama.cpp`, asset
  `llama-b<build>-bin-ubuntu-<backend>-x64.tar.gz`.
  - `b11146` — Vulkan build (30 MB), kept as fallback.
  - `b11146-cuda` — CUDA 13.4 build (149 MB) + bundled cudart/cublas
    from `cudart-llama-b11146-bin-ubuntu-cuda-13.4-x64.tar.gz` (440 MB),
    extracted into the same dir so `RUNPATH=$ORIGIN` resolves.
    Matches the installed driver (CUDA UMD 13.4). No system CUDA toolkit needed.
- Weights: `~/.local/share/llama.cpp/models/`
  - `LFM2.5-1.2B-Instruct-Q4_K_M.gguf` (default, 731 MB)
  - `LFM2.5-1.2B-Instruct-Q4_0.gguf` (~10-15% faster, slight quality cost)
- Wrappers in `~/.local/bin/`: `llama-cli`, `llama-server`, `lfm`.
  `lfm` is the one to use — it picks the model, offloads all layers and
  picks the device automatically (no `--device` flag for CUDA builds,
  `--device Vulkan1` for Vulkan builds since Vulkan0 is the Intel iGPU):
  - `lfm` — chat
  - `lfm -p "..." -n 200 -st` — one-shot
  - `lfm --server` — OpenAI-compatible API on 127.0.0.1:8080
  - env: `LFM_MODEL`, `LFM_NGL`, `LFM_CTX`, `LFM_DEVICE`, `LFM_PORT`, `LLAMA_DIR`
  - extra CLI args are appended and override the wrapper defaults
    (llama.cpp warns "specified multiple times" but honors the last value)

The upstream tarball keeps binaries and `.so` files together and relies on
`RUNPATH=$ORIGIN`, so **don't symlink the inner binaries into `~/.local/bin`** —
the wrappers exist for that reason.

## Performance (RTX 5070 Ti Laptop, 70W cap)

2026-10-01, LFM2.5-1.2B-Instruct, real `llama-cli` path (`-n 256` story):

| backend | quant | generation |
|---|---|---|
| Vulkan/Vulkan1 | Q4_K_M | ~100 t/s |
| Vulkan/Vulkan1 | Q4_0 | ~95 t/s |
| CUDA | Q4_K_M | ~306 t/s |
| CUDA | Q4_0 | ~350-400 t/s |

CUDA is ~3-4x Vulkan here. `-fa on` and `-ctk/-ctv q8_0` made no measurable
difference on either backend. Full offload confirmed (`17/17 layers to GPU`).

Caveat: measurements were taken with Minecraft (PrismLauncher java, ~3.8 GB
VRAM, 85-99% GPU util at times) contending for the dGPU — expect variance and
somewhat higher numbers with the game closed. The Q4_K_M CUDA number swung
75 -> 306 t/s between runs depending on game load.

## Adding another model

```sh
curl -L -o ~/.local/share/llama.cpp/models/NAME.gguf \
  https://huggingface.co/LiquidAI/<repo>/resolve/main/<file>.gguf
LFM_MODEL=~/.local/share/llama.cpp/models/NAME.gguf lfm
```
Liquid AI ships LFM2.5 at 230M / 350M / 1.2B / 2.6B / 8B-A1B (+ VL, Audio,
Embedding) in GGUF. HF API lists them:
`https://huggingface.co/api/models?author=LiquidAI&search=GGUF`.
Verify a download with the `x-linked-size` response header vs the local byte
count — HF has no `.sha256` sidecar on these repos.

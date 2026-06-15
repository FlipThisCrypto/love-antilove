#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

mkdir -p outputs/images outputs/metadata outputs/prompts outputs/reports

cat <<'MSG'
Setup complete.

For AMD RX 6800 on Linux, install ROCm/PyTorch in your ComfyUI environment separately:
  pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/rocm6.2

Then install/run ComfyUI and point config/collection.yaml at its API URL.
MSG

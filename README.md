# LOVE // ANTILOVE Generator

Local pipeline for generating an 888-piece NFT collection of premium pixel wizard characters.

- LOVE Wizards: `#001` through `#444`
- ANTILOVE Wizards: `#445` through `#888`
- Outputs: PNG images, metadata JSON, prompt text, CSV export, validation logs, rarity report
- Default first pass: dry-run with `3` LOVE and `3` ANTILOVE items

## Folder Layout

```text
love-antilove-generator/
  config/                 Collection, trait, and rarity rules
  prompts/                Base, positive, and negative prompt templates
  scripts/                Generator pipeline scripts
  comfyui/                Starter ComfyUI API workflow template
  outputs/images/         Final PNG files named 001.png through 888.png
  outputs/metadata/       Metadata JSON files named 001.json through 888.json
  outputs/prompts/        Prompt text files named 001.txt through 888.txt
  outputs/reports/        CSV exports, rarity report, validation report, traits source
```

## Quick Start

Linux is preferred for AMD ROCm.

```bash
cd love-antilove-generator
bash scripts/setup.sh
source .venv/bin/activate
```

Dry-run the six-token preview:

```bash
python scripts/generate_traits.py --dry-run
python scripts/generate_prompts.py
python scripts/generate_images.py --mode placeholder
python scripts/create_metadata.py
python scripts/rarity_report.py
python scripts/validate_collection.py --expected 6
```

Run the preview loop against `sample1` through `sample8`:

```bash
python scripts/preview_loop.py --iterations 1 --image-mode placeholder
```

On the ROCm/ComfyUI machine, run real image batches with:

```bash
python scripts/preview_loop.py --iterations 3 --image-mode comfyui
```

Each iteration creates a side-by-side reference/preview contact sheet in `outputs/reports/preview_loop/`. Review that sheet, tune the prompt templates or ComfyUI workflow, and rerun the loop until the batch matches the samples closely enough.

Windows RX 6800 DirectML preview run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_comfyui_directml_rx6800.ps1
python scripts/preview_loop.py --iterations 1 --love 3 --antilove 3 --image-mode comfyui --size 768
```

Retro pixel preview:

```powershell
python scripts/preview_loop.py --iterations 1 --love 3 --antilove 3 --image-mode comfyui --size 768 --pixel-size 8
```

Use `--pixel-size 4`, `6`, or `8` to control how chunky the final pixel treatment feels.

The current local Windows workflow uses ComfyUI installed beside this repo at `../ComfyUI`, with DirectML device index `1`, which maps to the AMD Radeon RX 6800 on this machine. The workflow expects these local ComfyUI model files:

- `../ComfyUI/models/checkpoints/DreamShaperXL_Lightning.safetensors`
- `../ComfyUI/models/loras/extremely detailed.safetensors`
- `../ComfyUI/models/loras/fantasy.safetensors`

It also uses `sample2.png` and `sample4.png` from the workspace root as reference images for img2img style anchoring, then removes the edge-connected white/gray background to produce transparent PNG previews.

Resume a failed or interrupted run:

```bash
python scripts/generate_prompts.py --resume
python scripts/generate_images.py --mode placeholder --resume
python scripts/create_metadata.py --resume
```

Full collection after style approval:

```bash
python scripts/generate_traits.py
python scripts/generate_prompts.py
python scripts/generate_images.py --mode comfyui --resume
python scripts/create_metadata.py --resume
python scripts/rarity_report.py
python scripts/validate_collection.py --expected 888
```

## AMD RX 6800 / ROCm Notes

Use ComfyUI on Linux with a ROCm-compatible PyTorch build. The RX 6800 is RDNA2 and commonly works with ROCm on supported Linux distributions, but exact setup depends on driver, kernel, and ROCm version.

Recommended path:

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/rocm6.2
python main.py --listen 127.0.0.1 --port 8188
```

Then edit `config/collection.yaml` if your ComfyUI URL is different.

## ComfyUI Workflow

`comfyui/workflow_template.json` is a starter API workflow with placeholder tokens:

- `POSITIVE_PROMPT`
- `NEGATIVE_PROMPT`
- `SEED`
- `WIDTH`
- `HEIGHT`
- `OUTPUT_PREFIX`

Replace `REPLACE_WITH_PIXEL_MODEL.safetensors` with an installed SDXL or pixel-art checkpoint. A pixel-art SDXL LoRA can also be added directly in ComfyUI; if you add nodes, update `scripts/generate_images.py` to map prompts into your exported API workflow.

The script queues jobs in ComfyUI mode. Copy or configure generated files into `outputs/images/001.png` through `outputs/images/888.png` before metadata validation.

Fallback options:

- `--mode placeholder`: creates transparent test PNGs so metadata and validation can be reviewed.
- CPU ComfyUI: slower, but usable for small batches.
- Web/API image generation: generate externally using `outputs/prompts/*.txt`, then place PNGs into `outputs/images/`.

## Art Rules

The prompts enforce:

- character-only wizard sprite
- full body, centered composition
- transparent background when possible
- no text, captions, logos, UI panels, frames, borders, watermarks, or numbers
- clean sharp pixel edges

LOVE uses soft light traits: hearts, rose petals, pink/white robes, gold trim, hopeful expressions.

ANTILOVE uses playful gothic traits: broken hearts, thorns, dark robes, crimson/purple accents, mischievous expressions, dark humor accessories.

## Metadata

Every JSON file contains:

- `name`
- `description`
- `image`
- `edition`
- `alignment`
- `attributes`
- `collection`
- `rewards note`

Names are deterministic:

- `LOVE Wizard #001` through `LOVE Wizard #444`
- `ANTILOVE Wizard #445` through `ANTILOVE Wizard #888`

Before minting, update these in `config/collection.yaml`:

- `image_base_uri`
- `metadata_base_uri`
- project descriptions if needed
- rewards note if project terms change

## Rarity

Per alignment:

- Common: 300
- Uncommon: 100
- Rare: 35
- Epic: 8
- Legendary: 1

The generator assigns rarity first, then chooses traits from the alignment-specific trait pools. `outputs/reports/traits.csv` and `outputs/reports/collection.csv` are the minting prep spreadsheets.

## Minting Prep

1. Generate or replace all images in `outputs/images/`.
2. Upload images to IPFS or your storage provider.
3. Replace `image_base_uri` in `config/collection.yaml`.
4. Re-run:

```bash
python scripts/create_metadata.py
python scripts/rarity_report.py
python scripts/validate_collection.py --expected 888
```

5. Upload `outputs/metadata/`.
6. Replace contract base URI with the final metadata URI.
7. Keep `outputs/reports/collection.csv` as the human-readable trait index.

## File Naming

Use zero-padded editions everywhere:

- Image: `outputs/images/001.png`
- Metadata: `outputs/metadata/001.json`
- Prompt: `outputs/prompts/001.txt`

Do not rename files after metadata is created unless you also regenerate metadata.

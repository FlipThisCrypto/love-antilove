# Rollback: Ornate Reference Workflow

This file preserves the working setup that produced the ornate chibi wizard previews approved before the retro pixel experiment.

Git commit containing this setup:

```text
6aa57b3 Wire ComfyUI DirectML preview generation
```

## Run Command

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_comfyui_directml_rx6800.ps1
python scripts/preview_loop.py --iterations 1 --love 3 --antilove 3 --image-mode comfyui --size 768
```

## Local ComfyUI Setup

ComfyUI install:

```text
I:\love-antilove\ComfyUI
```

Launch mode:

```text
--directml 1
```

On this machine, DirectML device index `1` maps to:

```text
AMD Radeon RX 6800
```

## Required Model Files

Checkpoint:

```text
../ComfyUI/models/checkpoints/DreamShaperXL_Lightning.safetensors
```

LoRAs:

```text
../ComfyUI/models/loras/extremely detailed.safetensors
../ComfyUI/models/loras/fantasy.safetensors
```

Reference images:

```text
../sample2.png  # LOVE reference
../sample4.png  # ANTILOVE reference
```

## LOVE Prompt Template

```text
extremely detailed fantasy, premium ornate chibi fantasy wizard character, single wizard only, full body, centered, pure white empty background for easy cutout, high-end collectible sticker character, crisp clean anime illustration, sharp line art. Mandatory composition: oversized decorated wizard hat with dangling heart charms, large expressive eyes, layered pink white lavender robe with lace-like gold trim, tiny boots, jeweled heart brooches, massive ornate winged heart-shaped staff almost as tall as the character held on the left side, one cute magical cat or bird familiar near the feet, floating heart charms, soft sparkles, rose petals, pastel white pink lavender and warm gold palette, hopeful sweet expression, dense accessory detail like the supplied sample images, clean silhouette, no scenery, no words, no letters, no readable signs, no logo, no UI, no border.

Trait match: {trait_sentence}
Rarity direction: {rarity_sentence}
```

## ANTILOVE Prompt Template

```text
extremely detailed fantasy, premium ornate chibi gothic fantasy wizard character, single wizard only, full body, centered, pure white empty background for easy cutout, high-end collectible sticker character, crisp clean anime illustration, sharp line art. Mandatory composition: oversized crooked witch hat with dangling broken-heart charms and thorns, large expressive mischievous red eyes, layered black charcoal robe with crimson magenta and purple trim, tiny boots, skull charms, gothic heart brooches, massive ornate thorned broken-heart staff almost as tall as the character held on the left side, one cute black cat or bat familiar near the feet, floating broken heart charms, shadow smoke, black rose petals, playful spooky dark-humor props with no readable writing, dense accessory detail like the supplied sample images, clean silhouette, no scenery, no words, no letters, no readable signs, no logo, no UI, no border.

Trait match: {trait_sentence}
Rarity direction: {rarity_sentence}
```

## Negative Prompt

```text
worst quality, low quality, bad anatomy, text, words, letters, readable sign, caption, logo, watermark, signature, artist name, frame, border, trading card, UI panel, number, gray background, scenery, room, landscape, multiple wizards, duplicate wizard, duplicate character, extra character, character sheet, turnaround, blurry, realistic photo, 3d render, flat vector icon, plain blocky sprite, simple staff, plain hat, cropped body, extra limbs, bad hands, gore, explicit violence, nudity.
```

## Workflow Settings

The workflow is reference-guided img2img.

Sampler:

```text
steps: 12
cfg: 3.0
sampler_name: euler
scheduler: sgm_uniform
denoise: 0.72
```

Model chain:

```text
CheckpointLoaderSimple: DreamShaperXL_Lightning.safetensors
LoraLoader: extremely detailed.safetensors, strength_model 1.0, strength_clip 1.0
LoraLoader: fantasy.safetensors, strength_model 0.8, strength_clip 0.8
LoadImage: REFERENCE_IMAGE
VAEEncode -> KSampler -> VAEDecode -> SaveImage
```

## Restore Notes

To restore from Git:

```powershell
git checkout 6aa57b3 -- comfyui/workflow_template.json prompts/love_prompt_template.txt prompts/antilove_prompt_template.txt prompts/negative_prompt.txt scripts/generate_images.py
```

To restore manually, copy the prompt templates and workflow settings from this file back into the matching project files.

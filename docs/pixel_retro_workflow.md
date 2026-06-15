# Pixel Retro Workflow

This is the active experiment for making the LOVE // ANTILOVE wizards feel more like retro pixel RPG sprites while preserving the successful ornate character composition.

## Run Command

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_comfyui_directml_rx6800.ps1
python scripts/preview_loop.py --iterations 1 --love 3 --antilove 3 --image-mode comfyui --size 768 --pixel-size 8
```

Use smaller or larger pixel blocks:

```powershell
python scripts/preview_loop.py --iterations 1 --love 3 --antilove 3 --image-mode comfyui --size 768 --pixel-size 4
python scripts/preview_loop.py --iterations 1 --love 3 --antilove 3 --image-mode comfyui --size 768 --pixel-size 6
python scripts/preview_loop.py --iterations 1 --love 3 --antilove 3 --image-mode comfyui --size 768 --pixel-size 8
```

Recommended review order:

- `--pixel-size 4`: keeps most ornate detail, mild pixel feel
- `--pixel-size 6`: balanced retro treatment
- `--pixel-size 8`: strongest retro sprite look, less facial detail

## LOVE Prompt Template

```text
retro pixel art fantasy wizard sprite, premium 32-bit RPG character, single wizard only, full body, centered, pure white empty background for easy cutout, crisp pixel clusters, visible square pixels, limited palette, clean 1 pixel dark outline, no anti-aliased painterly edges, chibi proportions, ornate but readable sprite details. Mandatory composition: oversized decorated wizard hat with dangling heart charms, large expressive pixel eyes, layered pink white lavender robe with gold trim, tiny boots, jeweled heart brooches, massive winged heart-shaped staff almost as tall as the character held on the left side, one cute pixel cat or bird familiar near the feet, floating heart charms, soft pixel sparkles, rose petals, pastel white pink lavender and warm gold palette, hopeful sweet expression, collectible retro game sprite, clean silhouette, no scenery, no words, no letters, no readable signs, no logo, no UI, no border.

Trait match: {trait_sentence}
Rarity direction: {rarity_sentence}
```

## ANTILOVE Prompt Template

```text
retro pixel art gothic fantasy wizard sprite, premium 32-bit RPG character, single wizard only, full body, centered, pure white empty background for easy cutout, crisp pixel clusters, visible square pixels, limited palette, clean 1 pixel dark outline, no anti-aliased painterly edges, chibi proportions, ornate but readable sprite details. Mandatory composition: oversized crooked witch hat with dangling broken-heart charms and thorns, large expressive mischievous red pixel eyes, layered black charcoal robe with crimson magenta and purple trim, tiny boots, skull charms, gothic heart brooches, massive thorned broken-heart staff almost as tall as the character held on the left side, one cute black pixel cat or bat familiar near the feet, floating broken heart charms, pixel shadow smoke, black rose petals, playful spooky dark-humor props with no readable writing, collectible retro game sprite, clean silhouette, no scenery, no words, no letters, no readable signs, no logo, no UI, no border.

Trait match: {trait_sentence}
Rarity direction: {rarity_sentence}
```

## Negative Prompt

```text
worst quality, low quality, bad anatomy, text, words, letters, readable sign, caption, logo, watermark, signature, artist name, frame, border, trading card, UI panel, number, gray background, scenery, room, landscape, multiple wizards, duplicate wizard, duplicate character, extra character, character sheet, turnaround, blurry, realistic photo, 3d render, painterly, oil painting, smooth airbrush, soft anti aliasing, flat vector icon, simple staff, plain hat, cropped body, extra limbs, bad hands, gore, explicit violence, nudity.
```

## Workflow Settings

The workflow remains reference-guided img2img from the successful ornate setup, but uses a slightly lower denoise value so the sample silhouette stays stable.

```text
steps: 12
cfg: 3.0
sampler_name: euler
scheduler: sgm_uniform
denoise: 0.64
```

Model chain:

```text
CheckpointLoaderSimple: DreamShaperXL_Lightning.safetensors
LoraLoader: extremely detailed.safetensors, strength_model 1.0, strength_clip 1.0
LoraLoader: fantasy.safetensors, strength_model 0.8, strength_clip 0.8
LoadImage: REFERENCE_IMAGE
VAEEncode -> KSampler -> VAEDecode -> background cleanup -> pixelate -> SaveImage
```

## Notes

The retro effect currently comes from both prompt pressure and deterministic postprocessing:

```text
--pixel-size 8
```

That means the art direction is easy to tune without changing model files. For final production, test `4`, `6`, and `8` on a 24-image preview batch before committing to the full 888.

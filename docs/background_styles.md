# Orange Background Styles

The generator now supports 12 orange-family background styles as metadata traits.

## Rarity Mapping

Common backgrounds:

- Amber Wash
- Apricot Glow
- Peach Pixel Mist
- Sunset Flat

Uncommon backgrounds:

- Blood Orange Bloom
- Tangerine Sparks
- Coral Heatwave

Rare backgrounds:

- Ember Halo
- Molten Rose
- Pumpkin Eclipse
- Blockchain Ember Grid
- Tangerine Chainlink

Epic background:

- Infernal Gold
- Tang Gang Flame Wall

Legendary background:

- Solar Blood Moon
- Tang Gang Crown

## Final Collection Behavior

Each NFT receives a `Background` metadata attribute during trait generation.

The background is selected from the tier mapped to the NFT rarity:

```text
Common -> common backgrounds
Uncommon -> uncommon backgrounds
Rare -> rare backgrounds
Epic -> epic background
Legendary -> legendary background
```

This keeps the best, most dramatic background treatments reserved for the rarest NFTs while still giving the common tokens consistent orange-family variation.

## Current Preview

The latest six-image preview uses the 64-bit character style at 1024x1024 with orange backgrounds applied after character generation:

```powershell
python scripts/generate_bit_variants.py --image-mode comfyui --size 1024 --love 3 --antilove 3 --seed 904 --presets 64bit
```

Output:

```text
outputs/variants/64bit/images/
outputs/reports/64bit_orange_bg_sheet.jpg
```

## Prompt-Native Background Mode

The preferred direction is now prompt-native backgrounds: the selected `Background` trait is added to the ComfyUI prompt, and the img2img reference is placed on that same background before sampling. This avoids transparency cleanup and lets the model paint the character and background together.

Run:

```powershell
python scripts/generate_bit_variants.py --image-mode comfyui --size 1024 --love 3 --antilove 3 --seed 904 --presets 64bit --background-mode prompt
```

Output:

```text
outputs/variants/64bit/images/
outputs/reports/64bit_prompt_bg_sheet.jpg
```

## New Preview Styles

Blockchain preview styles:

- Blockchain Ember Grid
- Tangerine Chainlink

Tang Gang rare-preview styles:

- Tang Gang Flame Wall
- Tang Gang Crown

Preview sheet:

```text
outputs/reports/new_background_preview_sheet.jpg
```

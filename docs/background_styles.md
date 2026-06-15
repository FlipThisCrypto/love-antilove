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

Epic background:

- Infernal Gold

Legendary background:

- Solar Blood Moon

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

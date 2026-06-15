# 8-Bit, 16-Bit, and 32-Bit Variant Batch

This batch creates 512x512 preview variants for comparing retro pixel intensity.

Run:

```powershell
python scripts/generate_bit_variants.py --image-mode comfyui --size 512 --love 3 --antilove 3 --seed 900
```

Output folders:

```text
outputs/variants/8bit/images/
outputs/variants/16bit/images/
outputs/variants/32bit/images/
```

Combined comparison sheet:

```text
outputs/reports/bit_variant_sheet.jpg
```

## Presets

8-bit:

```text
style-preset: 8bit
pixel-size: 10
palette-colors: 32
visible RGB colors after alpha cleanup: about 31
```

16-bit:

```text
style-preset: 16bit
pixel-size: 6
palette-colors: 96
visible RGB colors after alpha cleanup: about 92-96
```

32-bit:

```text
style-preset: 32bit
pixel-size: 4
palette-colors: 192
visible RGB colors after alpha cleanup: about 188-191
```

All variants are generated at 512x512 with transparent PNG output where possible.

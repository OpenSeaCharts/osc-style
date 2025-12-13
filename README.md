# OpenSeaCharts Style

You can use the style directly with the following url if your map viewer
supports PMTiles.

```url
https://raw.githubusercontent.com/OpenSeaCharts/osc-style/refs/heads/main/openseacharts.json
```

It is possible to edit the style on [Maputnik](https://maplibre.org/maputnik/).

### Symbols

- [OpenNauticalChart/josm](https://github.com/OpenNauticalChart/josm/tree/master/icons/svg)
- [OpenSeaMap/renderer](https://github.com/OpenSeaMap/renderer/tree/master/searender/symbols)

### Sprite Generation

Sprites are generated using a Python script.

**Requirements:**
- Python 3
- `librsvg2-bin` (for `rsvg-convert`)
- `spreet` (install via `cargo install spreet`)

**Usage:**
```bash
python sprites/generate_sprites.py
```

This script will:
1. Clean up build directories.
2. Copy and resize SVGs for 1x and 2x resolution.
3. Generate sprite sheets (`sprites.json`, `sprites.png`, etc.).
4. Post-process JSON files to add SDF flags.

### CI/CD

A GitHub Workflow (`.github/workflows/update_sprites.yml`) runs on push and PR to ensure that committed sprite files are up to date with the source SVGs.


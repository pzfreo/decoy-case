# decoy-case

[![Build](https://github.com/pzfreo/decoy-case/actions/workflows/build.yml/badge.svg)](https://github.com/pzfreo/decoy-case/actions/workflows/build.yml)
[![Slice](https://github.com/pzfreo/decoy-case/actions/workflows/slice.yml/badge.svg)](https://github.com/pzfreo/decoy-case/actions/workflows/slice.yml)

A small 3D printed enclosure for a [common USB-C decoy board](https://www.amazon.co.uk/dp/B0FNQNY8PT), built with [build123d](https://github.com/gumyr/build123d).

You can customise how tall the entry is for the wire at the back.

## How it works

1. `decoy_case.py` generates two STEP files (base + shell) using build123d
2. CI builds the STEP files on every push/PR
3. [estampo](https://github.com/estampo/estampo) slices them with OrcaSlicer in CI, producing print-ready gcode
4. PRs get a comment with estimated print time and filament usage

## Usage

```bash
pip install build123d
python decoy_case.py
```

This generates `decoy_base.step` and `decoy_shell.step`.

To slice locally:

```bash
pip install estampo
estampo run
```

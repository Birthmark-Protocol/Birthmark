# Birthmark Examples

This directory contains short scripts that demonstrate the intended Birthmark Protocol workflow. At the moment `basic_usage.py` is the only example; it walks through hashing an image, instantiating the camera interface, and outlining the verification step.

## Prerequisites
- Python 3.8 or newer
- Optional but recommended: a virtual environment
- The project installed in editable mode (`pip install -e .`) so the `Birthmark` package is importable

> The example only touches hashing and simulated camera setup. Installing without dependencies (`pip install -e . --no-deps`) is usually enough for a quick run. Install the full dependency set if you plan to explore blockchain or camera integrations later.

## Quick Start
```bash
# From the repository root
python -m venv .venv
source .venv/bin/activate
pip install -e . --no-deps

cd examples
# Provide a sample image that the script can hash
cp /path/to/any/photo.jpg example_image.jpg
# (Optional) create a tiny placeholder file instead
python - <<'PY'
from pathlib import Path
Path('example_image.jpg').write_bytes(b'Birthmark demo image')
PY

# Run the example
python basic_usage.py
```

The script looks for `example_image.jpg` in your current working directory. If it cannot find the file it will emit a warning and skip the hashing step.

## Expected Output
```
Birthmark Protocol - Example Usage
==================================================

=== Example 1: Hash Computation ===
✓ Image Hash: 4ad015d4b1272722419f16571191ee8f678154d8de1ae79d49c4bd6436bf251b
✓ Timestamp: 2025-11-03 01:54:47.612195

=== Example 2: Authenticated Capture ===
✓ Camera initialized: example_camera_001
✓ Network: testnet

⚠️  Actual camera capture not yet implemented
    This is a placeholder showing the intended workflow

=== Example 3: Image Verification ===
⚠️  Verification not yet implemented
    Will check blockchain for hash match

==================================================
✓ Examples complete!
```

Hashes and timestamps will change every run. Examples 2 and 3 intentionally show warnings because the camera capture, metadata persistence, and blockchain interfaces are still stubs.

## Troubleshooting
- **`ModuleNotFoundError: No module named 'birthmark'`** – On Linux and other case-sensitive systems the package currently installs as `Birthmark`. Update the import in `basic_usage.py` to `from Birthmark import ...` (or temporarily alias it in a REPL) before running the example.
- **`example_image.jpg not found`** – Confirm the file exists in the directory you execute the script from. Re-run the placeholder snippet above if you just want a dummy file.

## Next Steps
- Inspect `src/Birthmark/hash.py`, `camera.py`, and `blockchain.py` to see how the example ties into the core modules.
- Flesh out the TODOs in the camera and blockchain interfaces to turn the placeholders into real integrations.

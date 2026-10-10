# LSC Smart Connect Power Strip — Payload Reverse Engineering

Reverse engineering of the scheduled cycle payload format for the **LSC 3211133 Power Strip with USB** (sold by Action).

This project decodes and encodes the base64 payloads used by the device's "Scheduled Cycle" feature, enabling you to programmatically control timer schedules on each of the 3 independently switchable outlets.

## Device

| Feature | Details |
|---|---|
| **Model** | LSC 3211133 |
| **Outlets** | 3 × French standard (3680W total) + USB-A + USB-C |
| **Connectivity** | Wi-Fi 2.4 GHz (IEEE 802.11 b/g/n) |
| **Chip** | BK7231N (Tuya CBU module) |
| **Apps** | LSC Smart Connect / Tuya Smart |

See [device.md](device.md) for the full list of supported device commands (relay status, power/voltage monitoring, child lock, etc.).

## Project Structure

```
lsc-experiment/
├── project.md          # Raw research notes & test data (payload ↔ human-readable mapping)
├── device.md           # Device command reference (switches, sensors, relay, etc.)
├── antigravity/        # First implementation — CLI tools with argparse
│   ├── README.md
│   ├── decode_payload.py
│   ├── encode_payload.py
│   └── test_payloads.py
└── mistral/            # Iteration 2 — JSON-based API + CLI
    ├── README.md
    ├── plan.md
    ├── test.json
    ├── image.png
    └── cycle_time/
        ├── README.md
        ├── decode_payload.py
        ├── encode_payload.py
        └── test_payloads.py
```

### Two implementations

 | Directory | Approach | CLI | API | Tool / Model |
|---|---|---|---|---|
 | **antigravity/** | Argparse CLI — `--cycle` / `--socket` flags | `python decode_payload.py <base64>` | `encode_payload.py --cycle "1,activate,16:10,19:10,once,1,1"` | **Antigravity IDE** (Google) · Gemini 3.1 Pro |
 | **mistral/cycle_time/** | JSON file + Python API | `python decode_payload.py <base64>` (outputs JSON) | `encode_payload.py cycles.json` | **Mistral Vibe CLI** (Mistral) · Mistral Medium 3.5 |

Both implementations share the same underlying binary protocol.

## Binary Protocol

Each scheduled cycle is encoded as a **10-byte** block:

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 1 byte | Socket + Action | Bit 0: `1`=activate, `0`=deactivate · Bits 1-3: socket (0→1, 1→2, 2→3) |
| 1 | 1 byte | Repeat days | Bitmap: bit 0=Sun … bit 6=Sat · `0x00` = once |
| 2–3 | 2 bytes | Start time | Minutes since midnight, big-endian |
| 4–5 | 2 bytes | End time | Minutes since midnight, big-endian |
| 6 | 1 byte | Reserved | Typically `0x00` |
| 7 | 1 byte | Open duration | Minutes |
| 8 | 1 byte | Reserved | Typically `0x00` |
| 9 | 1 byte | Close duration | Minutes |

**Multi-cycle payloads** are simply concatenated 10-byte blocks (no extra header).

### Example

```
Payload: AQADygR+AAEAAQ==
Decoded: Socket 1 · activate · 16:10–19:10 · once · 1min / 1min
```

## Quick Start

```bash
# Decode a payload
python3 antigravity/decode_payload.py "AwAFggW+AAEAAQMAA+gC+AABAAEBAAWCBb4AAQAB"

# Encode a single cycle
python3 antigravity/encode_payload.py \
  --socket 1 --action activate --start 16:10 --end 19:10 \
  --days once --open 1 --close 1

# Encode multiple cycles
python3 antigravity/encode_payload.py \
  --cycle "1,activate,23:30,24:30,once,1,1" \
  --cycle "2,activate,23:30,24:30,once,1,1"

# Run tests
python3 antigravity/test_payloads.py
```

## Requirements

- **Python 3.8+**
- **No external dependencies** — uses only the standard library (`base64`, `struct`, `argparse`, `json`)

## License

This project is provided for **reverse engineering and educational purposes only**. Use at your own risk.

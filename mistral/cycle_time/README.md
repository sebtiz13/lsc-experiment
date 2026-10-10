# Smart Plug Payload Encoder/Decoder

A Python implementation for encoding and decoding payloads for a 3-socket smart power strip.

## Features

- **Decode** base64 payloads into human-readable cycle information
- **Encode** human-readable cycle information into base64 payloads
- Support for single and multi-cycle payloads
- Comprehensive error handling and validation
- Complete test suite covering all examples from the original specification

## Installation

No external dependencies required. Just use Python 3.8+:

```bash
cd smart_plug_payload
```

## Usage

### Decoding Payloads

```bash
python decode_payload.py <base64_payload>
```

Example:
```bash
python decode_payload.py AQADygR+AAEAAQ==
```

Output:
```
Single cycle payload:
  Socket: 1
  Activation: activate
  Time: 16:10-19:10
  Repeat: once
  Open: 1min
  Close: 1min
```

### Encoding Payloads

Create a JSON file with your cycles:

```json
[
  {
    "socket": 1,
    "activation": "activate",
    "start_time": "16:10",
    "end_time": "19:10",
    "repeat": "once",
    "open_duration": "1min",
    "close_duration": "1min"
  },
  {
    "socket": 2,
    "activation": "deactivate",
    "start_time": "00:10",
    "end_time": "23:12",
    "repeat": "Monday,Tuesday",
    "open_duration": "30min",
    "close_duration": "1h"
  }
]
```

Then encode it:

```bash
python encode_payload.py cycles.json
```

Output:
```
Encoded payload: AwAFggW+AAEAAQMAA+gC+AABAAEBAAWCBb4AAQAB
```

## Python API

### Decoding

```python
from decode_payload import decode_payload

payload = "AQADygR+AAEAAQ=="
cycles = decode_payload(payload)

for cycle in cycles:
    print(f"Socket {cycle['socket']}: {cycle['activation']} from {cycle['start_time']}-{cycle['end_time']}")
```

### Encoding

```python
from encode_payload import encode_payload

cycles = [
    {
        "socket": 1,
        "activation": "activate",
        "start_time": "16:10",
        "end_time": "19:10",
        "repeat": "once",
        "open_duration": "1min",
        "close_duration": "1min"
    }
]

payload = encode_payload(cycles)
print(f"Encoded: {payload}")
```

## Payload Structure

### Single Cycle (10 bytes)

| Byte | Description | Format |
|------|-------------|--------|
| 0    | Activation + Socket | Bit 0: activation (0=deactivate, 1=activate), Bits 1-3: socket (0-2) + 1 = 1-3 |
| 1    | Repeat days | Bitmap: Bit 0=Sunday, Bit 1=Monday, ..., Bit 6=Saturday, 0x00=once |
| 2-3  | Start time | Minutes since midnight (big-endian) |
| 4-5  | End time | Minutes since midnight (big-endian) |
| 6    | Reserved | Typically 0x00 |
| 7    | Open duration | Minutes |
| 8    | Reserved | Typically 0x00 |
| 9    | Close duration | Minutes |

### Multi-Cycle

Concatenation of multiple 10-byte single cycle payloads.

## Time Format

- Times are stored as minutes since midnight (0-1439, but can exceed for times crossing midnight)
- Display format: `HH:MM` (24-hour format)
- Example: `16:10` = 970 minutes, `00:30` = 30 minutes or 1470 minutes (24:30)

## Duration Format

Supported formats:
- `30min` - 30 minutes
- `1h` - 1 hour (60 minutes)
- `1h30min` or `1h30` - 1 hour and 30 minutes (90 minutes)
- `60` - 60 minutes (numeric only, assumes minutes)

## Repeat Days

- `once` - No repetition (0x00)
- `Sunday` - Only Sunday (0x01)
- `Monday,Tuesday` - Monday and Tuesday (0x06)
- `Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday` - Every day (0x7F)

## Examples

### Single Cycle Examples

```python
# 1 - activate - 16:10-19:10 - once - 1min - 1min
decode_payload("AQADygR+AAEAAQ==")

# 3 - activate - 18:45-00:00 - once - 1h - 1h
decode_payload("BQAEZQAAADwAPA==")

# 3 - activate - 13:15-23:45 - once - 2h15 - 3h
decode_payload("BQADGwWRAIcAtA==")
```

### Multi-Cycle Examples

```python
# Two cycles: socket 2 and socket 1, both 23:30-00:30
decode_payload("AwAFggW+AAEAAQEABYIFvgABAAE=")

# Three cycles on two sockets
decode_payload("AwAFggW+AAEAAQMAA+gC+AABAAEBAAWCBb4AAQAB")
```

## Testing

Run the comprehensive test suite:

```bash
python test_payloads.py
```

The test suite includes:
- All examples from the original specification
- Single and multi-cycle payloads
- Time edge cases (midnight crossing)
- Various repeat day patterns
- Different duration formats
- Round-trip encoding/decoding verification
- Error handling tests

## Error Handling

The implementation includes comprehensive error handling for:

- Invalid base64 payloads
- Invalid time formats
- Invalid duration formats
- Invalid socket numbers (must be 1-3)
- Invalid activation values
- Invalid repeat day specifications
- Missing required fields

## Implementation Details

- Pure Python, no external dependencies
- Type hints for better code clarity
- Comprehensive docstrings
- Command-line interfaces for easy usage
- Modular design for easy maintenance

## License

This implementation is provided as-is for reverse engineering and educational purposes. Use at your own risk.

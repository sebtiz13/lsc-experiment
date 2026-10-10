# Smart Plug Payload Tools

This project provides Python scripts to decode and encode the schedule payloads for a 3-socket smart power strip. It allows you to generate base64 strings required to configure the device's "Scheduled Cycle" feature and interpret existing payloads.

## Files

- `decode_payload.py`: Decodes a base64 payload into a readable table.
- `encode_payload.py`: Encodes schedule parameters into a base64 payload.
- `test_payloads.py`: Runs verification tests against known examples.

## Usage

### Decoding a Payload

Use `decode_payload.py` to view the details of a base64 string.

```bash
python3 decode_payload.py <base64_string>
```

**Example:**
```bash
python3 decode_payload.py "AwAFggW+AAEAAQMAA+gC+AABAAEBAAWCBb4AAQAB"
```

**Output:**
```
Socket   Action     Start  End    Days                 Open       Close
---------------------------------------------------------------------------
2        activate   23:30  24:30  once                 1min       1min
2        activate   16:40  12:40  once                 1min       1min
1        activate   23:30  24:30  once                 1min       1min
```

### Encoding a Payload

Use `encode_payload.py` to generate a base64 string from schedule parameters.

#### Single Cycle
You can specify a single cycle using individual arguments:

```bash
python3 encode_payload.py --socket 1 --action activate --start 16:10 --end 19:10 --days once --open 1 --close 1
```

**Arguments:**
- `--socket`: Socket number (1, 2, or 3).
- `--action`: Action to perform (`activate` or `deactivate`).
- `--start`: Start time in `HH:MM` format.
- `--end`: End time in `HH:MM` format.
  - **Note**: Use `24:xx`, `25:xx`, etc., if the end time is on the next day relative to the start time (e.g., start `23:30`, end `24:30` for 00:30 the next day).
- `--days`: Days of the week (e.g., `Mon,Tue`, `Sunday`, or `once`).
- `--open`: Open duration in minutes.
- `--close`: Close duration in minutes.

#### Multiple Cycles
To encode multiple cycles in a single payload, use the `--cycle` argument repeatedly. The format is `"socket,action,start,end,days,open,close"`.

```bash
python3 encode_payload.py \
  --cycle "2,activate,23:30,24:30,once,1,1" \
  --cycle "2,activate,16:40,12:40,once,1,1" \
  --cycle "1,activate,23:30,24:30,once,1,1"
```

## Testing

Run the provided test script to verify the tools against known valid examples:

```bash
python3 test_payloads.py
```

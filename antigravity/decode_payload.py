import sys
import argparse
import base64
import struct

def parse_days(day_mask):
    if day_mask == 0:
        return "once"

    days = []
    day_map = {
        1: "Sun",
        2: "Mon",
        4: "Tue",
        8: "Wed",
        16: "Thu",
        32: "Fri",
        64: "Sat"
    }

    for val, name in day_map.items():
        if day_mask & val:
            days.append(name)

    return ",".join(days)

def format_time(minutes):
    hh = minutes // 60
    mm = minutes % 60
    return f"{hh:02d}:{mm:02d}"

def decode_payload(payload_b64):
    try:
        # Pad if necessary
        missing_padding = len(payload_b64) % 4
        if missing_padding:
            payload_b64 += '=' * (4 - missing_padding)

        data = base64.b64decode(payload_b64)
    except Exception as e:
        print(f"Error decoding base64: {e}")
        sys.exit(1)

    if len(data) % 10 != 0:
        print(f"Warning: Payload length {len(data)} is not a multiple of 10 bytes.")

    print(f"{'Socket':<8} {'Action':<10} {'Start':<6} {'End':<6} {'Days':<20} {'Open':<10} {'Close':<10}")
    print("-" * 75)

    for i in range(0, len(data), 10):
        chunk = data[i:i+10]
        if len(chunk) < 10:
            break

        # Parse chunk
        # Byte 0: Socket << 1 | State
        b0 = chunk[0]
        socket_id = (b0 >> 1) + 1
        state = b0 & 1
        action = "activate" if state == 1 else "deactivate"

        # Byte 1: Days
        days = parse_days(chunk[1])

        # Bytes 2-3: Start Time (Big Endian)
        start_min = struct.unpack(">H", chunk[2:4])[0]
        start_time = format_time(start_min)

        # Bytes 4-5: End Time (Big Endian)
        end_min = struct.unpack(">H", chunk[4:6])[0]
        end_time = format_time(end_min)

        # Bytes 6-7: Open Duration
        open_val = struct.unpack(">H", chunk[6:8])[0]

        # Bytes 8-9: Close Duration
        close_val = struct.unpack(">H", chunk[8:10])[0]

        # Format duration (simple min logic or hm)
        # Assuming just minutes for display
        open_str = f"{open_val}min"
        close_str = f"{close_val}min"

        print(f"{socket_id:<8} {action:<10} {start_time:<6} {end_time:<6} {days:<20} {open_str:<10} {close_str:<10}")

def main():
    parser = argparse.ArgumentParser(description="Decode Smart Plug Payload")
    parser.add_argument("payload", help="Base64 encoded payload string")

    args = parser.parse_args()
    decode_payload(args.payload)

if __name__ == "__main__":
    main()

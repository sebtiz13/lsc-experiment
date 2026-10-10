import argparse
import base64
import struct
import sys

def parse_time(time_str):
    try:
        hh, mm = map(int, time_str.split(':'))
        return hh * 60 + mm
    except ValueError:
        print(f"Error: Invalid time format '{time_str}'. Use HH:MM.")
        sys.exit(1)

def parse_days_input(days_str):
    if days_str.lower() == "once":
        return 0

    day_map = {
        "sun": 1,
        "mon": 2,
        "tue": 4,
        "wed": 8,
        "thu": 16,
        "fri": 32,
        "sat": 64,
        "sunday": 1,
        "monday": 2,
        "tuesday": 4,
        "wednesday": 8,
        "thursday": 16,
        "friday": 32,
        "saturday": 64
    }

    mask = 0
    days = days_str.lower().split(',')
    for d in days:
        d = d.strip()
        if d in day_map:
            mask |= day_map[d]
        else:
            print(f"Error: Unknown day '{d}'. Use full names or abbreviations (e.g., Mon,Tue).")
            sys.exit(1)
    return mask

def encode_cycle(socket, action, start_time, end_time, days, open_dur, close_dur):
    # Byte 0: Socket << 1 | State
    socket_idx = int(socket) - 1
    state = 1 if action.lower() == "activate" else 0
    b0 = (socket_idx << 1) | state

    # Byte 1: Days
    b1 = parse_days_input(days)

    # Bytes 2-3: Start Time (Big Endian)
    start_min = parse_time(start_time)

    # Bytes 4-5: End Time (Big Endian)
    end_min = parse_time(end_time)

    # Bytes 6-7: Open Duration
    try:
        open_val = int(open_dur)
    except ValueError:
        print(f"Error: Open duration '{open_dur}' must be an integer (minutes).")
        sys.exit(1)

    # Bytes 8-9: Close Duration
    try:
        close_val = int(close_dur)
    except ValueError:
        print(f"Error: Close duration '{close_dur}' must be an integer (minutes).")
        sys.exit(1)

    return struct.pack(">BBHHHH", b0, b1, start_min, end_min, open_val, close_val)

def main():
    parser = argparse.ArgumentParser(description="Encode Smart Plug Payload")

    # Allow multiple cycles using the --cycle argument
    # Format: "socket,action,start,end,days,open,close"
    parser.add_argument("--cycle", action="append", help="Cycle definition: 'socket,action,start,end,days,open,close'")

    # Keep original individual arguments for single cycle convenience
    parser.add_argument("--socket", type=int, choices=[1, 2, 3], help="Socket number (1-3)")
    parser.add_argument("--action", choices=["activate", "deactivate"], help="Action (activate/deactivate)")
    parser.add_argument("--start", help="Start time in HH:MM")
    parser.add_argument("--end", help="End time in HH:MM")
    parser.add_argument("--days", help="Days (e.g. 'Mon,Tue' or 'Once')")
    parser.add_argument("--open", help="Open duration in minutes")
    parser.add_argument("--close", help="Close duration in minutes")

    args = parser.parse_args()

    packed_data = b""

    # Process individual arguments if provided
    if all([args.socket, args.action, args.start, args.end, args.days, args.open, args.close]):
        packed_data += encode_cycle(args.socket, args.action, args.start, args.end, args.days, args.open, args.close)

    # Process multiple cycles
    if args.cycle:
        for cycle_str in args.cycle:
            parts = cycle_str.split(',')
            if len(parts) != 7:
                print(f"Error: Invalid cycle format '{cycle_str}'. Expected 7 comma-separated values.")
                sys.exit(1)
            packed_data += encode_cycle(*parts)

    if not packed_data:
        print("Error: No cycle information provided. Use --cycle or individual arguments.")
        parser.print_help()
        sys.exit(1)

    # Encode Base64
    encoded = base64.b64encode(packed_data).decode('utf-8')
    print(encoded)

if __name__ == "__main__":
    main()

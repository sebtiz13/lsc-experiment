#!/usr/bin/env python3
"""
Smart Plug Payload Encoder

Encode human-readable cycle information into base64 payloads for smart power strip.
"""

import base64
import struct
import re
from typing import List, Dict, Union


def encode_payload(cycles: List[Dict[str, Union[str, int]]]) -> str:
    """
    Encode cycle information into base64 payload.

    Args:
        cycles: List of cycle dictionaries with keys:
                - socket: Socket number (1-3)
                - activation: 'activate' or 'deactivate'
                - start_time: Start time in HH:MM format
                - end_time: End time in HH:MM format
                - repeat: Repeat days or 'once'
                - open_duration: Open duration in human-readable format
                - close_duration: Close duration in human-readable format

    Returns:
        Base64 encoded payload string

    Raises:
        ValueError: If input data is invalid or cannot be encoded
    """
    if not cycles:
        raise ValueError("At least one cycle is required")

    # Validate and encode each cycle
    encoded_cycles = []
    for cycle in cycles:
        encoded_cycles.append(_encode_single_cycle(cycle))

    # Create payload
    if len(encoded_cycles) == 1:
        # Single cycle payload (no header)
        payload_bytes = encoded_cycles[0]
    else:
        # Multi-cycle payload with header
        payload_bytes = _create_multi_cycle_payload(encoded_cycles)

    # Base64 encode
    return base64.b64encode(payload_bytes).decode('ascii')


def _create_multi_cycle_payload(encoded_cycles: List[bytes]) -> bytes:
    """Create multi-cycle payload with proper header."""
    # No header for multi-cycle payloads, just concatenate 10-byte cycles
    return b''.join(encoded_cycles)


def _encode_single_cycle(cycle: Dict) -> bytes:
    """Encode a single cycle into 12-byte format."""
    # Validate required fields
    required_fields = ['socket', 'activation', 'start_time', 'end_time', 'repeat',
                       'open_duration', 'close_duration']
    for field in required_fields:
        if field not in cycle:
            raise ValueError(f"Missing required field: {field}")

    # Validate socket number
    socket_num = int(cycle['socket'])
    if socket_num not in [1, 2, 3]:
        raise ValueError(f"Socket number must be 1-3, got {socket_num}")

    # Validate activation
    activation = cycle['activation'].lower()
    if activation not in ['activate', 'deactivate']:
        raise ValueError(f"Activation must be 'activate' or 'deactivate', got {activation}")

    # Convert times to minutes, using original values if available for accurate re-encoding
    if '_original_start_minutes' in cycle and '_original_end_minutes' in cycle:
        start_minutes = cycle['_original_start_minutes']
        end_minutes = cycle['_original_end_minutes']
    else:
        start_minutes = time_to_minutes(cycle['start_time'])
        end_minutes = time_to_minutes(cycle['end_time'])

    # Convert repeat days to bitmap
    repeat_bitmap = days_to_bitmap(cycle['repeat'])

    # Convert durations to minutes
    open_minutes = duration_to_minutes(cycle['open_duration'])
    close_minutes = duration_to_minutes(cycle['close_duration'])

    # Byte 0: activation flag (bit 0) + socket number (bits 1-3)
    byte0 = 0x00
    if activation == 'activate':
        byte0 |= 0x01  # Set bit 0 for activate

    # Socket number (1-3) -> (0-2) for bits 1-3
    socket_value = socket_num - 1
    byte0 |= (socket_value & 0x07) << 1  # Set bits 1-3 for socket number

    # Byte 1: repeat days bitmap
    repeat_bitmap = days_to_bitmap(cycle['repeat'])

    # Pack all fields into 10-byte structure
    cycle_bytes = struct.pack(
        'B', byte0  # Byte 0: socket + activation
    ) + struct.pack(
        'B', repeat_bitmap  # Byte 1: repeat days bitmap
    ) + struct.pack(
        '>H', start_minutes  # Bytes 2-3: start time (big-endian)
    ) + struct.pack(
        '>H', end_minutes  # Bytes 4-5: end time (big-endian)
    ) + struct.pack(
        'B', repeat_bitmap  # Byte 6: repeat days
    ) + struct.pack(
        'B', open_minutes  # Byte 7: open duration (minutes)
    ) + struct.pack(
        'B', 0x00  # Byte 8: unknown/reserved
    ) + struct.pack(
        'B', close_minutes  # Byte 9: close duration (minutes)
    )

    return cycle_bytes


def time_to_minutes(time_str: str) -> int:
    """
    Convert HH:MM time string to minutes since midnight.

    Args:
        time_str: Time string in HH:MM format (24-hour)

    Returns:
        Minutes since midnight

    Raises:
        ValueError: If time format is invalid
    """
    try:
        hours, mins = map(int, time_str.split(':'))
        if hours < 0 or hours > 23:
            raise ValueError(f"Hours must be 0-23, got {hours}")
        if mins < 0 or mins > 59:
            raise ValueError(f"Minutes must be 0-59, got {mins}")
        return hours * 60 + mins
    except ValueError as e:
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM")


def days_to_bitmap(days_str: str) -> int:
    """
    Convert repeat days string to bitmap.

    Args:
        days_str: Comma-separated day names or 'once'
                 Example: 'once', 'Monday', 'Sunday,Monday,Tuesday'

    Returns:
        Bitmap where each bit represents a day
        Bit 0 = Sunday, Bit 1 = Monday, ..., Bit 6 = Saturday
        0x00 = once

    Raises:
        ValueError: If day names are invalid
    """
    if days_str.lower() == 'once':
        return 0x00

    day_names = {
        'sunday': 0,
        'monday': 1,
        'tuesday': 2,
        'wednesday': 3,
        'thursday': 4,
        'friday': 5,
        'saturday': 6
    }

    bitmap = 0x00
    day_list = [day.strip().lower() for day in days_str.split(',')]

    for day in day_list:
        if day not in day_names:
            raise ValueError(f"Invalid day name: {day}")
        bitmap |= (1 << day_names[day])

    return bitmap


def duration_to_minutes(duration_str: str) -> int:
    """
    Convert human-readable duration to minutes.

    Args:
        duration_str: Duration string in formats like:
                      '1min', '30min', '1h', '2h15min', '1h30min'

    Returns:
        Duration in minutes

    Raises:
        ValueError: If duration format is invalid
    """
    duration_str = duration_str.lower().strip()

    # Handle simple minutes format (e.g., '30min', '1min')
    min_match = re.match(r'^(\d+)min$', duration_str)
    if min_match:
        return int(min_match.group(1))

    # Handle simple hours format (e.g., '1h', '2h')
    hour_match = re.match(r'^(\d+)h$', duration_str)
    if hour_match:
        return int(hour_match.group(1)) * 60

    # Handle combined format (e.g., '1h30min', '2h15min', '2h15')
    combined_match = re.match(r'^(\d+)h(\d+)(min)?$', duration_str)
    if combined_match:
        hours = int(combined_match.group(1))
        minutes = int(combined_match.group(2))
        return hours * 60 + minutes

    # Handle format without units (e.g., '60', '90') - assume minutes
    if duration_str.isdigit():
        return int(duration_str)

    raise ValueError(f"Invalid duration format: {duration_str}. "
                    f"Expected formats: '30min', '1h', '1h30min'")


def main():
    """Command-line interface for encoding payloads."""
    import sys
    import json

    if len(sys.argv) != 2:
        print("Usage: python encode_payload.py <cycles_json_file>")
        print("Example: python encode_payload.py cycles.json")
        print("\nCycles JSON format:")
        print("[")
        print("  {")
        print("    \"socket\": 1,")
        print("    \"activation\": \"activate\",")
        print("    \"start_time\": \"16:10\",")
        print("    \"end_time\": \"19:10\",")
        print("    \"repeat\": \"once\",")
        print("    \"open_duration\": \"1min\",")
        print("    \"close_duration\": \"1min\"")
        print("  }")
        print("]")
        sys.exit(1)

    json_file = sys.argv[1]

    try:
        with open(json_file, 'r') as f:
            cycles = json.load(f)

        payload = encode_payload(cycles)
        print(f"Encoded payload: {payload}")

    except FileNotFoundError:
        print(f"Error: File {json_file} not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

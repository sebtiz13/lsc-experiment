#!/usr/bin/env python3
"""
Smart Plug Payload Decoder

Decode base64 payloads from smart power strip into human-readable format.
"""

import base64
import struct
from typing import List, Dict, Union


def decode_payload(base64_payload: str) -> List[Dict[str, Union[str, int]]]:
    """
    Decode a base64 payload into human-readable cycle information.

    Args:
        base64_payload: Base64 encoded payload string

    Returns:
        List of dictionaries, each representing a cycle with keys:
        - socket: Socket number (1-3)
        - activation: 'activate' or 'deactivate'
        - start_time: Start time in HH:MM format
        - end_time: End time in HH:MM format
        - repeat: Repeat days or 'once'
        - open_duration: Open duration in human-readable format
        - close_duration: Close duration in human-readable format

    Raises:
        ValueError: If payload is invalid or cannot be decoded
    """
    try:
        # Decode base64 to bytes
        payload_bytes = base64.b64decode(base64_payload)

        # Check if this is a multi-cycle payload (has header)
        # Multi-cycle payloads seem to start with non-zero and have length that's multiple of 10
        if len(payload_bytes) > 10 and len(payload_bytes) % 10 == 0:
            # Multi-cycle payload format
            return _decode_multi_cycle_payload(payload_bytes)
        else:
            # Single cycle payload
            return [_decode_single_cycle(payload_bytes)]

    except (base64.binascii.Error, struct.error, IndexError) as e:
        raise ValueError(f"Invalid payload format: {e}")


def _decode_multi_cycle_payload(payload_bytes: bytes) -> List[Dict]:
    """Decode a multi-cycle payload."""
    cycles = []

    # No header for multi-cycle payloads, just concatenated 10-byte cycles
    cycle_count = len(payload_bytes) // 10

    # Each cycle is 10 bytes
    for i in range(cycle_count):
        start_idx = i * 10
        end_idx = start_idx + 10
        cycle_bytes = payload_bytes[start_idx:end_idx]

        if len(cycle_bytes) != 10:
            raise ValueError(f"Invalid cycle data length at cycle {i}")

        cycles.append(_decode_single_cycle(cycle_bytes))

    return cycles


def _decode_single_cycle(cycle_bytes: bytes) -> Dict:
    """Decode a single 10-byte cycle."""
    if len(cycle_bytes) != 10:
        raise ValueError(f"Expected 10 bytes for single cycle, got {len(cycle_bytes)}")

    # Byte 0: activation flag (bit 0) + socket number (bits 1-3)
    byte0 = cycle_bytes[0]
    is_activated = (byte0 & 0x01) != 0  # Bit 0: 0=deactivate, 1=activate
    socket_num = ((byte0 >> 1) & 0x07) + 1  # Bits 1-3: socket number (0-2) + 1 = 1-3

    # Byte 1: repeat days bitmap
    repeat_bitmap = cycle_bytes[1]

    # Bytes 2-3: start time (minutes since midnight, big-endian)
    start_minutes = struct.unpack('>H', cycle_bytes[2:4])[0]

    # Bytes 4-5: end time (minutes since midnight, big-endian)
    end_minutes = struct.unpack('>H', cycle_bytes[4:6])[0]

    # Byte 6: unknown/reserved
    # reserved_byte6 = cycle_bytes[6]

    # Byte 7: open duration (minutes)
    open_minutes = cycle_bytes[7]

    # Byte 8: unknown/reserved
    # reserved_byte8 = cycle_bytes[8]

    # Byte 9: close duration (minutes)
    close_minutes = cycle_bytes[9]

    return {
        'socket': socket_num,
        'activation': 'activate' if is_activated else 'deactivate',
        'start_time': minutes_to_time(start_minutes),
        'end_time': minutes_to_time(end_minutes),
        'repeat': decode_repeat_days(repeat_bitmap),
        'open_duration': format_duration(open_minutes),
        'close_duration': format_duration(close_minutes),
        # Store original time values for accurate re-encoding
        '_original_start_minutes': start_minutes,
        '_original_end_minutes': end_minutes
    }


def minutes_to_time(minutes: int) -> str:
    """
    Convert minutes since midnight to HH:MM format.

    Args:
        minutes: Minutes since midnight (can be > 1440 for times crossing midnight)

    Returns:
        Time string in HH:MM format
    """
    # Handle times that cross midnight by using modulo for display
    # but preserve the original value for encoding
    display_minutes = minutes % (24 * 60)

    hours = display_minutes // 60
    mins = display_minutes % 60

    return f"{hours:02d}:{mins:02d}"


def decode_repeat_days(bitmap: int) -> str:
    """
    Convert repeat days bitmap to human-readable format.

    Args:
        bitmap: Byte where each bit represents a day
               Bit 0 = Sunday, Bit 1 = Monday, ..., Bit 6 = Saturday
               0x00 = once

    Returns:
        String describing repeat pattern
    """
    if bitmap == 0x00:
        return "once"

    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    selected_days = []

    for i in range(7):
        if bitmap & (1 << i):
            selected_days.append(day_names[i])

    return ",".join(selected_days)


def format_duration(minutes: int) -> str:
    """
    Format duration in minutes to human-readable format.

    Args:
        minutes: Duration in minutes

    Returns:
        Formatted string (e.g., "1h", "30min", "2h15")
    """
    if minutes == 0:
        return "0min"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours > 0 and remaining_minutes > 0:
        return f"{hours}h{remaining_minutes}"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{minutes}min"


def main():
    """Command-line interface for decoding payloads."""
    import sys
    import json

    if len(sys.argv) != 2:
        print("Usage: python decode_payload.py <base64_payload>")
        print("Example: python decode_payload.py AQADygR+AAEAAQ==")
        sys.exit(1)

    payload = sys.argv[1]

    try:
        cycles = decode_payload(payload)

        # Create a clean output without internal fields
        clean_cycles = []
        for cycle in cycles:
            clean_cycle = {
                'socket': cycle['socket'],
                'activation': cycle['activation'],
                'start_time': cycle['start_time'],
                'end_time': cycle['end_time'],
                'repeat': cycle['repeat'],
                'open_duration': cycle['open_duration'],
                'close_duration': cycle['close_duration']
            }
            clean_cycles.append(clean_cycle)

        # Output as JSON array
        print(json.dumps(clean_cycles, indent=2))

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

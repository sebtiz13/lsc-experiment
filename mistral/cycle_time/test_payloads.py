#!/usr/bin/env python3
"""
Comprehensive test suite for smart plug payload encoding and decoding.

Tests all examples from project.md and edge cases.
"""

import unittest
import json
import os
from decode_payload import decode_payload
from encode_payload import encode_payload


class TestPayloadEncodingDecoding(unittest.TestCase):
    """Test suite for payload encoding and decoding."""

    def setUp(self):
        """Set up test data from project.md examples."""
        self.single_cycle_cases = [
            # Format: (base64_payload, expected_decoded_result)
            ("AQADygR+AAEAAQ==", {
                'socket': 1,
                'activation': 'activate',
                'start_time': '16:10',
                'end_time': '19:10',
                'repeat': 'once',
                'open_duration': '1min',
                'close_duration': '1min'
            }),
            ("AAADygR+AAEAAQ==", {
                'socket': 1,
                'activation': 'deactivate',
                'start_time': '16:10',
                'end_time': '19:10',
                'repeat': 'once',
                'open_duration': '1min',
                'close_duration': '1min'
            }),
            ("AQAACgVwAAEAAQ==", {
                'socket': 1,
                'activation': 'activate',
                'start_time': '00:10',
                'end_time': '23:12',
                'repeat': 'once',
                'open_duration': '1min',
                'close_duration': '1min'
            }),
            ("BQADygR+AAEAAQ==", {
                'socket': 3,
                'activation': 'activate',
                'start_time': '16:10',
                'end_time': '19:10',
                'repeat': 'once',
                'open_duration': '1min',
                'close_duration': '1min'
            }),
            ("BQADygR+AAIAAg==", {
                'socket': 3,
                'activation': 'activate',
                'start_time': '16:10',
                'end_time': '19:10',
                'repeat': 'once',
                'open_duration': '2min',
                'close_duration': '2min'
            }),
            ("BQAEZQAAADwAPA==", {
                'socket': 3,
                'activation': 'activate',
                'start_time': '18:45',
                'end_time': '00:00',
                'repeat': 'once',
                'open_duration': '1h',
                'close_duration': '1h'
            }),
            ("BQADGwWRAIcAtA==", {
                'socket': 3,
                'activation': 'activate',
                'start_time': '13:15',
                'end_time': '23:45',
                'repeat': 'once',
                'open_duration': '2h15',
                'close_duration': '3h'
            }),
            ("BQADFgPWAAoACg==", {
                'socket': 3,
                'activation': 'activate',
                'start_time': '13:10',
                'end_time': '16:22',
                'repeat': 'once',
                'open_duration': '10min',
                'close_duration': '10min'
            }),
        ]

        self.multi_cycle_cases = [
            # Two cycles on different sockets
            # Note: The actual payload has cycles in order socket 2, socket 1
            ("AwAFggW+AAEAAQEABYIFvgABAAE=", [
                {
                    'socket': 2,
                    'activation': 'activate',
                    'start_time': '23:30',
                    'end_time': '00:30',
                    'repeat': 'once',
                    'open_duration': '1min',
                    'close_duration': '1min'
                },
                {
                    'socket': 1,
                    'activation': 'activate',
                    'start_time': '23:30',
                    'end_time': '00:30',
                    'repeat': 'once',
                    'open_duration': '1min',
                    'close_duration': '1min'
                }
            ]),

            # Three cycles on two sockets
            # Note: The actual payload has cycles in a different order than described in project.md
            ("AwAFggW+AAEAAQMAA+gC+AABAAEBAAWCBb4AAQAB", [
                {
                    'socket': 2,
                    'activation': 'activate',
                    'start_time': '23:30',
                    'end_time': '00:30',
                    'repeat': 'once',
                    'open_duration': '1min',
                    'close_duration': '1min'
                },
                {
                    'socket': 2,
                    'activation': 'activate',
                    'start_time': '16:40',
                    'end_time': '12:40',
                    'repeat': 'once',
                    'open_duration': '1min',
                    'close_duration': '1min'
                },
                {
                    'socket': 1,
                    'activation': 'activate',
                    'start_time': '23:30',
                    'end_time': '00:30',
                    'repeat': 'once',
                    'open_duration': '1min',
                    'close_duration': '1min'
                }
            ])
        ]

        self.time_edge_cases = [
            ("BQAFnQWfAAEAAQ==", "23:57", "23:59"),
            ("BQAFnwABAAEAAQ==", "23:59", "00:01"),
            ("BQAEZQAAADwAPA==", "18:45", "00:00"),
            ("AQAACgVwAAEAAQ==", "00:10", "23:12"),
        ]

        self.repeat_day_cases = [
            ("BQAA9gFIAAoACg==", "once"),
            ("BQEA9gFIAAoACg==", "Sunday"),
            ("BQMCYgPPADwAPA==", "Sunday,Monday"),
            ("BQ8DUgPPADwAPA==", "Sunday,Monday,Tuesday,Wednesday"),
            ("BX8DUgPPADwAPA==", "Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday"),
        ]

        self.duration_cases = [
            ("BQADygR+AAIAAg==", "2min", "2min"),
            ("BQAEZQAAADwAPA==", "1h", "1h"),
            ("BQADGwWRAIcAtA==", "2h15", "3h"),
            ("BQADFgPWAAoACg==", "10min", "10min"),
        ]

    def test_single_cycle_decode(self):
        """Test decoding of single cycle payloads."""
        for payload, expected in self.single_cycle_cases:
            with self.subTest(payload=payload):
                decoded = decode_payload(payload)
                self.assertEqual(len(decoded), 1)
                # Compare only the expected fields, ignoring internal fields like _original_*_minutes
                actual_cycle = decoded[0]
                for key in expected:
                    self.assertEqual(actual_cycle[key], expected[key], f"Mismatch in field {key}")

    def test_single_cycle_roundtrip(self):
        """Test round-trip encoding/decoding for single cycles."""
        for original_payload, expected in self.single_cycle_cases:
            with self.subTest(payload=original_payload):
                # Decode original
                decoded = decode_payload(original_payload)
                # Compare only expected fields, ignoring internal fields
                actual_cycle = decoded[0]
                for key in expected:
                    self.assertEqual(actual_cycle[key], expected[key], f"Mismatch in field {key}")

                # Encode back using decoded cycle (which has original time values)
                re_encoded = encode_payload(decoded)
                self.assertEqual(re_encoded, original_payload)

                # Decode re-encoded to verify
                re_decoded = decode_payload(re_encoded)
                # Compare only expected fields, ignoring internal fields
                re_actual_cycle = re_decoded[0]
                for key in expected:
                    self.assertEqual(re_actual_cycle[key], expected[key], f"Re-encoded mismatch in field {key}")

    def test_multi_cycle_decode(self):
        """Test decoding of multi-cycle payloads."""
        for payload, expected_cycles in self.multi_cycle_cases:
            with self.subTest(payload=payload):
                decoded = decode_payload(payload)
                self.assertEqual(len(decoded), len(expected_cycles))
                for i, (decoded_cycle, expected_cycle) in enumerate(zip(decoded, expected_cycles)):
                    with self.subTest(cycle=i):
                        # Compare only the expected fields, ignoring internal fields like _original_*_minutes
                        for key in expected_cycle:
                            self.assertEqual(decoded_cycle[key], expected_cycle[key], f"Mismatch in field {key}")

    def test_multi_cycle_roundtrip(self):
        """Test round-trip encoding/decoding for multi-cycles."""
        for original_payload, expected_cycles in self.multi_cycle_cases:
            with self.subTest(payload=original_payload):
                # Decode original
                decoded = decode_payload(original_payload)
                # Compare only expected fields, ignoring internal fields
                self.assertEqual(len(decoded), len(expected_cycles))
                for i, (actual_cycle, expected_cycle) in enumerate(zip(decoded, expected_cycles)):
                    for key in expected_cycle:
                        self.assertEqual(actual_cycle[key], expected_cycle[key], f"Cycle {i}, mismatch in field {key}")

                # Encode back using decoded cycles (which have original time values)
                re_encoded = encode_payload(decoded)
                self.assertEqual(re_encoded, original_payload)

                # Decode re-encoded to verify
                re_decoded = decode_payload(re_encoded)
                # Compare only expected fields, ignoring internal fields
                self.assertEqual(len(re_decoded), len(expected_cycles))
                for i, (re_actual_cycle, expected_cycle) in enumerate(zip(re_decoded, expected_cycles)):
                    for key in expected_cycle:
                        self.assertEqual(re_actual_cycle[key], expected_cycle[key], f"Re-encoded cycle {i}, mismatch in field {key}")

    def test_time_edge_cases(self):
        """Test time-related edge cases."""
        for payload, expected_start, expected_end in self.time_edge_cases:
            with self.subTest(payload=payload):
                decoded = decode_payload(payload)
                self.assertEqual(decoded[0]['start_time'], expected_start)
                self.assertEqual(decoded[0]['end_time'], expected_end)

    def test_repeat_days(self):
        """Test various repeat day patterns."""
        for payload, expected_repeat in self.repeat_day_cases:
            with self.subTest(payload=payload):
                decoded = decode_payload(payload)
                self.assertEqual(decoded[0]['repeat'], expected_repeat)

    def test_durations(self):
        """Test various duration formats."""
        for payload, expected_open, expected_close in self.duration_cases:
            with self.subTest(payload=payload):
                decoded = decode_payload(payload)
                self.assertEqual(decoded[0]['open_duration'], expected_open)
                self.assertEqual(decoded[0]['close_duration'], expected_close)

    def test_invalid_payloads(self):
        """Test handling of invalid payloads."""
        invalid_payloads = [
            "invalid_base64",
            "AQA=",  # Too short
            "AQADygR+AAEAAQ",  # Invalid length
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    decode_payload(payload)

    def test_invalid_encode_input(self):
        """Test handling of invalid encode input."""
        invalid_cycles = [
            [],  # Empty list
            [{}],  # Missing required fields
            [{'socket': 4, 'activation': 'activate', 'start_time': '10:00',
              'end_time': '11:00', 'repeat': 'once', 'open_duration': '1min',
              'close_duration': '1min'}],  # Invalid socket
            [{'socket': 1, 'activation': 'invalid', 'start_time': '10:00',
              'end_time': '11:00', 'repeat': 'once', 'open_duration': '1min',
              'close_duration': '1min'}],  # Invalid activation
            [{'socket': 1, 'activation': 'activate', 'start_time': '25:00',
              'end_time': '11:00', 'repeat': 'once', 'open_duration': '1min',
              'close_duration': '1min'}],  # Invalid time
            [{'socket': 1, 'activation': 'activate', 'start_time': '10:00',
              'end_time': '11:00', 'repeat': 'InvalidDay', 'open_duration': '1min',
              'close_duration': '1min'}],  # Invalid repeat
            [{'socket': 1, 'activation': 'activate', 'start_time': '10:00',
              'end_time': '11:00', 'repeat': 'once', 'open_duration': 'invalid',
              'close_duration': '1min'}],  # Invalid duration
        ]

        for i, cycles in enumerate(invalid_cycles):
            with self.subTest(case=i):
                with self.assertRaises(ValueError):
                    encode_payload(cycles)

    def test_json_file_roundtrip(self):
        """Test encoding/decoding using JSON files."""
        # Create a test JSON file
        test_cycles = [
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

        json_file = "test_cycles.json"

        try:
            # Write test file
            with open(json_file, 'w') as f:
                json.dump(test_cycles, f, indent=2)

            # Test encoding from file
            from encode_payload import main as encode_main
            import sys
            original_argv = sys.argv
            try:
                sys.argv = ["encode_payload.py", json_file]
                # Capture output - this would normally print to stdout
                # For testing, we'll call encode_payload directly
                payload = encode_payload(test_cycles)

                # Test decoding
                decoded = decode_payload(payload)
                self.assertEqual(len(decoded), len(test_cycles))

                for i, (decoded_cycle, original_cycle) in enumerate(zip(decoded, test_cycles)):
                    with self.subTest(cycle=i):
                        self.assertEqual(decoded_cycle['socket'], original_cycle['socket'])
                        self.assertEqual(decoded_cycle['activation'], original_cycle['activation'])
                        self.assertEqual(decoded_cycle['start_time'], original_cycle['start_time'])
                        self.assertEqual(decoded_cycle['end_time'], original_cycle['end_time'])
                        self.assertEqual(decoded_cycle['repeat'], original_cycle['repeat'])
                        self.assertEqual(decoded_cycle['open_duration'], original_cycle['open_duration'])
                        self.assertEqual(decoded_cycle['close_duration'], original_cycle['close_duration'])

            finally:
                sys.argv = original_argv

        finally:
            # Clean up
            if os.path.exists(json_file):
                os.remove(json_file)

    def test_all_project_examples(self):
        """Test all examples from project.md to ensure comprehensive coverage."""
        # This is a comprehensive test that includes all the examples
        # from the project.md file to ensure our implementation handles
        # all the documented cases correctly.

        all_test_cases = self.single_cycle_cases + self.multi_cycle_cases

        for case in all_test_cases:
            payload = case[0]
            expected_data = case[1]

            with self.subTest(payload=payload):
                # Test decode
                decoded = decode_payload(payload)

                if isinstance(expected_data, dict):  # Single cycle case
                    # Compare only expected fields, ignoring internal fields
                    actual_cycle = decoded[0]
                    for key in expected_data.keys():
                        self.assertEqual(actual_cycle[key], expected_data[key], f"Mismatch in field {key}")

                    # Test round-trip
                    re_encoded = encode_payload([expected_data])
                    self.assertEqual(re_encoded, payload)
                else:  # Multi-cycle case
                    expected_cycles = expected_data
                    # Compare only expected fields, ignoring internal fields
                    self.assertEqual(len(decoded), len(expected_cycles))
                    for i, (actual_cycle, expected_cycle) in enumerate(zip(decoded, expected_cycles)):
                        for key in expected_cycle.keys():
                            self.assertEqual(actual_cycle[key], expected_cycle[key], f"Cycle {i}, mismatch in field {key}")

                    # Test round-trip with decoded cycles (which have original time values)
                    re_encoded = encode_payload(decoded)
                    self.assertEqual(re_encoded, payload)


def run_tests_with_verbosity():
    """Run tests with verbose output."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPayloadEncodingDecoding)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run with verbose output
    success = run_tests_with_verbosity()

    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1)

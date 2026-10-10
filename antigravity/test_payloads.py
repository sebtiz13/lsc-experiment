import subprocess
import sys

# Test Cases
# Format: (Args dictionary, Expected Base64)
test_cases = [
    (
        {
            "socket": "1", "action": "activate", "start": "16:10", "end": "19:10",
            "days": "once", "open": "1", "close": "1"
        },
        "AQADygR+AAEAAQ=="
    ),
    (
        {
            "socket": "3", "action": "activate", "start": "13:15", "end": "23:45",
            "days": "once", "open": "135", "close": "180"
        },
        "BQADGwWRAIcAtA=="
    ),
    (
        {
            "socket": "3", "action": "activate", "start": "10:10", "end": "23:00",
            "days": "Mon,Tue", "open": "60", "close": "60"
        },
        "BQYCYgVkADwAPA=="
    ),
    (
        {
            "cycle": [
                "2,activate,23:30,24:30,once,1,1",
                "2,activate,16:40,12:40,once,1,1",
                "1,activate,23:30,24:30,once,1,1"
            ]
        },
        "AwAFggW+AAEAAQMAA+gC+AABAAEBAAWCBb4AAQAB"
    ),
]

def test_encode():
    print("Testing Encode...")
    for args, expected in test_cases:
        cmd = ["python3", "encode_payload.py"]
        for k, v in args.items():
            if isinstance(v, list):
                for item in v:
                    cmd.extend([f"--{k}", item])
            else:
                cmd.extend([f"--{k}", v])

        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout.strip()

        if output == expected:
            print(f"PASS: {args} -> {output}")
        else:
            print(f"FAIL: {args}")
            print(f"Expected: {expected}")
            print(f"Got:      {output}")

def test_decode():
    print("\nTesting Decode...")
    for args, b64 in test_cases:
        cmd = ["python3", "decode_payload.py", b64]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Input: {b64}")
        print(result.stdout)

if __name__ == "__main__":
    test_encode()
    test_decode()

import os
import csv
import re
from ftplib import FTP

# === FTP Server Configuration ===
FTP_HOST = '127.0.0.1'
FTP_USER = 'wla'
FTP_PASS = 'wla123'
REMOTE_DIR = "/"
LOCAL_DIR = "Files/"

# === Expected Headers ===
EXPECTED_HEADERS = ["batch_id", "timestamp"] + \
    [f"reading{i}" for i in range(1, 11)]


def test_file_search_function():
    print("Starting file search test...")

    # Connect to FTP
    try:
        ftp = FTP(FTP_HOST)
        ftp.login(user=FTP_USER, passwd=FTP_PASS)
        print("[OK] Connected to FTP server.")
    except Exception as e:
        print(f"[ERROR] FTP connection failed: {e}")
        return

    # Test cases for search
    search_keywords = ["test", "data", "invalid", "csv"]

    for keyword in search_keywords:
        print(f"\n[TESTING] Search for keyword: '{keyword}'")
        try:
            files = ftp.nlst()
            matched_files = [f for f in files if keyword in f]

            if matched_files:
                print(
                    f"[SUCCESS] Found {len(matched_files)} files matching '{keyword}':")
                for file in matched_files:
                    print(f"  - {file}")
            else:
                print(f"[INFO] No files found matching '{keyword}'")
        except Exception as e:
            print(f"[ERROR] Search failed for '{keyword}': {e}")

    ftp.quit()
    print("\n[COMPLETE] File search test finished.")


def test_header_validation():
    print("\nStarting header validation test...")

    # Create test files with different header scenarios
    test_cases = [
        {
            "name": "valid_headers.csv",
            "headers": EXPECTED_HEADERS,
            "expected": True
        },
        {
            "name": "missing_headers.csv",
            "headers": ["batch_id", "timestamp"],
            "expected": False
        },
        {
            "name": "extra_headers.csv",
            "headers": EXPECTED_HEADERS + ["extra_column"],
            "expected": False
        },
        {
            "name": "wrong_order_headers.csv",
            "headers": ["timestamp", "batch_id"] + [f"reading{i}" for i in range(1, 11)],
            "expected": False
        }
    ]

    # Create test directory if it doesn't exist
    os.makedirs(LOCAL_DIR, exist_ok=True)

    for test_case in test_cases:
        print(f"\n[TESTING] {test_case['name']}")
        file_path = os.path.join(LOCAL_DIR, test_case['name'])

        # Create test file
        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(test_case['headers'])
                # Add a sample row
                writer.writerow(['1', '2024-01-01'] + ['0.1'] * 10)

            # Validate headers
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                is_valid = headers == EXPECTED_HEADERS

                if is_valid == test_case['expected']:
                    print(
                        f"[SUCCESS] Header validation {'passed' if is_valid else 'failed'} as expected")
                else:
                    print(
                        f"[ERROR] Header validation {'passed' if is_valid else 'failed'} unexpectedly")
                    print(f"Expected: {test_case['expected']}")
                    print(f"Actual: {is_valid}")
                    print(f"Headers: {headers}")
        except Exception as e:
            print(f"[ERROR] Failed to process {test_case['name']}: {e}")

    print("\n[COMPLETE] Header validation test finished.")


def test_error_handling():
    print("\nStarting error handling test...")

    # Test cases for error handling
    error_cases = [
        {
            "name": "empty_file.csv",
            "content": "",
            "expected_error": "File is empty"
        },
        {
            "name": "invalid_data.csv",
            "content": "invalid,csv,data\n1,2,3",
            "expected_error": "Incorrect or missing headers"
        },
        {
            "name": "duplicate_batch.csv",
            "content": "batch_id,timestamp,reading1,reading2,reading3,reading4,reading5,reading6,reading7,reading8,reading9,reading10\n1,2024-01-01,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0\n1,2024-01-02,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0",
            "expected_error": "Duplicate batch_id"
        },
        {
            "name": "invalid_readings.csv",
            "content": "batch_id,timestamp,reading1,reading2,reading3,reading4,reading5,reading6,reading7,reading8,reading9,reading10\n1,2024-01-01,10.0,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0",
            "expected_error": "Value exceeds 9.9"
        }
    ]

    # Create test directory if it doesn't exist
    os.makedirs(LOCAL_DIR, exist_ok=True)

    for test_case in error_cases:
        print(f"\n[TESTING] {test_case['name']}")
        file_path = os.path.join(LOCAL_DIR, test_case['name'])

        try:
            # Create test file
            with open(file_path, 'w') as f:
                f.write(test_case['content'])

            # Validate file
            with open(file_path, 'r') as f:
                content = f.read()
                if not content.strip():
                    print(f"[SUCCESS] Detected empty file as expected")
                    continue

                reader = csv.reader(content.splitlines())
                headers = next(reader, None)

                if headers != EXPECTED_HEADERS:
                    print(f"[SUCCESS] Detected invalid headers as expected")
                    continue

                # Check for duplicate batch_ids
                batch_ids = set()
                for row_num, row in enumerate(reader, start=2):
                    if len(row) != 12:
                        print(f"[SUCCESS] Detected missing columns as expected")
                        break

                    batch_id = row[0]
                    if batch_id in batch_ids:
                        print(
                            f"[SUCCESS] Detected duplicate batch_id as expected")
                        break
                    batch_ids.add(batch_id)

                    # Check readings
                    for i, reading in enumerate(row[2:], start=1):
                        try:
                            value = float(reading)
                            if value > 9.9:
                                print(
                                    f"[SUCCESS] Detected value exceeding 9.9 as expected")
                                break
                        except ValueError:
                            print(
                                f"[SUCCESS] Detected non-numeric reading as expected")
                            break

        except Exception as e:
            print(f"[ERROR] Failed to process {test_case['name']}: {e}")

    print("\n[COMPLETE] Error handling test finished.")


if __name__ == "__main__":
    test_file_search_function()
    # test_header_validation()
    # test_error_handling()

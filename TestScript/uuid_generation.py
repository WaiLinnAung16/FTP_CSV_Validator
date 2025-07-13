import os
import re
import requests
from ftp_csv import Logger

# === Configuration ===
UUID_API = "https://www.uuidtools.com/api/generate/v1"
ERROR_LOG_FILE = os.path.join("error_logs", "error_log.txt")


def test_uuid_api_direct():
    print("Starting UUID API format test...")

    try:
        response = requests.get(UUID_API, timeout=10)
        response.raise_for_status()
        uuid_list = response.json()

        if not uuid_list or not isinstance(uuid_list[0], str):
            print("[ERROR] Unexpected response structure from UUID API:", uuid_list)
            return

        uuid = uuid_list[0]
        print(f"[SUCCESS] UUID received: {uuid}")

        # Check format with regex
        if re.fullmatch(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", uuid):
            print("[SUCCESS] UUID format is valid.")
        else:
            print("[ERROR] UUID format is invalid.")
    except Exception as e:
        print("[ERROR] UUID API request failed:", str(e))

    print("[COMPLETE] UUID API test finished.\n")


def test_logger_log_file():
    print("Starting logger test with UUID...")
    # Prepare logger and log a test message
    logger = Logger()
    test_message = "TEST_LOG: Simulated error for UUID logging"
    logger.log(test_message)
    # Ensure log file exists
    if not os.path.exists(ERROR_LOG_FILE):
        print("[ERROR] Log file does not exist.")
        return
    # Read last log line
    try:
        with open(ERROR_LOG_FILE, "r") as f:
            lines = f.readlines()
        if not lines:
            print("[ERROR] Log file is empty.")
            return
        last_line = lines[-1].strip()
        print("[INFO] Last log entry:", last_line)
        # Extract and validate UUID from the log
        match = re.search(r"\[UUID: ([a-f0-9\-]+)\]", last_line)
        if match:
            uuid = match.group(1)
            if re.fullmatch(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", uuid):
                print("[SUCCESS] UUID in log is valid:", uuid)
            else:
                print("[ERROR] UUID in log is incorrectly formatted:", uuid)
        else:
            print("[ERROR] UUID not found in log entry.")
        # Check if message is in log
        if test_message in last_line:
            print("[SUCCESS] Test message found in log.")
        else:
            print("[ERROR] Test message not found in log.")
    except Exception as e:
        print("[ERROR] Failed to read or process log file:", str(e))

    print("[COMPLETE] Logger UUID test finished.\n")
if __name__ == "__main__":
    test_uuid_api_direct()
    test_logger_log_file()

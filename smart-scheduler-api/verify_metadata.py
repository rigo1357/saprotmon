import requests
import sys

BASE_URL = "http://localhost:8000"

def test_metadata():
    print("Testing /api/metadata/semesters...")
    try:
        resp = requests.get(f"{BASE_URL}/api/metadata/semesters")
        if resp.status_code == 200:
            print("SUCCESS: Semesters fetched successfully.")
            print(resp.json())
        else:
            print(f"FAILED: Status {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"ERROR: {e}")

    print("\nTesting /api/metadata/majors...")
    try:
        resp = requests.get(f"{BASE_URL}/api/metadata/majors")
        if resp.status_code == 200:
            print("SUCCESS: Majors fetched successfully.")
            print(resp.json())
        else:
            print(f"FAILED: Status {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_metadata()

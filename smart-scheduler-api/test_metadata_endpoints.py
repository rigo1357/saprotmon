import requests
import json

BASE_URL = "http://localhost:8000"

# Test login first
print("=== Testing Login ===")
login_data = {
    "username": "admin",
    "password": "admin"
}
login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"Login Status: {login_response.status_code}")

if login_response.status_code == 200:
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test metadata endpoints
    print("\n=== Testing /api/metadata/semesters ===")
    sem_response = requests.get(f"{BASE_URL}/api/metadata/semesters", headers=headers)
    print(f"Status: {sem_response.status_code}")
    print(f"Response: {json.dumps(sem_response.json(), indent=2, ensure_ascii=False)}")
    
    print("\n=== Testing /api/metadata/majors ===")
    maj_response = requests.get(f"{BASE_URL}/api/metadata/majors", headers=headers)
    print(f"Status: {maj_response.status_code}")
    print(f"Response: {json.dumps(maj_response.json(), indent=2, ensure_ascii=False)}")
    
    # Test courses endpoint to check encoding
    print("\n=== Testing /api/courses (first 3) ===")
    courses_response = requests.get(f"{BASE_URL}/api/courses", headers=headers)
    print(f"Status: {courses_response.status_code}")
    if courses_response.status_code == 200:
        courses_data = courses_response.json()
        print(f"Total courses: {courses_data.get('total', 0)}")
        for course in courses_data.get('items', [])[:3]:
            print(f"  - {course['code']}: {course['name']}")
else:
    print(f"Login failed: {login_response.text}")

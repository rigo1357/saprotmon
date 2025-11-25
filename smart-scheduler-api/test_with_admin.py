import requests
import json

BASE_URL = "http://localhost:8000"

# Test login with form data (not JSON)
print("=== Testing Login ===")
login_data = {
    "username": "admin",
    "password": "Admin@123"
}
login_response = requests.post(f"{BASE_URL}/api/login", data=login_data)  # Changed from json= to data=
print(f"Login Status: {login_response.status_code}")

if login_response.status_code == 200:
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test metadata endpoints
    print("\n=== Testing /api/metadata/semesters ===")
    sem_response = requests.get(f"{BASE_URL}/api/metadata/semesters", headers=headers)
    print(f"Status: {sem_response.status_code}")
    sem_data = sem_response.json()
    print(f"Response: {json.dumps(sem_data, indent=2, ensure_ascii=False)}")
    
    if sem_data.get('semesters'):
        print(f"✓ Found {len(sem_data['semesters'])} semesters")
    else:
        print("✗ No semesters found - this is why dropdown is empty!")
    
    print("\n=== Testing /api/metadata/majors ===")
    maj_response = requests.get(f"{BASE_URL}/api/metadata/majors", headers=headers)
    print(f"Status: {maj_response.status_code}")
    maj_data = maj_response.json()
    print(f"Response: {json.dumps(maj_data, indent=2, ensure_ascii=False)}")
    
    if maj_data.get('majors'):
        print(f"✓ Found {len(maj_data['majors'])} majors")
    else:
        print("✗ No majors found - this is why dropdown is empty!")
    
    # Test courses endpoint to check encoding
    print("\n=== Testing /api/courses (first 5) ===")
    courses_response = requests.get(f"{BASE_URL}/api/courses", headers=headers, params={"limit": 5})
    print(f"Status: {courses_response.status_code}")
    if courses_response.status_code == 200:
        courses_data = courses_response.json()
        total = courses_data.get('total', 0)
        print(f"Total courses: {total}")
        
        if total == 0:
            print("✗ No courses in database! You need to upload courses first.")
        else:
            print("\nFirst 5 courses:")
            for course in courses_data.get('items', [])[:5]:
                print(f"  Code: {course['code']}")
                print(f"  Name: {course['name']}")
                # Check encoding
                try:
                    encoded = course['name'].encode('utf-8')
                    print(f"  Encoding: OK (UTF-8)")
                except:
                    print(f"  Encoding: ERROR")
                print(f"  Semester: {course.get('semester', 'N/A')}")
                print(f"  Major: {course.get('major', 'N/A')}")
                print()
else:
    print(f"Login failed: {login_response.status_code}")
    print(f"Error: {login_response.text}")

"""Simple test script"""
import requests
import json

BASE_URL = 'http://localhost:5000'

print("=" * 50)
print("CIVIC AI Backend Test")
print("=" * 50)

# Test 1: Server is running
print("\n1. Testing server...")
try:
    r = requests.get(f'{BASE_URL}/')
    print("   Server is running!")
except:
    print("   ERROR: Server not responding")
    exit()

# Test 2: Login
print("\n2. Testing login...")
r = requests.post(f'{BASE_URL}/api/auth/login', json={
    'email': 'admin@civicai.com',
    'password': 'admin123'
})

if r.status_code == 200:
    token = r.json()['access_token']
    print(f"   Login successful!")
    print(f"   Token: {token[:50]}...")
else:
    print(f"   Login failed: {r.text}")
    exit()

# Test 3: Get Profile
print("\n3. Testing profile endpoint...")
headers = {'Authorization': f'Bearer {token}'}
r = requests.get(f'{BASE_URL}/api/auth/profile', headers=headers)
if r.status_code == 200:
    user = r.json()['user']
    print(f"   Profile retrieved!")
    print(f"   Name: {user['name']}")
    print(f"   Email: {user['email']}")
    print(f"   Role: {user['role']}")
else:
    print(f"   ERROR: {r.status_code} - {r.text[:200]}")

print("\n" + "=" * 50)
print("Test Complete!")
print("=" * 50)

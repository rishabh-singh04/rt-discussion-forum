import requests

API_KEY = "AIzaSyA4ipIg6avVEh7P6xoOntXcOxEnjMBmYwg"  # Replace with your Firebase Web API key
email = "rishabh@gmail.com"
password = "123456"

url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
payload = {
    "email": email,
    "password": password,
    "returnSecureToken": True
}

response = requests.post(url, json=payload)
data = response.json()

if "idToken" in data:
    print("Your Firebase ID Token:\n", data["idToken"])
else:
    print("Error:", data)

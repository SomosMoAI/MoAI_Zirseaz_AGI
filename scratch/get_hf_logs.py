import requests
import json

url = "https://zirseazai-zirseaz.hf.space/api/predict"
payload = {"data": []}
headers = {"Authorization": "Bearer YOUR_HF_TOKEN"}
try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print("Status Code:", response.status_code)
    try:
        data = response.json()
        print("Logs:")
        print(data["data"][0])
    except:
        print("Response text (first 500 chars):")
        print(response.text[:500])
except Exception as e:
    print("Error:", e)

import requests

url = 'https://api.worqhat.com/flows/trigger/c014dca0-f99f-4dbf-b7de-6c0a4d741678'
api_key = 'wh_mehc3yukSKmE3Z97IKYLlRdv7i7Mw5UfFQDRl26vvJzy'
payload = {
    "img_info": "img"
}
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
resp = requests.post(url, json=payload, headers=headers)
print(resp.status_code, resp.text)
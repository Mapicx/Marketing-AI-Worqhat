import requests

url = 'https://api.worqhat.com/flows/trigger/a1b94a6b-0d1b-4d67-90de-a4410890e1e4'
api_key = 'wh_mehe90ntp51wYmPOOgm6qvFgt8UYy9EL9PilaG0P5AYd'
payload = {
    "Campagion_info": "campaion"
}
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
resp = requests.post(url, json=payload, headers=headers)
print(resp.status_code, resp.text)
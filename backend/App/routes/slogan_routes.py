from fastapi import APIRouter
import requests

router = APIRouter()

URL = "https://api.worqhat.com/flows/trigger/a1b94a6b-0d1b-4d67-90de-a4410890e1e4"
API_KEY = "wh_mehe90ntp51wYmPOOgm6qvFgt8UYy9EL9PilaG0P5AYd"

@router.post("/")
def generate_slogan(campaign_info: str):
    payload = {"Campagion_info": campaign_info}
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    resp = requests.post(URL, json=payload, headers=headers)
    return {"status_code": resp.status_code, "response": resp.json()}

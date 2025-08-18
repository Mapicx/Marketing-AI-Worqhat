from fastapi import APIRouter
import requests

router = APIRouter()

# Move your WorqHat API details here
URL = "https://api.worqhat.com/flows/trigger/c014dca0-f99f-4dbf-b7de-6c0a4d741678"
API_KEY = "wh_mehc3yukSKmE3Z97IKYLlRdv7i7Mw5UfFQDRl26vvJzy"

@router.post("/")
def generate_image(img_info: str):
    payload = {"img_info": img_info}
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    resp = requests.post(URL, json=payload, headers=headers)
    return {"status_code": resp.status_code, "response": resp.json()}

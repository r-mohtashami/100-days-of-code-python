import requests
import os
from dotenv import load_dotenv

load_dotenv()

SHEETY_PRICE_ENDPOINT = "https://api.sheety.co/a6d11b7bb898aff685805a423651024e/flightDeals/prices"


class DataManager:
    def __init__(self):
        self.sheety_token = os.getenv("SHEETY_TOKEN")
        self.sheety_headers = {
            "Authorization": f"Bearer {self.sheety_token}"
        }
        self.destination_data = []

    def get_destination_data(self):
        response = requests.get(SHEETY_PRICE_ENDPOINT, headers=self.sheety_headers)
        response.raise_for_status()
        data = response.json()
        self.destination_data = data["prices"]
        return self.destination_data

    def update_destination_codes(self, sheet_data):
        for row in sheet_data:
            object_id = row["id"]
            code = row["iataCodes"]

            sheety_edit_endpoint = f"{SHEETY_PRICE_ENDPOINT}/{object_id}"

            updated_row = {
                "price": {
                    "iataCodes": code
                }
            }

            response = requests.put(
                sheety_edit_endpoint,
                headers=self.sheety_headers,
                json=updated_row
            )
            response.raise_for_status()
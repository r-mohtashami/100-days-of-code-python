import requests
import os
from dotenv import load_dotenv

load_dotenv()

SHEETY_PRICE_ENDPOINT = "https://api.sheety.co/a6d11b7bb898aff685805a423651024e/flightDeals/pricesNew"


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
        self.destination_data = data["pricesNew"]
        return self.destination_data

    def update_lowest_price(self, row_id, new_price):
        new_data = {
            "pricesNew": {
                "lowestPrice": new_price
            }
        }

        response = requests.put(
            url=f"{SHEETY_PRICE_ENDPOINT}/{row_id}",
            headers=self.sheety_headers,
            json=new_data,
        )
        print(response.text)
        response.raise_for_status()
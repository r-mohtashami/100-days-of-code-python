
# ---------------------- Imports ---------------------- #

import requests
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

# ---------------------- Environment Variables ---------------------- #

APP_ID = os.getenv("NUTRITIONIX_APP_ID")
API_KEY = os.getenv("NUTRITIONIX_API_KEY")
SHEETY_TOKEN = os.getenv("SHEETY_TOKEN")


# ---------------------- API Endpoints ---------------------- #

nutritionix_url = "https://app.100daysofpython.dev/v1/nutrition/natural/exercise"
sheety_url = "https://api.sheety.co/a6d11b7bb898aff685805a423651024e/myWorkouts/workouts"


# ---------------------- API Headers ---------------------- #

nutritionix_headers = {
    "Content-Type": "application/json",
    "x-app-id": APP_ID,
    "x-app-key": API_KEY
}

sheety_headers = {
    "Authorization": f"Bearer {SHEETY_TOKEN}"
}


# ---------------------- User Input ---------------------- #

query = input("Tell me which exercise you did?")


# ---------------------- Request Body ---------------------- #

data = {
    "query": query
}


# ---------------------- Nutritionix Request ---------------------- #

response = requests.post(nutritionix_url, headers=nutritionix_headers, json=data)
response.raise_for_status()
result = response.json()


# ---------------------- Date and Time ---------------------- #

today = datetime.now()
date = today.strftime("%d/%m/%Y")
time = today.strftime("%H:%M:%S")


# ---------------------- Sheety Request ---------------------- #

for exe in result["exercises"]:
    exercise_data = {
        "workout": {
            "date": date,
            "time": time,
            "exercise": exe["name"],
            "duration": exe["duration_min"],
            "calories": exe["nf_calories"]
        }
    }

    sheet_response = requests.post(sheety_url, headers=sheety_headers, json=exercise_data)
    sheet_response.raise_for_status()


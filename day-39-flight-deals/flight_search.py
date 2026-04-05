import os
import requests
from dotenv import load_dotenv
from flight_data import FlightData

load_dotenv()


class FlightSearch:
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.base_url = "https://serpapi.com/search"

    def get_destination_codes(self, city, country):
        params = {
            "engine": "google_flights_autocomplete",
            "q": city,
            "exclude_regions": "true",
            "api_key": self.serpapi_key
        }

        response = requests.get(url=self.base_url, params=params)
        response.raise_for_status()
        suggestions = response.json().get("suggestions", [])

        best_country_match = ""
        first_city_match = ""
        first_airports_match = ""

        for suggestion in suggestions:
            suggestion_type = suggestion.get("type")
            suggestion_name = suggestion.get("name", "").lower()
            airports = suggestion.get("airports", [])

            if not airports:
                continue

            codes = [airport["id"] for airport in airports if "id" in airport]
            if not codes:
                continue

            joined_codes = ",".join(codes)

            if not first_airports_match:
                first_airports_match = joined_codes

            if suggestion_type == "city":
                if not first_city_match:
                    first_city_match = joined_codes

                if city.lower() in suggestion_name and country.lower() in suggestion_name:
                    best_country_match = joined_codes
                    break

        if best_country_match:
            return best_country_match
        if first_city_match:
            return first_city_match
        return first_airports_match

    def _empty_flight_data(self):
        return FlightData(
            price="N/A",
            origin_airport="N/A",
            destination_airport="N/A",
            out_date="N/A",
            return_date="N/A"
        )

    def _request_flights(self, origin, destination_codes, from_time, to_time):
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination_codes,
            "outbound_date": from_time,
            "return_date": to_time,
            "currency": "GBP",
            "api_key": self.serpapi_key
        }

        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()

    def _filter_valid_destination_codes(self, origin, destination_codes, from_time, to_time):
        codes = [code.strip() for code in destination_codes.split(",") if code.strip()]
        valid_codes = []

        for code in codes:
            try:
                self._request_flights(origin, code, from_time, to_time)
                valid_codes.append(code)
            except requests.exceptions.HTTPError:
                continue

        return ",".join(valid_codes)

    def search_flights(self, origin, destination_codes, from_time, to_time):
        try:
            data = self._request_flights(origin, destination_codes, from_time, to_time)
            return self.find_cheapest_flight(data, to_time)

        except requests.exceptions.HTTPError:
            valid_destination_codes = self._filter_valid_destination_codes(
                origin, destination_codes, from_time, to_time
            )

            if not valid_destination_codes:
                return self._empty_flight_data()

            try:
                data = self._request_flights(origin, valid_destination_codes, from_time, to_time)
                return self.find_cheapest_flight(data, to_time)
            except requests.exceptions.HTTPError:
                return self._empty_flight_data()

    def find_cheapest_flight(self, data, return_date):
        best_flights = data.get("best_flights", [])
        other_flights = data.get("other_flights", [])
        all_flights = best_flights + other_flights

        if not all_flights:
            return self._empty_flight_data()

        cheapest_flight = min(
            all_flights,
            key=lambda flight: flight.get("price", float("inf"))
        )

        flights = cheapest_flight.get("flights", [])
        if not flights:
            return self._empty_flight_data()

        first_leg = flights[0]

        price = cheapest_flight.get("price", "N/A")
        origin_airport = first_leg.get("departure_airport", {}).get("id", "N/A")
        destination_airport = first_leg.get("arrival_airport", {}).get("id", "N/A")
        out_time = first_leg.get("departure_airport", {}).get("time", "N/A")
        out_date = out_time.split(" ")[0] if out_time != "N/A" else "N/A"

        return FlightData(
            price=price,
            origin_airport=origin_airport,
            destination_airport=destination_airport,
            out_date=out_date,
            return_date=return_date
        )
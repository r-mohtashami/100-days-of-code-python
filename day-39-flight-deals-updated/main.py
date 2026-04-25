from datetime import datetime, timedelta
from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import find_cheapest_flight
from notification_manager import NotificationManager
import requests_cache


requests_cache.install_cache(
    "flight_cache",
    urls_expire_after={
        "*.sheety.co*": requests_cache.DO_NOT_CACHE,
        "*": 3600,
    }
)

data_manager = DataManager()
sheet_data = data_manager.get_destination_data()

flight_search = FlightSearch()
notification_manager = NotificationManager()

tomorrow = datetime.now() + timedelta(days=1)
one_week_later = tomorrow + timedelta(days=7)
six_month_from_today = datetime.now() + timedelta(days=(6 * 30))
ORIGIN_CITY_IATA = "LHR"

for destination in sheet_data:
    print(f"\nChecking {destination['city']}...")

    flights = flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination["iataCode"],
        from_time=tomorrow,
        to_time=one_week_later
    )

    cheapest_flight = find_cheapest_flight(
        flights,
        return_date=one_week_later.strftime("%Y-%m-%d")
    )

    print(
        f"Result: price={cheapest_flight.price}, "
        f"from={cheapest_flight.origin_airport}, "
        f"to={cheapest_flight.destination_airport}, "
        f"out={cheapest_flight.out_date}, "
        f"return={cheapest_flight.return_date}"
    )

    if cheapest_flight.price != "N/A" and cheapest_flight.price < destination["lowestPrice"]:
        print(f"Lower price found for {destination['city']} - updating sheet and sending SMS")

        data_manager.update_lowest_price(destination["id"], cheapest_flight.price)

        notification_manager.send_sms(
            message_body=f"Low price alert! Only GBP {cheapest_flight.price} to fly "
                         f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, "
                         f"on {cheapest_flight.out_date} until {cheapest_flight.return_date}."
        )
    else:
        print(f"No update needed for {destination['city']}")
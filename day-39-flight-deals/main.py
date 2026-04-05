from datetime import datetime, timedelta
from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager

data_manager = DataManager()
sheet_data = data_manager.get_destination_data()

flight_search = FlightSearch()
notification_manager = NotificationManager()

for row in sheet_data:
    if row["iataCodes"] == "":
        codes = flight_search.get_destination_codes(row["city"], row["country"])
        row["iataCodes"] = codes

data_manager.update_destination_codes(sheet_data)

tomorrow = datetime.now() + timedelta(days=1)
one_week_later = tomorrow + timedelta(days=7)

from_time = tomorrow.strftime("%Y-%m-%d")
to_time = one_week_later.strftime("%Y-%m-%d")

for row in sheet_data:
    flight = flight_search.search_flights(
        origin="LHR",
        destination_codes=row["iataCodes"],
        from_time=from_time,
        to_time=to_time
    )

    print(
        f"{row['city']}: £{flight.price} | "
        f"{flight.origin_airport} -> {flight.destination_airport} | "
        f"{flight.out_date} to {flight.return_date}"
    )

    if flight.price != "N/A" and flight.price < row["lowestPrice"]:
        message = (
            f"Low price alert! Only £{flight.price} to fly "
            f"from {flight.origin_airport} to {flight.destination_airport}, "
            f"from {flight.out_date} to {flight.return_date}."
        )
        notification_manager.send_sms(message)
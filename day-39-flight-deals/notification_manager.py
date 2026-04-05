import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()


class NotificationManager:
    def __init__(self):
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.verified_number = os.getenv("TWILIO_VERIFIED_NUMBER")

    def send_sms(self, message_body):
        message = self.client.messages.create(
            body=message_body,
            from_=self.twilio_phone_number,
            to=self.verified_number
        )
        return message.sid

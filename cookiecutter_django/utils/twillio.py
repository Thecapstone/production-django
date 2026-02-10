from django.conf import settings
from twilio.rest import Client

SID = settings.TWILIO_ACCOUNT_SID
TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_PHONE = settings.TWILIO_PHONE

client: Client = Client(SID, TOKEN)


def send_otp(phone_no: str, otp: int):
    body = f"Your login OTP for wave is {otp}"
    message = client.messages.create(
        body=body, from_=f"+{TWILIO_PHONE}", to=str(phone_no)
    )
    return message.status

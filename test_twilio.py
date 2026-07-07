from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

client = Client(
    os.getenv("ACCOUNT_SID"),
    os.getenv("AUTH_TOKEN")
)

try:
    account = client.api.accounts(os.getenv("ACCOUNT_SID")).fetch()
    print("SUCCESS")
    print(account.friendly_name)
except Exception as e:
    print("ERROR:", e)

from datetime import date
import os
from twilio.rest import Client

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

def delete_messages(number, on_after_date=None):
    """
    Deletes all "Incoming" messages from the Twilio logs.
    """
    if on_after_date is not None:
        messages = client.messages.list(to=number, date_sent=on_after_date)
    else:
        return

    counter = 0
    for message in messages:
        client.messages(message.sid).delete()
        counter += 1

    print("Deleted {} message(s)".format(counter))

def main():
    today = date.today()
    delete_messages(os.environ['TWILIO_NUMBER'], today)

if __name__=='__main__':
    main()
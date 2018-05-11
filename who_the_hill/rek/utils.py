from datetime import date
import os
from twilio.rest import Client

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = TwilioRestClient(account_sid, auth_token)

delete_messages(number, on_after_date=None)
    if on_after_date is not None
        messages = client.messages.list(to=number, date_sent=on_after_date)

    counter = 0
    for message in messages:
        client.messages.delete(message.sid)
        counter += 1

    print("Deleted {} messages".format(counter))

def main():
    delete_messages(os.environ['TWILIO_NUMBER'])

if __name__=='__main__':
    main()
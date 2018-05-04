import time
from datetime import datetime
import os
import boto3
from botocore.exceptions import ClientError

class Alerter:
    """ Alerts program manager of potential abuse of a program. 

        Args:
            counter_limit (int): The max amount of program uses per time interval.
            time_interval (int): Time alloted per interval, measured in seconds.
            recipients (list): Emails to which Alerter will send potential abuse warnings.
    """
    def __init__(self, counter_limit, time_interval, recipients):
        self.counter = 0
        self.time_interval_start = time.time()
        self.counter_limit = counter_limit
        self.time_interval = time_interval
        self.recipients = recipients
        self.client = boto3.client('ses',region_name=os.environ.get("AWS_DEFAULT_REGION", None), aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID_EMAIL", None), aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY_EMAIL", None))

    def increment_counter(self):
        """ Increment counter by 1. """
        self.counter += 1

    def check_for_counter_limit(self):
        """ Check if counter if greater than or equal to the counter limit. """
        return self.counter >= self.counter_limit

    def reset_counter(self):
        """ Set counter to 0. """
        self.counter = 0

    def check_for_time_interval(self):
        """ Check if the passed-in time interval has passed. """
        return (time.time() - self.time_interval_start) >= self.time_interval

    def reset_time_interval(self):
        """ Reset time interval. """
        self.time_interval_start = time.time()

    def abuse_check(self):
        """ 
        Check if the counter limit has been passed within the given time interval. If so, notify 
        program manager of potential abuse.
        """
        self.increment_counter()

        if (self.check_for_counter_limit() and (not self.check_for_time_interval())):
            for recipient in self.recipients:
                self.send_email(recipient)
            self.reset_counter()
            self.reset_time_interval()
        elif (self.check_for_time_interval()):
            self.reset_counter()
            self.reset_time_interval()


    def send_email(self, recipient):
        # The sender of the email.
        sender = os.environ.get("EMAIL_SENDER", None)

        # The character encoding for the email.
        charset = "UTF-8"

        # The subject line for the email.
        subject = "Who The Hill - Alert!"

        # The current time
        hour = datetime.now().time().hour
        minute = datetime.now().time().minute
        time_of_day = "a.m."
        if hour > 11: 
            hour = (hour % 12) + 1
            time_of_day = "p.m."
        if minute < 10: 
            minute = "0" + str(minute)
        current_time = "{0}:{1} {2}".format(hour, minute, time_of_day)

        # The HTML body of the email.
        htmlbody = """<p>At {0}, more than {1} text messages were sent to Who The Hill. This occurred before a full time interval of {2} seconds passed. Only {3} seconds have passed. Please be aware of potential abuse of the application. Nobody likes high Twilio costs!</p>""".format(current_time, self.counter_limit, self.time_interval, (time.time() - self.time_interval_start))

        # The email body for recipients with non-HTML email clients.  
        textbody = "At {0}, more than {1} text messages were sent to Who The Hill. This occurred before a full time interval of {2} seconds passed. Only {3} seconds have passed. Please be aware of potential abuse of the application. Nobody likes high Twilio costs!".format(current_time, self.counter_limit, self.time_interval, (time.time() - self.time_interval_start))

        # Try to send the email.
        try:
            #Provide the contents of the email.
            response = self.client.send_email(
                Destination={
                    'ToAddresses': [
                        recipient,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': charset,
                            'Data': htmlbody,
                        },
                        'Text': {
                            'Charset': charset,
                            'Data': textbody,
                        },
                    },
                    'Subject': {
                        'Charset': charset,
                        'Data': subject,
                    },
                },
                Source=sender,
            )
        # Display an error if something goes wrong.	
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['ResponseMetadata']['RequestId'])
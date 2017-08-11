# Who The Hill

## What is Who The Hill?
[Shazam, but for House members faces.](https://twitter.com/jestei/status/819250406471729152)

Who The Hill is an MMS-based facial recognition service for members of Congress. Reporters covering Congress can text pictures of members of Congress to a number we’ve set up and they’ll get back:

1. A list of all the members of Congress recognized in their picture
2. Numbers indicating how confident Amazon is about the recognition
3. Colors corresponding to each member of Congress recognized
4. The picture they sent, but with a box around each member of Congress in the color corresponding to them

<img src="https://pbs.twimg.com/media/DGP41GAU0AASDvh.jpg" width="414" alt="Who The Hill in the flesh">

## Local Installation
Before getting the app running, you'll need a [Twilio](https://www.twilio.com/) account (with an operational MMS number), an [Amazon Rekognition](https://aws.amazon.com/rekognition/) account, an [Amazon SES](https://aws.amazon.com/ses) account, and an [Amazon S3](https://aws.amazon.com/s3) or [Google Cloud Storage](https://cloud.google.com/storage/) account

```
git clone https://github.com/newsdev/who_the_hill.git
cd who_the_hill
virtualenv -p /path/to/Python3 .
. bin/activate
pip install -r requirements.txt
```

To run the app locally, you will need some environment variables...

Three sets of AWS (or AWS-like) keys are needed:
* AWS Rekognition credentials
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
```

* AWS S3-like service endpoint and credentials
```
AWS_S3_ENDPOINT
AWS_GCS_ACCESS_KEY_ID
AWS_GCS_SECRET_ACCESS_KEY
```

* AWS SES credentials (for email alerter)
```
AWS_ACCESS_KEY_ID_EMAIL
AWS_SECRET_ACCESS_KEY_EMAIL
```
(You can find more information about the AWS and AWS-like credentials [here.](http://boto3.readthedocs.io/en/latest/guide/configuration.html#environment-variable-configuration))

You will also need credentials and a number from [Twilio.](https://www.twilio.com/):
```
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_NUMBER
```

You'll also need to have somewhere to send spam email alerts and an email account from which to send them:
```
EMAIL_RECIPIENTS
EMAIL_SENDER
```

To check whether results returned from Rekognition are actually members of Congress, you can either use the json dump of members of Congress (as well as variations on spellings of their name) included in this repo, or use your own API endpoint that returns similarly formatted json. If you don't set this environment variable, Who The Hill will default to using the included json file:
```
NICKNAMES_ENDPOINT
```

Finally, you'll also have to decide what the public facing name of your app will be. We like "Who The Hill," but apparently some people aren't so keen on that name:
```
APP_NAME
```

You can store your environment variables in a `dev.env` file...
```
export AWS_ACCESS_KEY_ID='<YOUR_ID>'
export AWS_SECRET_ACCESS_KEY='<YOUR_ACCESS_KEY>'
export AWS_DEFAULT_REGION='<YOUR_PREFERRED_REGION>'
export TWILIO_ACCOUNT_SID='<YOUR_ACCOUNT_SID>'
export TWILIO_AUTH_TOKEN='<YOUR_AUTH_TOKEN>'
...
```

...and run `source dev.env`. This will export your credentials to your environment.

## Running the App
Running the app locally requires running two servers at the same time: one for app.py (which houses the call to Amazon's Rekognition) and another for twilio_app.py (which handles receiving and sending messages via Twilio).

One method for running the application uses [ngrok](https://ngrok.com/) to tunnel to localhost, providing a public URL for the Twilio webhook. Ngrok allows you to expose the Twilio server so it can receive text messages. That public link refreshes every time the ngrok server is shut down.

## Acknowledgements
This app was developed by Interactive News interns [Gautam Hathi](https://github.com/gautamh) and [Sherman Hewitt](https://github.com/SHewitt95).

The idea was pitched by [Rachel Shorey](https://github.com/rshorey) and [Jeremy Bowers](https://github.com/jeremyjbowers).

The idea was conceived by [Jennifer Steinhauer](https://www.nytimes.com/by/jennifer-steinhauer).

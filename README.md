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
Before getting the app running, you'll need a [Twilio](https://www.twilio.com/) account (with an operational MMS number), an [Amazon Rekognition](https://aws.amazon.com/rekognition/) account and an [Amazon S3](https://aws.amazon.com/s3) or [Google Cloud Storage](https://cloud.google.com/storage/) account.

Who The Hill also requires Python3 and works best with `virtualenv` and `virtualenvwrapper`. For more on how NYT Interactive News sets up our Python environment, check out [this blog post by Sara Simon](https://open.nytimes.com/set-up-your-mac-like-an-interactive-news-developer-bb8d2c4097e5).

```
git clone https://github.com/newsdev/who-the-hill.git && cd who-the-hill
mkvirtualenv whothehill
pip install -r requirements.txt
```

To run the app locally, you will need some environment variables.

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

(You can find more information about the AWS and AWS-like credentials [here.](http://boto3.readthedocs.io/en/latest/guide/configuration.html#environment-variable-configuration))

You will also need credentials and a number from [Twilio.](https://www.twilio.com/):
```
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_NUMBER
```

To check whether results returned from Rekognition are actually members of Congress, you can either use the json dump of members of Congress (as well as variations on spellings of their name) included in this repo, or use your own API endpoint that returns similarly formatted json. If you don't set this environment variable, Who The Hill will default to using the included json file:
```
NICKNAMES_ENDPOINT
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
You can run the app locally as a web service that integrates with Twilio or as a CLI for examining a folder full of images to recognize.

### As a web application
Run the app locally `python who_the_hill/web/pub.py` and tunnel with [ngrok](https://ngrok.com/) so that you can integrate with Twilio, which needs a public-facing endpoint to POST data to.

### As a CLI for recognition
Put the images within which you'd like to recognize members of Congress into a folder like `/tmp/to_recognize` and then call the CLI like this:

```
python who_the_hill/cli --directory /tmp/to_recognize/
```

The app will examine the images, find and recognize faces, and produce a JSON report. Note: The CLI still requires working S3/GCS tokens and (obviously) access to the AWS Rekognition API. It does not require Twilio credentials, though.

## Acknowledgements
[Jennifer Steinhauer](https://www.nytimes.com/by/jennifer-steinhauer) came up with the original idea behind Who The Hill and was an enthusiastic sponsor and tester.

Who The Hill was developed by Interactive News interns [Gautam Hathi](https://github.com/gautamh) and [Sherman Hewitt](https://github.com/SHewitt95) in the summer of 2017 and partially rewritten in the spring of 2018 by [Jeremy Bowers](https://github.com/jeremyjbowers), all under the watchful eye of [Rachel Shorey](https://github.com/rshorey).
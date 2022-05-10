# Whatsapp Hubspot Connector

## The idea

The full hubspot api can be expensive, but its is also possible to ssend an email,

We acn then listen for this specific type of email and then process it according to predifined rules so that we can 
then send an email

## Configuration

All Configuration should be put in the .env file amd any senstive data should then be put in the .env.local, for example the whatapps api key

**HOST**=Your email imap host

**EMAIL**=the email where the hubspot mail is received

**PASSWORD**=you emial password

**the 360 template**=noreply@hubspot.com (the sender)

**SENDER_SUBJECT**="HUBSPOT TEST" (the subject)

**SEND_TO_TEL**=Telephone to send to

**D360-API-KEY**=the api key

**D360-API-TEMPLATE**=the 360 template

**D360-API-NAMESPACE**=the 360 namespace

## Installation

```
pip install -r requirements.txt
```

The application is now built. You can test it my running:

```
python main.py
```

Then we recommend setting up a cron

```
* * * * * python path_to/main.py
```




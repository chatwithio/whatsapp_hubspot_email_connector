import logging
import requests
import json


def send_to_may_contacts(tel, message, apikey):
    url = "http://api.manycontacts.com/v1/message/text"
    data = {'number': tel, 'text': message}
    headers = {'Content-type': 'application/json', 'apikey': apikey}
    try:
        r = requests.post(url, data=json.dumps(data), headers=headers)
        if r.status_code != 200:
            logging.error('Bad status code '+str(r.status_code))
        else:
            print("Message sent")
    except Exception as e:
        logging.error(e)


send_to_may_contacts('34910059158', 'Test', '9d5239e6-3843-4144-b1a9-cd180b5bb945')
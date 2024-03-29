from imap_tools import MailBox, AND, MailMessageFlags, A
from dotenv import dotenv_values
import re
import requests
import os
from bs4 import BeautifulSoup

my_dir = os.getcwd()
abspath = os.path.abspath(__file__)
my_dir = os.path.dirname(abspath)
os.chdir(my_dir)



config = {
    **dotenv_values(my_dir + "/.env"),  # load shared development variables
    **dotenv_values(my_dir + "/.env.local"),  # load sensitive variables
}


def send_whatsapp(tel, email_data):
    data = {
        "to": tel.replace(" ", "").replace("+", ""),
        "type": "template",
        "template": {
            "namespace": config['D360-API-NAMESPACE'],
            "language": {
                "policy": "deterministic",
                "code": "en"
            },
            "name": config['D360-API-TEMPLATE'],
            "components": [{
                "type": "body",
                "parameters": [
                    {
                        "text": email_data,
                        # "text": email_data['name'] + " " + email_data['email'] + " " + email_data['tel'] + " " +
                        #         email_data['emp'],
                        "type": 'text',
                    }
                    # {
                    #     "text": email_data['email'],
                    #     "type": 'text',
                    # },
                    # {
                    #     "text": email_data['tel'],
                    #     "type": 'text',
                    # },
                    # {
                    #     "text": email_data['emp'],
                    #     "type": 'text',
                    # },
                ]
            }
            ]
        }
    }

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "D360-API-KEY": config['D360-API-KEY']
    }

    try:
        requests.post('https://waba.360dialog.io/v1/messages', json=data, headers=headers)

    except requests.exceptions.RequestException as e:
        raise e


def parse_body(email_text):

    results = {
        'email': 'N/A',
        'name': 'N/A',
        'tel': 'N/A',
    }

    exp_email = re.search(r"Email:\r\n(.*)", email_text, re.MULTILINE)
    exp_name = re.search(r"First name:\r\n(.*)", email_text, re.MULTILINE)
    exp_name1 = re.search(r"Last name:\r\n(.*)", email_text, re.MULTILINE)
    exp_tel = re.search(r"Phone number:\r\n(.*)", email_text, re.MULTILINE)

    if exp_name:
        results['name'] = exp_name.group(1).strip()

    # if exp_name1:
    #     results['name1'] = results['name'] + ' ' + exp_name1.group(1).strip()

    if exp_email:
        results['email'] = exp_email.group(1).strip()

    if exp_tel:
        results['tel'] = exp_tel.group(1).strip()

    return results


def process_mails():

    # results = {
    #     'email': '',
    #     'name': '',
    #     'tel': '',
    #     'emp': '',
    # }
    #
    # send_whatsapp(results)

    with MailBox(config['HOST']).login(config['EMAIL'], 'Amenas88!!', 'INBOX') as mailbox:
        # print("IN")
        for msg in mailbox.fetch(
                criteria=AND(
                    seen=False,
                    from_=config['SENDER_MAIL'],
                    subject=config['SENDER_SUBJECT']
                ),
                mark_seen=False,
                bulk=True):

            soup = BeautifulSoup(msg.html, "html.parser")

            c = 0

            results = {
                'email': '',
                'name': '',
                'tel': '',
                'emp': '',
            }

            for tag in soup.findAll('p'):
                if not tag.has_attr('style'):
                    if c == 0:
                        results['name'] = tag.text.strip()
                    if c == 1:
                        results['name'] = results['name'] + "  " + tag.text.strip()
                    if c == 2:
                        results['tel'] = tag.text
                    if c == 3:
                        results['email'] = tag.text
                    if c == 4:
                        results['emp'] = tag.text
                    c = c + 1

            message = "Message sent from hubspot: Name"+results['name'] + " Email: " + results['email'] + " Tel: " + results['tel'] + " Employees: " + results['emp']
            #print(message)

            if "on HubSpot Form" or "" in msg.subject:
                # client_details = parse_body(msg.text)
                send_whatsapp(results['tel'], message)
                mailbox.flag(msg.uid, MailMessageFlags.SEEN, True)


if __name__ == "__main__":
    process_mails()

from imap_tools import MailBox, AND, MailMessageFlags, A
from dotenv import dotenv_values
import re
import requests
import os
from bs4 import BeautifulSoup
import logging
from manycontacts import send_to_may_contacts

my_dir = os.getcwd()
abspath = os.path.abspath(__file__)
my_dir = os.path.dirname(abspath)
os.chdir(my_dir)

config = {
    **dotenv_values(my_dir + "/.env"),  # load shared development variables
    **dotenv_values(my_dir + "/.env.local"),  # load sensitive variables
}

logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(my_dir + '/logs/logs.log')
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


def send_whatsapp(tel, data, template):

    params = []

    # for data in datas:
    #     params.append(
    #         {
    #             "text": data,
    #             "type": 'text',
    #         }
    #     )

    payload = {
        "to": tel, #tel.replace(" ", "").replace("+", ""),
        "type": "template",
        "template": {
            "namespace": config['D360-API-NAMESPACE'],
            "language": {
                "policy": "deterministic",
                "code": "es"
            },
            "name": template,
            "components": [{
                "type": "body",
                "parameters": [
                    {
                        "text": data,
                        "type": 'text',
                    }
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
        resp = requests.post('https://waba.360dialog.io/v1/messages', json=payload, headers=headers)
        logger.info(payload)
        logger.info(resp)

    except requests.exceptions.RequestException as e:
        logger.error(payload)


def process_mails(struct):
    with MailBox(config['HOST']).login(config['EMAIL'], 'Amenas88!!', 'INBOX') as mailbox:

        tel_pattern = '^(\+)?[0-9]+$'

        for msg in mailbox.fetch(
                criteria=AND(
                    seen=False,
                    from_=config['SENDER_MAIL'],
                    #subject='Agenda tu sesi'
                ),
                mark_seen=False,
                bulk=True):

            if msg.subject == struct['subject']:

                soup = BeautifulSoup(msg.html, "html.parser")

                prelim_results = {
                    'line1': '',
                    'line2': '',
                    'line3': '',
                }
                c = 0
                print('---------------')
                print(msg.subject)
                results = {}

                for tag in soup.findAll('p'):
                    if not tag.has_attr('style'):
                        if c == 0:
                            prelim_results['line1'] = tag.text.strip()
                        if c == 1:
                            prelim_results['line2'] = tag.text.strip()
                        if c == 2:
                            prelim_results['line2'] = tag.text
                        c = c + 1

                if re.match(tel_pattern, prelim_results['line2']):
                    results = {
                        'name': prelim_results['line1'],
                        'tel': prelim_results['line2'],
                    }
                elif re.match(tel_pattern, prelim_results['line3']):
                    results = {
                        'name': prelim_results['line1'] + " " + prelim_results['line2'],
                        'tel': prelim_results['line3'],
                    }
                else:
                    continue

                results['tel'] = results['tel'].replace(" ", "").replace("+", "")

                if len(results['tel']) == 9:
                    results['tel'] = "34" + results['tel']

                print(results)

                send_whatsapp(results['tel'], results['name'], struct['template'])
                mailbox.flag(msg.uid, MailMessageFlags.SEEN, True)

                send_to_may_contacts(results['tel'], "Campaign" + struct['subject'], config['MANY-CONTACTS-API'])


structs = [
    {
        'subject': 'Ya queda menos',
        'template': 'ya_queda_menos1',
    },
    {
        'subject': 'Agenda tu sesión',
        'template': 'agenda_tu_sesion',
    },
    {
        'subject': 'Reminder de agenda tu sesión',
        'template': '',
    },
    {
        'subject': 'Descubre nuestra guía',
        'template': 'descubre_nuestra_guia',
    },
    {
        'subject': 'Experto a disposición',
        'template': 'experto_a_disposicion',
    },
    {
        'subject': 'Envío regalo',
        'template': 'envio_regalo',
    },
    {
        'subject': 'Pasos a seguir',
        'template': 'pasos_a_seguir',
    },
    {
        'subject': 'Nos encargamos de todo',
        'template': 'nos_encargamos_de_todo1',
    }
]


for struct in structs:
    process_mails(struct)



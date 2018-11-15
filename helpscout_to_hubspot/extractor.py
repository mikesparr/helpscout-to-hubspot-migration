import os
import logging
import requests
from envparse import env

env.read_envfile()
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def help():
    return (u"You need to get access keys from each API and update config first")

def get_mailboxes():
    url = env.str("HELPSCOUT_API_URL")
    endpoint = "/mailboxes"
    token = env.str("HELPSCOUT_API_TOKEN")
    headers = {"Authorization": "Bearer {}".format(token)}

    # fetch data
    logging.info("Fetching data")
    response = requests.get(url+endpoint, headers=headers)
    return response.json()

def main():
    logging.info('Started')
    get_mailboxes()
    logging.info('Finished')

if __name__ == '__main__':
    main()
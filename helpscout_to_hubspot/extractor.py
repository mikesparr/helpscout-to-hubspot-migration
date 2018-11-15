import os
import time
import urllib
import logging
import requests
from envparse import env

env.read_envfile()
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

KEYS = {
    "Customer": "customers",
    "Conversation": "conversations",
    "Error": "error_description",
    "Mailbox": "mailboxes"
}

def help():
    return (u"You need to get access keys from each API and update config first")

def _get_page(url):
    token = env.str("HELPSCOUT_API_TOKEN")
    headers = {"Authorization": "Bearer {}".format(token)}
    logging.info("Fetching URL: {}".format(url))
    response = requests.get(url, headers=headers)
    return response.json()

def _get_next_page(obj):
    links = obj["_links"]
    next_page_url = links.get("next")["href"]

    time.sleep(.075) # avoid exceeding 10 req/sec rate limit
    return _get_page(next_page_url)

def _has_error(obj):
    return True if obj.get("error", None) is not None else False

def _has_next_page(obj):
    if _has_error(obj):
        return False

    links = obj["_links"]
    return True if links.get("next", None) is not None else False

def _get_initial_records(type, params = None):
    path = env.str("HELPSCOUT_API_URL")
    endpoint = "/{}".format(type)
    url = (path + endpoint)

    # add querystring params if exist (Dictionary)
    if (params is not None):
        url += "?{}".format(urllib.urlencode(params))

    return _get_page(url)


# records
def get_records(type, params = None):
    return _get_initial_records(type, params)

def get_all_records(type, params = None):
    response = get_records(type, params)
    records = []

    if _has_error(response):
        logging.error("Error: {}".format(response[KEYS["Error"]]))
    else:
        # add initial page to list
        records.extend(response["_embedded"][type])

        # if multiple pages, loop, fetch and append additional records
        while _has_next_page(response):
            response = _get_next_page(response)
            records.extend(response["_embedded"][type])
    
    logging.info("Returning {} {}".format(len(records), type))
    return records

def get_mailbox_ids():
    response = get_records(KEYS["Mailbox"])
    mailboxes = response["_embedded"][KEYS["Mailbox"]]
    id_list = [box["id"] for box in mailboxes]
    return id_list


def main():
    logging.info(KEYS["Mailbox"])
    print(get_mailbox_ids)

    logging.info(KEYS["Conversation"])
    conversations = get_records(KEYS["Conversation"], {"status": "all"})
    print(_has_next_page(conversations))

    logging.info("All conversations")
    _ = get_all_records(KEYS["Conversation"], {"status": "all"})

    logging.info("Finished")


if __name__ == '__main__':
    main()

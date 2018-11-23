# Helpscout To Hubspot Migration
This script is intended to extract all data from Helpscout API V2 and prepare and load it into Hubspot Service Hub

# Install
```bash
git clone git@github.com:mikesparr/helpscout-to-hubspot-migration.git
cd helpscout-to-hubspot-migration
python setup.py install
```

# Setup
## 1. Extractor (HelpScout)
HelpScout API uses OAuth2 and requires authorization in a browser. You must first set up your API code and secret via the admin site.

 * https://developer.helpscout.com/mailbox-api/overview/authentication

## 2. Create an .env file in module folder or set in your ENV
```bash
HELPSCOUT_API_URL=https://api.helpscout.net/v2
HELPSCOUT_CLIENT_ID={your app id}
HELPSCOUT_CLIENT_SECRET={your app secret}
```

## 3. Transformer
Use default mappings to generated Hubspot CSVs, or create your own. The `transformer` will convert 
your output files from the extractor to a desired format, and optionally output CSV files.

## 4. Loader (Hubspot)
Hubspot recommends using their CSV loader so take the CSV output file(s) and load them per their instructions https://knowledge.hubspot.com/articles/kcs_article/contacts/associate-records-via-import

# Usage
```python
# example.py

import os
import helpscout_to_hubspot
from helpscout_to_hubspot import extractor
from helpscout_to_hubspot import transformer

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
EXT_KEYS = extractor.KEYS
FILE_TYPES = {
    "Source": "json",
    "Sink": "csv",
    "Mapping": "mapping"
}

# NOTE: be sure you set up the ENV params!!!

def get_filename(name, file_type):
    if (file_type == FILE_TYPES["Mapping"]):
        return "{}.{}.{}".format(FILE_TYPES["Mapping"], name, FILE_TYPES["Source"])
    else:
        return "{}.{}".format(name, file_type)

# extract data from HelpScout
users = extractor.get_all_records(EXT_KEYS["User"])
extractor.dict_to_file(users, get_filename(EXT_KEYS["User"], FILE_TYPES["Source"]))
customers = extractor.get_all_records(EXT_KEYS["Customer"])
extractor.dict_to_file(customers, get_filename(EXT_KEYS["Customer"], FILE_TYPES["Source"]))
conversations = extractor.get_all_records(EXT_KEYS["Conversation"])
extractor.dict_to_file(conversations, get_filename(EXT_KEYS["Conversation"], FILE_TYPES["Source"]))

# transform extracted data into CSV for Hubspot import
user_mapping = transformer.json_to_dict(get_filename(EXT_KEYS["User"], FILE_TYPES["Mapping"]))
users_dict = transformer.json_to_dict(get_filename(EXT_KEYS["User"], FILE_TYPES["Source"]))
user_list = transformer.transform(users_dict, user_mapping)
transformer.list_to_csv(user_list, user_mapping, get_filename(EXT_KEYS["User"], FILE_TYPES["Sink"]))

customer_mapping = transformer.json_to_dict(get_filename(EXT_KEYS["Customer"], FILE_TYPES["Mapping"]))
customers_dict = transformer.json_to_dict(get_filename(EXT_KEYS["Customer"], FILE_TYPES["Source"]))
customer_list = transformer.transform(customers_dict, customer_mapping)
transformer.list_to_csv(customer_list, customer_mapping, get_filename(EXT_KEYS["Customer"], FILE_TYPES["Sink"]))

conversation_mapping = transformer.json_to_dict(get_filename(EXT_KEYS["Conversation"], FILE_TYPES["Mapping"]))
conversations_dict = transformer.json_to_dict(get_filename(EXT_KEYS["Conversation"], FILE_TYPES["Source"]))
conversation_list = transformer.transform(conversations_dict, conversation_mapping)
transformer.list_to_csv(conversation_list, conversation_mapping, get_filename(EXT_KEYS["Conversation"], FILE_TYPES["Sink"]))

# expected result are 3 .json and 3 .csv files - use .csv files and import into Hubspot

```

# Test
`python setup.py test` or `nosetests`

# Disclaimer
I built this for one-time use and am sharing in case others need. Absolutely no warranties or support are provided so 
use at your own risk. If APIs change after (November 2018) then you can fork this repo and customize to your needs

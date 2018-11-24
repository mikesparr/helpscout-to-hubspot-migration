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
conversations = extractor.get_all_records(EXT_KEYS["Conversation"], {"status": "all"})
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

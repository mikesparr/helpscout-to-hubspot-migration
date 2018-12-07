import os
import csv
import copy
import json
import time
import datetime
import logging
from envparse import env

env.read_envfile()
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

# avoid magic strings
KEYS = {
    "Title": "title",
    "Source": "source",
    "Dest": "dest",
    "Excludes": "excludes"
}
DOT_DELIMITER = "."


def _get_dot_val(obj, string_field):
    """Uses string dot notation to locate field in object and get value"""

    value = None

    try:
        parts = string_field.split(DOT_DELIMITER)
        for part in parts[:-1]:
            obj = obj.get(part, None)

        if obj is not None and isinstance(obj, dict):
            value = obj.get(parts[-1])
    except Exception, e:
        logging.error( "Error getting field {}".format(string_field) )
    
    logging.debug("Returning {} for {}".format(value, string_field))
    return value

def _get_header_fields_from_mapping(mapping):
    """Returns list of field names for header row"""

    fields = []

    if (len(mapping) <= 0):
        logging.warn("Mapping has no fields")
    else:
        fields = [field[KEYS["Title"]] for field in mapping]

    logging.debug("Returning header fields {}".format(fields))
    return fields

def _get_transformed_obj(obj, mapping):
    """Returns new dict using mapping"""
    new_obj = {}

    for field in mapping:
        new_obj[field[KEYS["Dest"]]] = _get_dot_val(obj, field[KEYS["Source"]])
    
    logging.debug("Returning transformed obj {}".format(str(new_obj)))
    return new_obj

def _is_excluded(obj, mapping):
    """Flags flattened object if should be excluded based on mapping source key"""
    exclude = False

    for field in mapping:
        exclude_list = field.get(KEYS["Excludes"], None)
        if (exclude_list is not None and len(exclude_list) > 0):
            test_val = _get_dot_val(obj, field[KEYS["Source"]])
            # only change if positive test
            for to_exclude in exclude_list:
                # test for partial match
                if to_exclude in test_val:
                    exclude = True

    return exclude

def flatten(obj):
    """Flattens dict if has nested list using indices as keys"""
    new_obj = {}

    if isinstance(obj, dict):
        for k,v in obj.iteritems():
            if isinstance(v, list):
                new_obj[k] = {str(idx): flatten(val) for idx, val in enumerate(v)}
            elif isinstance(v, dict):
                new_obj[k] = flatten(v)
            elif isinstance(v, basestring):
                new_obj[k] = v.encode("utf-8")
            else:
                new_obj[k] = v
    else:
        logging.debug("*** Object was not a dict ***".format(obj))
        new_obj = obj
    
    logging.debug("Returning new obj {}".format(str(new_obj)))
    return new_obj

def transform(data, mapping):
    """Transforms date using mapping into list of new dicts"""
    new_data = []

    for row in data:
        flattened = flatten(row)
        # check first if excluded, otherwise transform and add to list
        if (_is_excluded(flattened, mapping)) is False:
            transformed = _get_transformed_obj(flattened, mapping)
            new_data.append(transformed)
    
    logging.debug("Returning transformed data {}".format(str(new_data)))
    return new_data

def json_to_dict(filename):
    """Loads JSON file and returns dict"""
    try:
        with open(filename) as file:
            return json.loads(file.read())
    except IOError, ioe:
        logging.error(ioe)
        return None

def list_to_csv(data, mapping, filename):
    """Creates CSV file from list of dicts"""

    with open(filename, "wb+") as output_file:
        out = csv.writer(output_file, quoting=csv.QUOTE_MINIMAL)
        out.writerow(_get_header_fields_from_mapping(mapping))
        for row in data:
            out.writerow([row[val[KEYS["Dest"]]] for val in mapping])

        logging.info("Generated CSV file {} with {} rows".format(filename, len(data)))


def main():

    TEST_RECORDS = [
        {
            "type": "email", 
            "status": "active", 
            "mailboxId": 42,
            "subject": "Some support request",
            "preview": "This is the \"message\" content",
            "threads": [
                {
                    "type": "message",
                    "body": "This is the message content", 
                    "source": {
                        "type": "email"
                    },
                    "author": {
                        "first_name": "Sam",
                        "last_name": "Smith",
                        "email": "sam@smith.com"
                    }
                }
            ]
        },
        {
            "type": "email", 
            "status": "active", 
            "mailboxId": 42,
            "subject": "Some support request",
            "preview": "Thanks we will let you know",
            "threads": [
                {
                    "type": "message",
                    "body": "Thanks we will let you know", 
                    "source": {
                        "type": "email"
                    },
                    "author": {
                        "first_name": "Sam",
                        "last_name": "Smith",
                        "email": "sam@smith.com"
                    }
                }
            ]
        },
        {
            "type": "email", 
            "status": "active", 
            "mailboxId": 42,
            "subject": "Some support request",
            "preview": "This is the message content",
            "threads": [
                {
                    "type": "message",
                    "body": "This is the message content", 
                    "source": {
                        "type": "email"
                    },
                    "author": {
                        "first_name": "Sam",
                        "last_name": "Smith",
                        "email": "sam@smith.com"
                    }
                }
            ]
        }
    ]

    TEST_MAPPING = [
        {
            "title": "Mailbox",
            "source": "mailboxId",
            "dest": "box"
        },
        {
            "title": "Type",
            "source": "type",
            "dest": "type"
        },
        {
            "title": "Subject",
            "source": "subject",
            "dest": "subject"
        },
        {
            "title": "Text",
            "source": "preview",
            "dest": "text"
        },
        {
            "title": "Author",
            "source": "threads.0.author.email",
            "dest": "email"
        }
    ]

    my_list = transform(TEST_RECORDS, TEST_MAPPING)
    list_to_csv(my_list, TEST_MAPPING, "test_output.csv")
    

if __name__ == '__main__':
    main()

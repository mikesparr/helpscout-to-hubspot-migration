# -*- coding: utf-8 -*- 

import os
import sys
import csv
import copy
import json
import time
import datetime
import logging
import traceback
from envparse import env

reload(sys)
sys.setdefaultencoding('utf8')

env.read_envfile()
logging.basicConfig(format=u'%(levelname)s:%(message)s', level=logging.DEBUG)

# avoid magic strings
KEYS = {
    "Title": "title",
    "Source": "source",
    "Dest": "dest",
    "Excludes": "excludes",
    "List": "list",
    "Parent": "_parent"
}
DOT_DELIMITER = "."


def _get_dot_val(obj, string_field, ctx = None):
    """Uses string dot notation to locate field in object and get value"""

    value = None

    try:
        parts = string_field.split(DOT_DELIMITER)

        # check if _parent is first part, then apply following field to ctx object instead
        for part in parts[:-1]:
            if part == KEYS["Parent"]:
                logging.debug("Parent field detected so switching to context source")
                obj = ctx if ctx is not None else {}
            else:
                obj = obj.get(part, None)

        if obj is not None and isinstance(obj, dict):
            value = obj.get(parts[-1])
            logging.debug("Got value of type {}".format(type(value).__name__))
    except Exception:
        logging.error( "Error getting field {}".format(string_field) )
    
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

def _get_transformed_obj(obj, mapping, ctx = None):
    """Returns new dict using mapping"""

    new_obj = {}
    new_list = []

    for field in mapping:
        # if dest field is list, iterate through it's fields
        if _is_nested_mapping(field):
            logging.debug("Handling nested field {}".format( json.dumps(field) ) )
            # loop through list field
            for item in ctx[ field[KEYS["Source"]] ]:
                temp_obj = {}
                logging.debug("Item in items {}".format(json.dumps(item)))
                for sub_field in field[KEYS["Dest"]]:
                    logging.debug("Handling sub_field {}".format( json.dumps(sub_field) ) )
                    # add ctx in case _parent field referenced in nested mapping
                    temp_obj[ sub_field[KEYS["Dest"]] ] = _get_dot_val(item, sub_field[KEYS["Source"]], ctx)

                new_list.append(temp_obj)
        else:
            new_obj[field[KEYS["Dest"]]] = _get_dot_val(obj, field[KEYS["Source"]])
    
    logging.debug("Returning transformed obj {}".format(json.dumps(new_obj)))
    return new_list if len(new_list) > 0 else new_obj

def _is_nested_mapping(field):
    """Returns true if nested mapping"""

    return type(field[KEYS["Dest"]]).__name__ == KEYS["List"]

def _is_excluded(obj, mapping):
    """Flags flattened object if should be excluded based on mapping source key"""

    exclude = False

    for field in mapping:
        exclude_list = field.get(KEYS["Excludes"], None)
        if (exclude_list is not None and len(exclude_list) > 0):
            test_val = str( _get_dot_val(obj, field[KEYS["Source"]]) ).decode('utf-8')
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
    
    logging.debug("Returning new obj {}".format(json.dumps(new_obj)))
    return new_obj

def transform(data, mapping):
    """Transforms date using mapping into list of new dicts"""

    new_data = []

    for row in data:
        flattened = flatten(row)
        # check first if excluded, otherwise transform and add to list
        if (_is_excluded(flattened, mapping)) is False:
            transformed = _get_transformed_obj(flattened, mapping, row)
            # check if list or single object
            logging.debug("transformed type is {}".format(type(transformed).__name__))
            if type(transformed).__name__ == KEYS["List"]:
                new_data.extend(transformed)
            else:
                new_data.append(transformed)
    
    logging.debug("Returning transformed data {}".format(json.dumps(new_data)))
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

    error_count = 0

    # test for nested mapping and replace
    if len(mapping) > 0:
        first_field = mapping[0]
        if _is_nested_mapping(first_field):
            mapping = first_field[KEYS["Dest"]]

    with open(filename, "wb+") as output_file:
        out = csv.writer(output_file, quoting=csv.QUOTE_MINIMAL)
        out.writerow(_get_header_fields_from_mapping(mapping))
        for row in data:
            try:
                out.writerow([ str(row[val[KEYS["Dest"]]]).encode('utf-8') for val in mapping])
            except Exception:
                traceback.print_exc()
                logging.info("--- Skipped row ---")
                error_count += 1

        logging.info("Generated CSV file {} with {} rows".format(filename, len(data)))
        logging.info("Caught {} errors".format(error_count))


def main():

    print("View README or example.py for usage examples")

if __name__ == '__main__':
    main()

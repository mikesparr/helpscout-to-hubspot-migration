import os
import csv
import json
import time
from unittest import TestCase

from helpscout_to_hubspot import transformer

TEST_DICT = {
    "foo": "bar",
    "items": [
        {"name": "apple"},
        {"name": "banana"},
        {"name": "orange"}
    ],
    "person": {
        "first": "Jane",
        "last": "Doe",
        "email": "jane@doe.com"
    }
}

TEST_MAPPING = [
    {"title": "Foo", "source": "foo", "dest": "foo"},
    {"title": "Fruit", "source": "items.0.name", "dest": "fruit"},
    {"title": "First Name", "source": "person.first", "dest": "first"},
    {"title": "Last Name", "source": "person.last", "dest": "last"},
    {"title": "Email", "source": "person.email", "dest": "email"}
]
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_JSON_FILE = "{}/test_conversations.json".format(DIR_PATH)

class TestHelpers(TestCase):
    def test_json_to_dict(self):
        result = transformer.json_to_dict(TEST_JSON_FILE)
        self.assertTrue(len(result) == 3) # 3 records

    def test_get_dot_value(self):
        result = transformer._get_dot_val(TEST_DICT, "person.last")
        self.assertEqual(result, TEST_DICT["person"]["last"])

    def test_get_headers(self):
        expected = [field["title"] for field in TEST_MAPPING]
        result = transformer._get_header_fields_from_mapping(TEST_MAPPING)
        self.assertEqual(result, expected)

    def test_flatten(self):
        result = transformer.flatten(TEST_DICT)
        self.assertEqual(result["items"]["0"]["name"], "apple")

class TestTransform(TestCase):
    def test_transform(self):
        expected = [{
            "foo": TEST_DICT["foo"],
            "fruit": TEST_DICT["items"][0]["name"],
            "first": TEST_DICT["person"]["first"],
            "last": TEST_DICT["person"]["last"],
            "email": TEST_DICT["person"]["email"]
        }]
        result = transformer.transform([TEST_DICT], TEST_MAPPING)
        self.assertEqual(result, expected)
    
class TestWriteCSV(TestCase):
    def test_list_to_csv(self):
        test_filename = "delete_me.csv"
        test_list = transformer.transform([TEST_DICT], TEST_MAPPING)

        transformer.list_to_csv(test_list, TEST_MAPPING, test_filename)

        time.sleep(.25) # give time to write file
        with open(test_filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for item in test_list:
                    self.assertEqual(item["fruit"], row["Fruit"])
        
        os.remove(test_filename) # clean up




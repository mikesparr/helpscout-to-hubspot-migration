import os
import csv
import json
import time
from unittest import TestCase

from helpscout_to_hubspot import transformer

test_dict = {
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

test_mapping = [
    {"title": "Foo", "source": "foo", "dest": "foo"},
    {"title": "Fruit", "source": "items.0.name", "dest": "fruit"},
    {"title": "First Name", "source": "person.first", "dest": "first"},
    {"title": "Last Name", "source": "person.last", "dest": "last"},
    {"title": "Email", "source": "person.email", "dest": "email"}
]

class TestHelpers(TestCase):
    def test_get_dot_value(self):
        result = transformer._get_dot_val(test_dict, "person.last")
        self.assertEqual(result, test_dict["person"]["last"])

    def test_get_headers(self):
        expected = [field["title"] for field in test_mapping]
        result = transformer._get_header_fields_from_mapping(test_mapping)
        self.assertEqual(result, expected)

    def test_flatten(self):
        result = transformer.flatten(test_dict)
        self.assertEqual(result["items"]["0"]["name"], "apple")

class TestTransform(TestCase):
    def test_transform(self):
        expected = [{
            "foo": test_dict["foo"],
            "fruit": test_dict["items"][0]["name"],
            "first": test_dict["person"]["first"],
            "last": test_dict["person"]["last"],
            "email": test_dict["person"]["email"]
        }]
        result = transformer.transform([test_dict], test_mapping)
        self.assertEqual(result, expected)
    
class TestWriteCSV(TestCase):
    def test_list_to_csv(self):
        test_filename = "delete_me.csv"
        test_list = transformer.transform([test_dict], test_mapping)

        transformer.list_to_csv(test_list, test_mapping, test_filename)

        time.sleep(.25) # give time to write file
        with open(test_filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for item in test_list:
                    self.assertEqual(item["fruit"], row["Fruit"])
        
        os.remove(test_filename) # clean up




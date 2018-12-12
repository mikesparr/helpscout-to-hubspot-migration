import os
import csv
import json
import time
from unittest import TestCase

from helpscout_to_hubspot import transformer

TEST_DICT = {
    "id": 1,
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

TEST_DICT_FLATTENED = {
    "id": 1,
    "foo": "bar",
    "items": {
        "0": {"name": "\xf0\x9f\x8f\xa0 apple"},
        "1": {"name": "banana"},
        "2": {"name": "orange"}
    },
    "person": {
        "first": "Jane",
        "last": "Doe",
        "email": "jane@doe.com"
    }
}

TEST_DICT_2 = {
    "id": 2,
    "foo": "bar",
    "items": [
        {"name": "orange"},
        {"name": "banana"},
        {"name": "pineapple"}
    ],
    "person": {
        "first": "John",
        "last": "Doe",
        "email": "john@doe.com"
    }
}

TEST_MAPPING = [
    {"title": "Foo", "source": "foo", "dest": "foo"},
    {"title": "Fruit", "source": "items.0.name", "dest": "fruit"},
    {"title": "First Name", "source": "person.first", "dest": "first"},
    {"title": "Last Name", "source": "person.last", "dest": "last"},
    {"title": "Email", "source": "person.email", "dest": "email"}
]
TEST_MAPPING_WITH_FILTER = [
    {"title": "Foo", "source": "foo", "dest": "foo"},
    {"title": "Fruit", "source": "items.0.name", "dest": "fruit"},
    {"title": "First Name", "source": "person.first", "dest": "first"},
    {"title": "Last Name", "source": "person.last", "dest": "last"},
    {"title": "Email", "source": "person.email", "dest": "email", "excludes": ["john@doe.com"]}
]
TEST_MAPPING_WITH_PARTIAL_VALUE_FILTER = [
    {"title": "Foo", "source": "foo", "dest": "foo"},
    {"title": "Fruit", "source": "items.0.name", "dest": "fruit"},
    {"title": "First Name", "source": "person.first", "dest": "first"},
    {"title": "Last Name", "source": "person.last", "dest": "last"},
    {"title": "Email", "source": "person.email", "dest": "email", "excludes": ["doe.com"]}
]
TEST_MAPPING_WITH_MULTIPLE_FILTERS = [
    {"title": "Foo", "source": "foo", "dest": "foo"},
    {"title": "Fruit", "source": "items.0.name", "dest": "fruit", "excludes": ["apple"]},
    {"title": "First Name", "source": "person.first", "dest": "first"},
    {"title": "Last Name", "source": "person.last", "dest": "last"},
    {"title": "Email", "source": "person.email", "dest": "email", "excludes": ["john@doe.com"]}
]
TEST_NESTED_MAPPING = [
    {"title": "Foo", "source": "items", "dest": [
        {"title": "Foo", "source": "_parent.id", "dest": "Foo ID"},
        {"title": "Fruit", "source": "name", "dest": "fruit"}
    ]}
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
    
    def test_is_nested_mapping(self):
        # true
        result = transformer._is_nested_mapping(TEST_NESTED_MAPPING[0])
        self.assertTrue(result)
        # false
        result = transformer._is_nested_mapping(TEST_MAPPING[0])
        self.assertFalse(result)
    
    def test_is_excluded(self):
        result1 = transformer._is_excluded(TEST_DICT_2, TEST_MAPPING_WITH_FILTER)
        result2 = transformer._is_excluded(TEST_DICT, TEST_MAPPING_WITH_FILTER)
        result3 = transformer._is_excluded(TEST_DICT_FLATTENED, TEST_MAPPING_WITH_MULTIPLE_FILTERS)
        # partial value exclusion (Issue #2)
        result4 = transformer._is_excluded(TEST_DICT, TEST_MAPPING_WITH_PARTIAL_VALUE_FILTER)
        result5 = transformer._is_excluded(TEST_DICT_2, TEST_MAPPING_WITH_PARTIAL_VALUE_FILTER)
        self.assertTrue(result1)
        self.assertFalse(result2)
        self.assertTrue(result3) # another field was flagged
        # partial value exclusion (Issue #2)
        self.assertTrue(result4)
        self.assertTrue(result5) # both true because have 'doe.com' in email

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

    def test_transform_with_filter(self):
        test_sources = [TEST_DICT, TEST_DICT_2]
        expected = [{
            "foo": TEST_DICT["foo"],
            "fruit": TEST_DICT["items"][0]["name"],
            "first": TEST_DICT["person"]["first"],
            "last": TEST_DICT["person"]["last"],
            "email": TEST_DICT["person"]["email"]
        }] # should not have john doe

        result = transformer.transform(test_sources, TEST_MAPPING_WITH_FILTER)
        self.assertEqual(len(result), 1)
        self.assertEqual(result, expected)
    
    def test_transform_with_nested(self):
        test_sources = [TEST_DICT]
        expected = [
            {"Foo ID": 1, "fruit": "apple"},
            {"Foo ID": 1, "fruit": "banana"},
            {"Foo ID": 1, "fruit": "orange"}
        ] # includes parent ID and each nested value

        result = transformer.transform(test_sources, TEST_NESTED_MAPPING)
        self.assertEqual(result, expected)
        self.assertEqual(len(result), 3)
    
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




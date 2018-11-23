import os
import json
import time
import datetime
from unittest import TestCase

from helpscout_to_hubspot import extractor

KEYS = extractor.KEYS

class TestHelp(TestCase):
    def test_is_string(self):
        s = extractor.help()
        self.assertTrue(isinstance(s, basestring))

class TestWriteFile(TestCase):
    def test_dict_to_file(self):
        test_dict = [{"foo": "bar"}]
        test_filename = "delete_me.json"
        extractor.dict_to_file(test_dict, test_filename)

        time.sleep(.25) # give time to write file
        with open(test_filename) as file:
            result_dict = json.loads(file.read())
            self.assertEqual(test_dict, result_dict)
        
        os.remove(test_filename) # clean up

class TestMailboxes(TestCase):
    # you must add an HELPSCOUT_CLIENT_ID and HELPSCOUT_CLIENT_SECRET 
    # to .env before these will work (see README.md)  
    def test_get_mailbox_ids(self):
        result = extractor.get_mailbox_ids()
        self.assertGreater(len(result), 0)

class TestUsers(TestCase):
    def test_get_records(self):
        result = extractor.get_records(KEYS["User"], {"status": "all"})
        users = result[KEYS["Embedded"]][KEYS["User"]]
        self.assertIsNotNone(users)
        self.assertGreater(len(users), 3)
    
    def test_get_all_users(self):
        result = extractor.get_all_records(KEYS["User"], {"status": "active"})
        self.assertGreater(len(result), 1)

class TestCustomers(TestCase):
    def test_get_records(self):
        result = extractor.get_records(KEYS["Customer"])
        customers = result[KEYS["Embedded"]][KEYS["Customer"]]
        self.assertIsNotNone(customers)
        self.assertGreater(len(customers), 5) # just one page to avoid timeout

class TestConversations(TestCase):
    def test_get_records(self):
        result = extractor.get_records(KEYS["Conversation"])
        conversations = result[KEYS["Embedded"]][KEYS["Conversation"]]
        self.assertIsNotNone(conversations)
        self.assertGreater(len(conversations), 5)
    
    def test_get_all_conversations(self):
        result = extractor.get_all_records(KEYS["Conversation"], {"status": "active"}) # defaults to active
        self.assertGreater(len(result), 1)

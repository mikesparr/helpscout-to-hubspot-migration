from unittest import TestCase

import helpscout_to_hubspot as h2h

KEYS = h2h.extractor.KEYS

class TestHelp(TestCase):
    def test_is_string(self):
        s = h2h.help()
        self.assertTrue(isinstance(s, basestring))

class TestMailboxes(TestCase):
    # you must add an HELPSCOUT_API_TOKEN to .env before these will work (see README.md)  
    def test_get_mailbox_ids(self):
        result = h2h.extractor.get_mailbox_ids()
        self.assertGreater(len(result), 0)

class TestCustomers(TestCase):
    def test_get_records(self):
        result = h2h.extractor.get_records(KEYS["Customer"])
        customers = result["_embedded"][KEYS["Customer"]]
        self.assertIsNotNone(customers)
        self.assertGreater(len(customers), 5)
    
    def test_get_all_customers(self):
        result = h2h.extractor.get_all_records(KEYS["Customer"])
        self.assertGreater(len(result), 50) # multiple pages 
    
    def test_write_file(self):
        self.assertTrue(True)

class TestConversations(TestCase):
    def test_get_records(self):
        result = h2h.extractor.get_records(KEYS["Conversation"], {"status": "all"})
        conversations = result["_embedded"][KEYS["Conversation"]]
        self.assertIsNotNone(conversations)
        self.assertGreater(len(conversations), 5)
    
    def test_get_all_conversations(self):
        result = h2h.extractor.get_all_records(KEYS["Conversation"], {"status": "active"})
        self.assertGreater(len(result), 1)
    
    def test_fetch_detail(self):
        self.assertTrue(True)
    
    def test_write_file(self):
        self.assertTrue(True)


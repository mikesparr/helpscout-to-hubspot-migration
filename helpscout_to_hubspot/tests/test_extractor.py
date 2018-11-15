from unittest import TestCase

import helpscout_to_hubspot as h2h

class TestHelp(TestCase):
    def test_is_string(self):
        s = h2h.help()
        self.assertTrue(isinstance(s, basestring))

class TestMailboxes(TestCase):
    # you must add an HELPSCOUT_API_TOKEN to .env before these will work (see README.md)
    def test_get_mailboxes(self):
        result = h2h.extractor.get_mailboxes()
        mailboxes = result["_embedded"]["mailboxes"]
        self.assertIsNotNone(mailboxes)
        self.assertGreaterEqual(len(mailboxes), 3)

class TestCustomers(TestCase):
    def test_fetch_data(self):
        self.assertTrue(True)

    def test_paginate(self):
        self.assertTrue(True)
    
    def test_write_file(self):
        self.assertTrue(True)

class TestConversations(TestCase):
    def test_fetch_list(self):
        self.assertTrue(True)

    def test_paginate(self):
        self.assertTrue(True)
    
    def test_fetch_detail(self):
        self.assertTrue(True)
    
    def test_write_file(self):
        self.assertTrue(True)


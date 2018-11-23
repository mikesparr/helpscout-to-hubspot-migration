from unittest import TestCase

from helpscout_to_hubspot import loader

class TestHelp(TestCase):
    def test_is_string(self):
        s = loader.help()
        self.assertTrue(isinstance(s, basestring))


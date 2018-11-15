from unittest import TestCase

import helpscout_to_hubspot as h2h

FIELD_MAPPINGS = {
    "type": "source_type",
    "status": "status",
    "subject": "subject",
    "preview": "content",
    "mailboxId": "pipeline"
}
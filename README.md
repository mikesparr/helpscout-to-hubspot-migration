# Helpscout To Hubspot Migration
This script is intended to extract all data from Helpscout API V2 and prepare and load it into Hubspot Service Hub

# Setup
## Extractor (HelpScout)
HelpScout API uses OAuth2 and requires authorization in a browser. You must first set up your API code and secret via the admin site.

 * https://developer.helpscout.com/mailbox-api/overview/authentication

## .env file in module folder or set in your ENV
```
HELPSCOUT_API_URL=https://api.helpscout.net/v2
HELPSCOUT_CLIENT_ID={your app id}
HELPSCOUT_CLIENT_SECRET={your app secret}
```

## Transformer
TODO

## Loader (Hubspot)
TODO


# Install
```
python setup.py install
```

# Usage
```
import helpscout_to_hubspot as h2h
```
TODO

# Test
`python setup.py test` or `nosetests`

# Disclaimer
I built this for one-time use and am sharing in case others need. Absolutely no warranties or support are provided so 
use at your own risk. If APIs change after (November 2018) then you can fork this repo and customize to your needs

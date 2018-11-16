# Helpscout To Hubspot Migration
This script is intended to extract all data from Helpscout API V2 and prepare and load it into Hubspot Service Hub

# Setup
## Extractor (HelpScout)
HelpScout API uses OAuth2 and requires authorization in a browser. You must first set up your API code and secret via the admin console. A trick I like to do for the callback URL is use a webhook testing tool ( https://webhook.site ). You'll generate a unique URL and can use that to register your API App. Then you initiate the authentication request in browser via URL and add the app_id and secret. It will post a response with a `code` to your webhook tester. You then request `auth_token` per instructions and copy the `token` and not the `refresh_token`. Paste the token value in an `.env` file like below, and you have 2 hours to make requests before it expires.

 * https://developer.helpscout.com/mailbox-api/overview/authentication

## .env file in module folder
```
HELPSCOUT_API_URL=https://api.helpscout.net/v2
HELPSCOUT_API_TOKEN={token from your request here} # need to get before running
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

import logging
import os
from datetime import datetime

import requests

mailgun_private_key = os.environ('mailgun_private_key')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    send an email to registered user
    """
    email = event.get('email')
    url = event.get('url')
    status_code = event.get('status_code')
    timestamp = event.get('timestamp')
    date = datetime.fromtimestamp(timestamp)

    if not email or not url or not timestamp or status_code is None:
        logger.warning('Skip notification with email=[%s], url=[%s], status_code=[%s]', email, url, status_code)
        return

    domain = url.split('/')[2] if len(url.split('/')) >= 2 else None
    if not domain:
        logger.warning('Skip notification with domain=[%s]', domain)
        return

    mailgun_url = "https://api.mailgun.net/v3/mg.pingclock.com/messages"
    auth = ("api", mailgun_private_key)
    data = {
        "from": "Walther (pingclock.com) <alerts@mg.pingclock.com>",
        "to": [email],
        "subject": "Alert from [%s]" % url,
        "text": "[%s] -- status code: %d received from url: %s" % (date.strftime('%c'), status_code, url)
    }
    return requests.post(mailgun_url, auth=auth, data=data)

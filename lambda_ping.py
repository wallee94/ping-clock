import requests


def lambda_handler(context, event):
    url = context.get('url')
    status_code = context.get('status_code')
    mailgun_secret_key = '68838b36cbe9b42423fa0ca12f046723-41a2adb4-30fa37a7'
    slack_group = ''
    alert_emails = ['walthere.lee@gmail.com']
    is_premium = False

    res = requests.get(url, timeout=1.2)
    if res.status_code != status_code:
        data = {
            "from": "PingClock <alert@mg.pingclock.com>",
            "to": alert_emails,
            "subject": "Alert from PingClock",
            "text": "Testing some Mailgun awesomness!"
        }
        auth = ("api", mailgun_secret_key)
        url = "https://api.mailgun.net/v3/mg.pingclock.com/messages"
        res = requests.post(url, auth=auth, data=data, timeout=1)
        return

    if is_premium:
        timing = res.elapsed.total_seconds()

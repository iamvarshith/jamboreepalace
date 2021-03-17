from config import Config, Secrets
import requests
import json


def sendMail(usermail: str, subject: str, template: str, variables: dict):
    requests.post("{}".format(Secrets.MAILGUN_POST_URL),
                  auth=("api", "{}".format(Secrets.MAILGUNAPI)),
                  data={"from": "Annapurna <noreply@support.annapurna.tech>",
                        "to": [usermail],
                        "subject": "{}".format(subject),
                        "template": template,
                        "h:X-Mailgun-Variables": json.dumps(variables)

                        })

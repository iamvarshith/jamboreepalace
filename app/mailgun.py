from config import Config, Secrets
import requests
import json

# {
#     "username": "test_username",
#     "property_name": "test_property_name",
#     "no_adults": "test_no_adults",
#     "date": "test_date",
#     "location": "test_location",
#     "capacity": "test_capacity",
#     "phone": "test_phone",
#     "booking_id": "test_booking_id"
# }

def sendMail(usermail: str, subject: str, template: str, variables: dict):
    requests.post("{}".format(Secrets.MAILGUN_POST_URL),
                  auth=("api", "{}".format(Secrets.MAILGUNAPI)),
                  data={"from": "Jamboree Palace <noreply@support.jamboreepalace.me>",
                        "to": [usermail],
                        "subject": "{}".format(subject),
                        "template": template,
                        "h:X-Mailgun-Variables": json.dumps(variables)

                        })

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TESING_ENV = os.getenv('TEST_ENV')
    KING = os.getenv('king')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')


class Secrets:
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = os.getenv('GOOGLE_DISCOVERY_URL')
    OAUTHLIB_INSECURE_TRANSPORT = os.getenv('OAUTHLIB_INSECURE_TRANSPORT')
    URL = os.getenv('URL')
    MAILGUN_POST_URL = os.getenv('mailgun_post_url')
    MAILGUNAPI = os.getenv('mailgunapi')
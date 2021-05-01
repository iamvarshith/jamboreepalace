import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TESING_ENV = os.getenv('TEST_ENV')
    KING = os.getenv('king')
    SECRET_KEY = os.getenv('SECRET_KEY')
    db_user = os.getenv('db_user')
    db_password = os.getenv('db_password')
    db_host = os.getenv('db_host')
    db_port = os.getenv('db_port')
    db_name = os.getenv('db_name')
    SQLALCHEMY_DATABASE_URI = "postgresql://{user}:{password}@{host}:{port}/{name}".\
        format(user=db_user,password=db_password,host=db_host,port=db_port,name=db_name)
    print(SQLALCHEMY_DATABASE_URI)



class Secrets:
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = os.getenv('GOOGLE_DISCOVERY_URL')
    OAUTHLIB_INSECURE_TRANSPORT = os.getenv('OAUTHLIB_INSECURE_TRANSPORT')
    URL = os.getenv('URL')
    MAILGUN_POST_URL = os.getenv('mailgun_post_url')

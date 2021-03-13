import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TESING_ENV = os.getenv('TEST_ENV')
    KING = os.getenv('king')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')


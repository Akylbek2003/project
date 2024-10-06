import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

class Configuration(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Flask-Security
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    SECURITY_PASSWORD_HASH = os.getenv('SECURITY_PASSWORD_HASH')

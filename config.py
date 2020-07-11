from os import getenv
from common.utils import get_env_variable

from dotenv import load_dotenv
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Dynamic (Environmental) configurations

# Crashes if not present in environment
SECRET_KEY = get_env_variable('SECRET_KEY')
MASTER_PASSWORD = get_env_variable('MASTER_PASSWORD')

# DB_URL is postgres one if launched from Heroku or sqlite one for local testing
DB_URL = getenv("DATABASE_URL", 'sqlite:///data.db')

# Debug and testing only if explicitly stated in environment
DEBUG = getenv("DEBUG") == "TRUE"
TESTING = getenv("TESTING") == "TRUE"
ENVIRONMENT = "development" if getenv("DEVELOPMENT") == "TRUE" else "production"


class Config:
    """Flask config class."""
    SQLALCHEMY_DATABASE_URI = DB_URL

    # silence the deprecation warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True

    # jwt configs
    JWT_BLACKLIST_ENABLED = True  # enable blacklist feature
    # allow blacklisting for access and refresh tokens
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    # token expire time in seconds
    JWT_TOKEN_EXPIRES = 3600
    JWT_SECRET_KEY = SECRET_KEY

    DEBUG = DEBUG
    TESTING = TESTING
    ENV = "development"

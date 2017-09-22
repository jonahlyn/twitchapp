# config.py

class Config(object):
    """
    Common configurations
    """

    SECRET_KEY = ''

    """Twitch Autentication parameters"""
    TWITCH_KEY = ''
    TWITCH_SECRET = ''


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False


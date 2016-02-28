class BaseConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

class TestConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    DEBUG = True
    TESTING = True

class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/people.db'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    DEBUG = True

class ProdConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tmp/people_prod.db'

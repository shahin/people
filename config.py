class BaseConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

class TestConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    PRESERVE_CONTEXT_ON_EXCEPTION = False

class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/people.db'
    DEBUG = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False

class ProdConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tmp/people_prod.db'

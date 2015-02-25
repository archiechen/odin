# config

class Configuration(object):
    DATABASE = {
        'name': 'example.db',
        'engine': 'peewee.SqliteDatabase',
        'check_same_thread': False,
    }
    DEBUG = True
    SECRET_KEY = 'shhhh'

class ProductionConfig(Configuration):
    DATABASE = {
        'name': 'odin',
        'user': 'odin',
        'password': 'odin',
        'host':'127.0.0.1',
        'engine': 'peewee.PostgresqlDatabase'
    }
    DEBUG = False
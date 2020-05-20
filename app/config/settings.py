class BaseConfig:
    API_PREFIX = '/api/v1'
    TESTING = False
    DEBUG = False
    SWAGGER_UI_DOC_EXPANSION = 'list'
    SWAGGER_UI_REQUEST_DURATION = True
    RESTX_MASK_SWAGGER = False
    WORKER_STORE = '/data/worker'


class DevConfig(BaseConfig):
    FLASK_ENV = 'development'
    DEBUG = True
    MONGO_DATABASE_URI = 'mongodb://mongo-flask-app:27017/'
    MONGO_DATABASE = 'ergo'
    CELERY_BROKER = 'redis://redis-flask-service:6379/0'
    CELERY_RESULT_BACKEND = 'redis://redis-flask-service:6379/1'


class ProductionConfig(BaseConfig):
    FLASK_ENV = 'production'
    MONGO_DATABASE_URI = 'mongodb://mongo-flask-app:27017/'
    MONGO_DATABASE = 'ergo'
    CELERY_BROKER = 'redis://redis-flask-service:6379/0'
    CELERY_RESULT_BACKEND = 'redis://redis-flask-service:6379/1'


class TestConfig(BaseConfig):
    FLASK_ENV = 'development'
    DEBUG = True
    MONGO_DATABASE_URI = 'mongodb://localhost:27017/'
    MONGO_DATABASE = 'ergoTest'
    CELERY_BROKER = 'redis://localhost:6379/0'
    # CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'mongodb://localhost:27017/fromCelery'

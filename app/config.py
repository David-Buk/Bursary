class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fantastic_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'Fantastic 11'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    MAIL_SERVER = 'smtp.googleemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'fansteleven@gmail.com'
    MAIL_PASSWORD = 'fansteleven@11'

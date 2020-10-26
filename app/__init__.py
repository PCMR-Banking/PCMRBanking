from flask import Flask, Response, g
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_moment import Moment
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)
mail = Mail()
moment = Moment(app)
response = Response()

from app import routes, models, errors, email, decorators

# app.config["MAIL_SERVER"] = "smtp.sendgrid.net"
# app.config["MAIL_PORT"] = 465
# app.config["MAIL_USE_SSL"] = True
# app.config["MAIL_USERNAME"] = 'apikey'
# app.config["MAIL_PASSWORD"] = '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'
# app.config["SENDGRID_API_KEY"] = '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'

# DATABASE = os.environ['DATABASE_URL']

# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = psycopg2.connect(DATABASE)
#     return db

# def init_db():
#     with app.app_context():
#         db = get_db()
#         with app.open_resource('schema.sql', mode='r') as f:
#             db.cursor().execute(f.read())
#         db.commit()

# def query_db(query, args=(), one=False):
#     cur = get_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
#     cur.execute(query, args)
#     rv = cur.fetchall()
#     cur.close()
#     return (rv[0] if rv else None) if one else rv

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config['MAIL_USE_TLS'] = False
app.config["MAIL_USERNAME"] = 'pcmrbank@gmail.com'
app.config["MAIL_PASSWORD"] = 'kv202OUpSWSs'
app.config['MAIL_SUBJECT_PREFIX'] = 'XXX '
app.config['MAIL_DEFAULT_SENDER'] = ('No-reply PCMR Secure Bank','pcmrbank@gmail.com')

mail.init_app(app)

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='PCMR Secure Bank Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/pcmr.log', maxBytes=10240,
                                            backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info('PCMR startup')

    if app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/pcmrapp.log',
                                            maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('PCMR BANK')
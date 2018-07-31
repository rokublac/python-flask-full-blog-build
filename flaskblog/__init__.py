# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
app.config['SECRET_KEY'] = '2f6d03141c9438db59078d7c786e9a3a' # generated with secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# create database instance
db = SQLAlchemy(app)
# create brcypt instance
bcrypt = Bcrypt(app)
# creat login manager instance
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
# email config for password reset
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = '587'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'testingrokublak@gmail.com'
app.config['MAIL_PASSWORD'] = 'test1234!'
mail = Mail(app)

from flaskblog import routes
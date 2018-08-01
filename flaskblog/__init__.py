# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config


# create database instance
db = SQLAlchemy()
# create brcypt instance
bcrypt = Bcrypt()
# creat login manager instance
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
# forgot/reset password email system
mail = Mail()


def create_app(config_class=Config):
	app = Flask(__name__)
	# import Config class from config.py
	app.config.from_object(Config)

	# extensions
	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)

	# ====== import blueprints ======
	from flaskblog.main.routes import main
	from flaskblog.users.routes import users
	from flaskblog.posts.routes import posts
	app.register_blueprint(main)
	app.register_blueprint(users)
	app.register_blueprint(posts)

	return app

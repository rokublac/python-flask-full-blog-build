import os


class Config:
	SECRET_KEY = '2f6d03141c9438db59078d7c786e9a3a' # generated with secrets.token_hex(16) - and you would prbobably not hardcode these...
	SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
	# email config for password reset
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = '587'
	MAIL_USE_TLS = True
	MAIL_USERNAME = 'testingrokublak@gmail.com' # hardcoded for testing
	MAIL_PASSWORD = #password

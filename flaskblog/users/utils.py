import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


# save user upload image
def save_picture(form_picture):
	# random 8bit hex for file name ro reduce change of file name collision
	random_hex = secrets.token_hex(8)
	# split file name and extension so we can resave the file with the correct extension
	_ , f_ext = os.path.splitext(form_picture.filename)
	# concatenate hex and file extension
	picture_fn = random_hex + f_ext
	# save to profile pics directory
	picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

	# resized user image
	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)

	# save resized image
	i.save(picture_path)
	return picture_fn


# send reset email
def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='testingrokublak@gmail.com', recipients=[user.email])
	msg.body = f''' To reset your password, please visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request, please ignore this emai and no changes will be made.
'''
	mail.send(msg)
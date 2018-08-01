from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import (RegistrationForm, RequestResetForm,
								  LoginForm, UpdateAccountForm, ResetPasswordForm)
from flaskblog.users.utils import save_picture, send_reset_email


users = Blueprint('users', __name__)


# Register page
@users.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	# create and instance of RegistrationForm 
	registerForm = RegistrationForm()

	# Submit validation with flash message notifications
	if registerForm.validate_on_submit():
		# hash password into string format
		hashed_pw = bcrypt.generate_password_hash(registerForm.password.data).decode('utf-8')
		# create user
		user = User(username=registerForm.username.data, email=registerForm.email.data, password=hashed_pw)
		# add user to database
		db.session.add(user)
		db.session.commit()
		# flash message
		flash(f'Your account has successfully been created. You can now log in!', 'success')
		# redirect to login page
		return redirect(url_for('users.login'))

	return render_template('register.html', title='Register', form=registerForm)

# Login page
@users.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	# create and instance of LoginForm 
	loginForm = LoginForm()

	if loginForm.validate_on_submit():
		user = User.query.filter_by(email=loginForm.email.data).first()
		if user and bcrypt.check_password_hash(user.password, loginForm.password.data):
			login_user(user, remember=loginForm.remember_me.data)
			# if user is logging in from a restrict page direct, forward to page once logged in.
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('main.home'))
		else:
			flash('Login unsuccessful. Please check email and password', 'danger')

	return render_template('login.html', title='Login', form=loginForm)

# log out
@users.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.home'))


# account page
@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	updateAccountForm = UpdateAccountForm()

	if updateAccountForm.validate_on_submit():
		if updateAccountForm.display_picture.data:
			# call save picture function which returns a file name
			picture_file = save_picture(updateAccountForm.display_picture.data)
			# set new picture with new file name
			current_user.profile_image = picture_file
		current_user.username = updateAccountForm.username.data
		current_user.email = updateAccountForm.email.data
		db.session.commit()
		flash('Your account has been successfully updated!', 'success')
		# redirect to account page again to prevent POST GET redirect pattern (page reload and data resubmit)
		return redirect(url_for('users.account'))
	# retrieve user data
	elif request.method == 'GET':
		updateAccountForm.username.data = current_user.username
		updateAccountForm.email.data = current_user.email
	
	profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image) 
	return render_template('account.html', title='Account', profile_image=profile_image, form=updateAccountForm)


# user link (within posts) that leads to user post
@users.route('/user/<string:username>')
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	# find first user or else 404
	user = User.query.filter_by(username=username).first_or_404()
	# grab posts by specific user
	posts = Post.query.filter_by(author=user)\
		.order_by(Post.date_posted.desc())\
		.paginate(page=page, per_page=5)
	return render_template('user_posts.html', posts=posts, user=user)


# request password reset
@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	resetRequestForm = RequestResetForm()
	if resetRequestForm.validate_on_submit():
		user = User.query.filter_by(email=resetRequestForm.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', title='Reset Password', form=resetRequestForm)


# reset password
@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('Token is invalid or has expired.', 'warning')
		return redirect(url_for('users.reset_request'))
	resetForm = ResetPasswordForm()
	if resetForm.validate_on_submit():
		# hash password into string format
		hashed_pw = bcrypt.generate_password_hash(resetForm.password.data).decode('utf-8')
		user.password = hashed_pw
		db.session.commit()
		flash(f'Your password has been successfully updated! You can now log in.', 'success')
		# redirect to login page
		return redirect(url_for('users.login'))
	return render_template('reset_token.html', title='Reset Password', form=resetForm)
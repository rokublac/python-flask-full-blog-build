import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
							PostForm, RequestResetForm, ResetPasswordForm)
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


# ============= Routes set up ============= #
# Homepage
@app.route('/')
@app.route('/home')
def home():
	# grab page number from URL is user types one in
	page = request.args.get('page', 1, type=int)
	# only show 5 pages per page, desc by date
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('home.html', posts=posts)

# About page
@app.route('/about')
def about():
    return render_template('about.html', title='About')

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
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
		return redirect(url_for('login'))

	return render_template('register.html', title='Register', form=registerForm)

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	# create and instance of LoginForm 
	loginForm = LoginForm()

	if loginForm.validate_on_submit():
		user = User.query.filter_by(email=loginForm.email.data).first()
		if user and bcrypt.check_password_hash(user.password, loginForm.password.data):
			login_user(user, remember=loginForm.remember_me.data)
			# if user is logging in from a restrict page direct, forward to page once logged in.
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login unsuccessful. Please check email and password', 'danger')

	return render_template('login.html', title='Login', form=loginForm)

# log out
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))

# save user upload image
def save_picture(form_picture):
	# random 8bit hex for file name ro reduce change of file name collision
	random_hex = secrets.token_hex(8)
	# split file name and extension so we can resave the file with the correct extension
	_ , f_ext = os.path.splitext(form_picture.filename)
	# concatenate hex and file extension
	picture_fn = random_hex + f_ext
	# save to profile pics directory
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

	# resized user image
	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)

	# save resized image
	i.save(picture_path)
	return picture_fn

# account page
@app.route('/account', methods=['GET', 'POST'])
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
		return redirect(url_for('account'))
	# retrieve user data
	elif request.method == 'GET':
		updateAccountForm.username.data = current_user.username
		updateAccountForm.email.data = current_user.email
	
	profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image) 
	return render_template('account.html', title='Account', profile_image=profile_image, form=updateAccountForm)


# Add new post
@app.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
	postForm = PostForm()
	if postForm.validate_on_submit():
		post = Post(title=postForm.title.data, content=postForm.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been create!', 'success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title='New Post', form=postForm, legend='New Post')


# single post route
@app.route("/post/<int:post_id>")
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)


# update posts
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    update_post_form = PostForm()
    if update_post_form.validate_on_submit():
        post.title = update_post_form.title.data
        post.content = update_post_form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        update_post_form.title.data = post.title
        update_post_form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=update_post_form, legend='Update Post')


# delete post
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been successfully deleted.', 'success')
	return redirect(url_for('home'))


# user link (within posts) that leads to user post
@app.route('/user/<string:username>')
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	# find first user or else 404
	user = User.query.filter_by(username=username).first_or_404()
	# grab posts by specific user
	posts = Post.query.filter_by(author=user)\
		.order_by(Post.date_posted.desc())\
		.paginate(page=page, per_page=5)
	return render_template('user_posts.html', posts=posts, user=user)


# send reset email
def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='testingrokublak@gmail.com', recipients=[user.email])
	msg.body = f''' To reset your password, please visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, please ignore this emai and no changes will be made.
'''
	mail.send(msg)


# request password reset
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	resetRequestForm = RequestResetForm()
	if resetRequestForm.validate_on_submit():
		user = User.query.filter_by(email=resetRequestForm.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=resetRequestForm)


# reset password
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('Token is invalid or has expired.', 'warning')
		return redirect(url_for('reset_request'))
	resetForm = ResetPasswordForm()
	if resetForm.validate_on_submit():
		# hash password into string format
		hashed_pw = bcrypt.generate_password_hash(resetForm.password.data).decode('utf-8')
		user.password = hashed_pw
		db.session.commit()
		flash(f'Your password has been successfully updated! You can now log in.', 'success')
		# redirect to login page
		return redirect(url_for('login'))
	return render_template('reset_token.html', title='Reset Password', form=resetForm)


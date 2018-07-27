from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


# dummy data
posts = [
	{
		'author': 'Benz',
		'title': 'Post 1',
		'content': 'First post content',
		'date_posted': 'July 20, 2018'
	},
	{
		'author': 'Bella',
		'title': 'Recipe 1',
		'content': 'Second post content',
		'date_posted': 'July 25, 2018'
	}
]

# ============= Routes set up ============= #
# Homepage
@app.route('/')
@app.route('/home')
def home():
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

# account page
@app.route('/account')
@login_required
def account():
	return render_template('account.html', title='Account')

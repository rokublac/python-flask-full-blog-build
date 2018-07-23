from flask import render_template, url_for, flash, redirect
from flaskblog import app
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post


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
	# create and instance of RegistrationForm 
	registerForm = RegistrationForm()

	# Submit validation with flash message notifications
	if registerForm.validate_on_submit():
		flash(f'Account created for {registerForm.username.data}!', 'success')
		return redirect(url_for('home'))

	return render_template('register.html', title='Register', form=registerForm)

# Login page
@app.route('/login')
def login():
	# create and instance of LoginForm 
	loginForm = LoginForm()
	return render_template('login.html', title='Login', form=loginForm)

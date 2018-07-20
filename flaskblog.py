# -*- coding: utf-8 -*-
from flask import Flask, render_template
app = Flask(__name__)

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

# run in DEBUG mode when script is ran directly
if __name__ == '__main__':
    app.run(debug=True)


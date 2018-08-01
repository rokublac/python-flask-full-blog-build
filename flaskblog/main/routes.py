from flask import Blueprint, render_template, request
from flaskblog.models import Post


main = Blueprint('main', __name__)


# Homepage
@main.route('/')
@main.route('/home')
def home():
	# grab page number from URL is user types one in
	page = request.args.get('page', 1, type=int)
	# only show 5 pages per page, desc by date
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('home.html', posts=posts)

# About page
@main.route('/about')
def about():
    return render_template('about.html', title='About')
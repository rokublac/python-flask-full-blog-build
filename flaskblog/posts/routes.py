from flask import (Blueprint, render_template, 
				  url_for, flash, redirect, request, abort)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post
from flaskblog.posts.forms import PostForm


posts = Blueprint('posts', __name__)


# Add new post
@posts.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
	postForm = PostForm()
	if postForm.validate_on_submit():
		post = Post(title=postForm.title.data, content=postForm.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been create!', 'success')
		return redirect(url_for('main.home'))
	return render_template('create_post.html', title='New Post', form=postForm, legend='New Post')


# single post route
@posts.route("/post/<int:post_id>")
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)


# update posts
@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
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
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        update_post_form.title.data = post.title
        update_post_form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=update_post_form, legend='Update Post')


# delete post
@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been successfully deleted.', 'success')
	return redirect(url_for('main.home'))
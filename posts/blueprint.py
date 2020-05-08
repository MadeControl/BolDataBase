import traceback

from flask import Blueprint, request, redirect, url_for
from flask import render_template
from .forms import PostForm
from app import db
from models import Post, Tag
from flask_security import login_required
posts = Blueprint('posts', __name__, template_folder='templates', static_url_path='posts')


@posts.route('/')
def index():
    q = request.args.get('q')
    if q:
        posts = []
        for post in Post.query.all():
            if post not in posts:
                for tag in post.tags:
                    if tag.name.lower() == q.lower():
                        posts.append(post)
        posts += Post.query.filter(
            Post.title.contains(q) | Post.body.contains(q)).order_by(
            Post.created.desc())
    else:
        posts = Post.query.order_by(Post.created.desc())
    return render_template('posts/index.html', posts=posts)


# @posts.route('/<slug>/edit/', methods=['GET', 'POST'])
# def edit_post(slug):
#     post = Post.query.filter(Post.slug == slug).first_or_404()
#     if request.method == 'POST':
#         form = PostForm(formdata=request.form, obj=post)
#         form.populate_obj(post)
#         db.session.commit()
#
#         return redirect(url_for('posts.post_detail', slug=post.slug))
#
#     form = PostForm(obj=post)
#     return render_template('posts/edit_post.html', post=post, form=form)


@posts.route('/<slug>')
def post_detail(slug):
    post = Post.query.filter(Post.slug == slug).first_or_404()
    if post:
        tags = post.tags
        return render_template('posts/post_detail.html', post=post, tags=tags)
    else:
        return "<h1>This post is not exist</h1>"


@posts.route('/tags/<slug>')
def tag_detail(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    return render_template('posts/tag_detail.html', tag=tag, posts=tag.posts)


@posts.route('/tags')
def index_tag():
    tags = Tag.query.all()
    return render_template('posts/index_tag.html', tags=tags)


@posts.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        tags_name = request.form['tags']
        tags = []
        all_to_add = []
        for name in tags_name.split():
            tag = Tag.query.filter(Tag.name.contains(name)).first_or_404()
            if tag:
                tags += [tag]
                continue
            tag = Tag(name=name)
            all_to_add += [tag]
            tags += [tag]
        try:
            post = Post(title=title, body=body)
            post.tags = tags
            all_to_add.append(post)
            db.session.add_all(all_to_add)
            db.session.commit()
            return redirect(url_for('posts.index'))
        except:
            print('Something went wrong')
            print(traceback.format_exc())
            return '<h1>Something went wrong<h1>' + traceback.format_exc()
    form = PostForm()
    return render_template('posts/create_post.html', form=form, tags=Tag.query.all())

from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Blog, User, BlogMeta, Comment
from __init__ import db
from markupsafe import Markup
import os
import bleach
import boto3
import uuid
from slugify import slugify
from datetime import date

from werkzeug.utils import secure_filename
routes = Blueprint('routes', __name__)


#tmmk04#Mu
def generate_slug(title):
    return slugify(title)

def sanitize_html(content):
    """
    Sanitize HTML content using Bleach.
    """
    # Define allowed HTML tags and attributes
    allowed_tags = [
        'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul',
        'br', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img'  # Allow <img> tag for images
    ]
    allowed_attributes = {
        '*': ['class'],  # Allow class attribute on all tags
        'a': ['href', 'title', '&#39;'],  # Allow href and title attributes on <a> tags
        'img': ['src', 'alt']  # Allow src and alt attributes on <img> tags
    }

    # Sanitize the HTML content
    sanitized_content = bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes, strip=True)

    return sanitized_content

def truncate_title(title, word_limit=3):
    words = title.split()
    if len(words) > word_limit:
        return ' '.join(words[:word_limit]) + '...'
    return title

@routes.app_template_filter('truncate_title')
def truncate_title_filter(title):
    return truncate_title(title)

def truncate_content(content, word_limit=7):
    # Remove <p> if it's at the beginning
    if content.startswith('<p>'):
        content = content[3:]

    words = content.split()
    if len(words) > word_limit:
        return ' '.join(words[:word_limit]) + '...'
    return content


@routes.app_template_filter('truncate_content')
def truncate_content_filter(content):
    return truncate_content(content)



@routes.route('/')
def home():
    recent_blogs = Blog.query.order_by(Blog.date_posted.desc()).limit(2).all()
    featured_blogs = Blog.query.order_by(Blog.date_posted.desc()).limit(2).all()
    business_blogs = Blog.query.filter_by(category='Business').order_by(Blog.date_posted.desc()).all()
    technology_blogs = Blog.query.filter_by(category='Technology').order_by(Blog.date_posted.desc()).all()
    entertainment_blogs = Blog.query.filter_by(category='Entertainment').order_by(Blog.date_posted.desc()).all()
    sports_blogs = Blog.query.filter_by(category='Sports').order_by(Blog.date_posted.desc()).all()

    most_popular = Blog.query.order_by(Blog.view_count.desc()).limit(6).all()

    # Retrieve the most popular blog posts
    most_popular = Blog.query.order_by(Blog.view_count.desc()).limit(6).all()

    # Prepare the lists as per the specified order
    first_popular = most_popular[0] if most_popular else None
    second_popular = most_popular[1] if len(most_popular) > 1 else None
    tier_two = most_popular[2:4] if len(most_popular) > 2 else []
    tier_one = most_popular[4:6] if len(most_popular) > 4 else []


    # Retrieve the latest blog posts
    latest_posts = Blog.query.order_by(Blog.date_posted.desc()).limit(6).all()

    # Prepare the lists as per the specified order
    first_latest = latest_posts[0] if latest_posts else None
    second_latest = latest_posts[1] if len(latest_posts) > 1 else None
    tier_two_latest = latest_posts[2:4] if len(latest_posts) > 2 else []
    tier_one_latest = latest_posts[4:6] if len(latest_posts) > 4 else []

    # Retrieve the most popular blog posts
    most_popular_blogs = Blog.query.order_by(Blog.view_count.desc()).limit(5).all()
    today = date.today().strftime('%A, %B %d, %Y')
    
    return render_template("index.html", recent_blogs=recent_blogs, featured_blogs=featured_blogs, 
    business_blogs=business_blogs, entertainment_blogs=entertainment_blogs, sports_blogs=sports_blogs,
    technology_blogs=technology_blogs, first_popular=first_popular, second_popular=second_popular, tier_one=tier_one,
    tier_two=tier_two, first_latest=first_latest, second_latest=second_latest, tier_one_latest=tier_one_latest,
    tier_two_latest=tier_two_latest, today=today, latest_posts=latest_posts,
    most_popular_blogs=most_popular_blogs)


@routes.route('/categories/<category_name>')
def category(category_name):
    # Query blogs by category name\
    recent_blogs = Blog.query.order_by(Blog.date_posted.desc()).limit(2).all()
    today = date.today().strftime('%A, %B %d, %Y')
    category_blogs = Blog.query.filter_by(category=category_name).order_by(Blog.date_posted.desc()).all()
    return render_template("category.html", category_name=category_name, category_blogs=category_blogs,
    recent_blogs=recent_blogs, today=today)


@routes.route('/contact', methods=['POST', 'GET'])
def contact():
    recent_blogs = Blog.query.order_by(Blog.date_posted.desc()).limit(2).all()
    today = date.today().strftime('%A, %B %d, %Y')

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')  # Captured but not used
        message = request.form.get('message')

        if name and email and message:
            # Create a new Comment object without the subject
            new_comment = Comment(name=name, email=email, message=message)
            db.session.add(new_comment)
            db.session.commit()
            flash('Your comment has been added successfully!', 'success')
            return redirect(url_for('routes.contact'))  # Redirect to the contact page after submission
        else:
            flash('Please fill in all required fields.', 'error')

    return render_template("contact.html", recent_blogs=recent_blogs, today=today)


@routes.route('/single')
# @login_required
def single():
    return render_template("single.html")

@routes.route('/user/dashboard')
@login_required
def Admin():
    return render_template("Admin.html")



@routes.route('/admin/dashboard', methods=['POST', 'GET'])
@login_required
def admin_dashboard():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        keywords = request.form.get('keywords')
        category = request.form.get('category')
        content = request.form.get('editor')
        image = request.files.get('image')

        sanitized_content = sanitize_html(content)
        slug = generate_slug(title)
        canonical_url = request.url_root + 'blog/' + slug

        if image:
            filename = secure_filename(image.filename)
            new_filename = uuid.uuid4().hex + '.' + filename.rsplit('.', 1)[1].lower()
            image_path = os.path.join(current_app.root_path, 'static/BlogImages/', new_filename)
            image.save(image_path)
        else:
            new_filename = None

        new_blog = Blog(
            title=title,
            slug=slug,
            content=sanitized_content,
            blog_image=new_filename,
            category=category,
            user_id=current_user.id
        )
        db.session.add(new_blog)
        db.session.commit()

        new_blog_meta = BlogMeta(
            description=description,
            keywords=keywords,
            canonical=canonical_url,
            blog_id=new_blog.id
        )
        db.session.add(new_blog_meta)
        db.session.commit()

        flash('Blog post added successfully!', category='success')

    page = request.args.get('page', 1, type=int)
    per_page = 10
    all_blogs = Blog.query.join(User).order_by(Blog.date_posted.desc()).paginate(page=page, per_page=per_page, error_out=False)
    all_users = User.query.paginate(page=page, per_page=per_page, error_out=False)

    # Fetch comments
    all_comments = Comment.query.order_by(Comment.read_status.asc(), Comment.id.desc()).all()
    comments_with_info = []
    for comment in all_comments:
        if comment.blogpost_id:
            blog = Blog.query.get(comment.blogpost_id)
            blog_title = blog.title if blog else 'Unknown Blog'
        else:
            blog_title = 'General'

        # Calculate the number of days since the comment was posted
        days_ago = (date.today() - comment.date_posted.date()).days
        if days_ago < 7:
            time_since = f'{days_ago} days ago' if days_ago != 1 else '1 day ago'
        else:
            time_since = comment.date_posted.strftime('%B %d, %Y')

        comments_with_info.append({
            'comment': comment,
            'blog_title': blog_title,
            'time_since': time_since
        })

    return render_template(
        "Admin.html", 
        all_blogs=all_blogs, 
        all_users=all_users, 
        comments=comments_with_info
    )


from flask import request, redirect, url_for

@routes.route('/blog/<string:slug>', methods=['GET', 'POST'])
def blog(slug):
    # Retrieve the blog post from the database based on the slug
    blog_post = Blog.query.filter_by(slug=slug).first()
    if not blog_post:
        # Handle case where blog post with given slug doesn't exist
        return render_template('error.html', error_message='Blog post not found')

    # Increment view count if the request is a GET request (to avoid counting other HTTP methods)
    if request.method == 'GET':
        if blog_post.view_count is None:
            blog_post.view_count = 1
        else:
            blog_post.view_count += 1

        db.session.commit()

    # Retrieve associated BlogMeta entry if available
    blog_meta = BlogMeta.query.filter_by(blog_id=blog_post.id).first()
    today = date.today().strftime('%A, %B %d, %Y')
    recent_blogs = Blog.query.order_by(Blog.date_posted.desc()).limit(2).all()

    # Handle comment form submission
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Validate and process the comment (example: save to database)
        if name and email and message:
            new_comment = Comment(name=name, email=email, message=message, blogpost_id=blog_post.id)
            db.session.add(new_comment)
            db.session.commit()
            flash('Your comment has been added successfully!', 'success')
            return redirect(url_for('routes.blog', slug=slug))  # Redirect to the same blog post page after submission
        else:
            flash('Please fill in all required fields.', 'error')

    # Pass the blog post data to the template
    return render_template('blog.html', blog_post=blog_post, blog_meta=blog_meta, today=today, recent_blogs=recent_blogs)


@routes.route('/delete-blog/<int:blog_id>', methods=['POST'])
@login_required
def delete_blog(blog_id):
    blog_to_delete = Blog.query.get_or_404(blog_id)
    if blog_to_delete.user_id != current_user.id:
        flash('You do not have permission to delete this blog post.', category='error')
        return redirect(url_for('views.admin_dashboard'))
    
    # Delete associated BlogMeta entries
    BlogMeta.query.filter_by(blog_id=blog_id).delete()

    # Now delete the blog post
    db.session.delete(blog_to_delete)
    db.session.commit()
    flash('Blog post and associated meta data deleted successfully!', category='success')
    return redirect(url_for('views.admin_dashboard'))

@routes.route('/admin/mark-comment-read/<int:comment_id>', methods=['POST'])
@login_required
def mark_comment_read(comment_id):
    # Retrieve the comment from the database
    comment = Comment.query.get_or_404(comment_id)

    # Mark the comment as read
    comment.read_status = True
    db.session.commit()

    # Redirect back to the admin dashboard or appropriate page
    return redirect(url_for('routes.admin_dashboard'))


@routes.route('/admin/delete-comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    # Retrieve the comment from the database
    comment = Comment.query.get_or_404(comment_id)

    # Delete the comment
    db.session.delete(comment)
    db.session.commit()

    # Redirect back to the admin dashboard or appropriate page
    return redirect(url_for('routes.admin_dashboard'))



# Users
@routes.route('/users/dashboard', methods=['POST', 'GET'])
@login_required
def user_dashboard():
    if request.method == 'POST':
        # Check if the form is for submitting a blog post or a comment
        # if 'submit_blog' in request.form:
        # Handling blog post submission
        title = request.form.get('title')
        description = request.form.get('description')
        keywords = request.form.get('keywords')
        category = request.form.get('category')
        content = request.form.get('editor')
        image = request.files.get('image')

        sanitized_content = sanitize_html(content)
        slug = generate_slug(title)
        canonical_url = request.url_root + 'blog/' + slug

        if image:
            filename = secure_filename(image.filename)
            new_filename = uuid.uuid4().hex + '.' + filename.rsplit('.', 1)[1].lower()
            image_path = os.path.join(current_app.root_path, 'static/BlogImages/', new_filename)
            image.save(image_path)
        else:
            new_filename = None

        new_blog = Blog(
            title=title,
            slug=slug,
            content=sanitized_content,
            blog_image=new_filename,
            category=category,
            user_id=current_user.id
        )
        db.session.add(new_blog)
        db.session.commit()

        new_blog_meta = BlogMeta(
            description=description,
            keywords=keywords,
            canonical=canonical_url,
            blog_id=new_blog.id
        )
        db.session.add(new_blog_meta)
        db.session.commit()

        flash('Blog post added successfully!', category='success')

    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Fetch all blogs created by the current user
    all_blogs = Blog.query.filter_by(user_id=current_user.id).order_by(Blog.date_posted.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # Fetch comments associated with blogs authored by the current user
    all_comments = Comment.query.join(Blog).filter(Blog.user_id == current_user.id).order_by(Comment.read_status.asc(), Comment.id.desc()).all()
    
    comments_with_info = []
    for comment in all_comments:
        if comment.blogpost_id:
            blog = Blog.query.get(comment.blogpost_id)
            blog_title = blog.title if blog else 'Unknown Blog'
        else:
            blog_title = 'General'

        # Calculate the number of days since the comment was posted
        days_ago = (date.today() - comment.date_posted.date()).days
        if days_ago < 7:
            time_since = f'{days_ago} days ago' if days_ago != 1 else '1 day ago'
        else:
            time_since = comment.date_posted.strftime('%B %d, %Y')

        comments_with_info.append({
            'comment': comment,
            'blog_title': blog_title,
            'time_since': time_since
        })

    return render_template(
        "users.html", 
        all_blogs=all_blogs, 
        comments=comments_with_info
    )



#Mark as read for the users page
@routes.route('/admin/mark-comment-read-users/<int:comment_id>', methods=['POST'])
@login_required
def mark_comment_read_users(comment_id):
    # Retrieve the comment from the database
    comment = Comment.query.get_or_404(comment_id)

    # Mark the comment as read
    comment.read_status = True
    db.session.commit()

    # Redirect back to the admin dashboard or appropriate page
    return redirect(url_for('routes.user_dashboard'))



@routes.route('/admin/delete-comment-users/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment_users(comment_id):
    # Retrieve the comment from the database
    comment = Comment.query.get_or_404(comment_id)

    # Delete the comment
    db.session.delete(comment)
    db.session.commit()

    # Redirect back to the admin dashboard or appropriate page
    return redirect(url_for('routes.user_dashboard'))

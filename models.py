from __init__ import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)   
    password = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    blogs = db.relationship('Blog', back_populates='user')
    

class Blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(150), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    blog_image = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    view_count = db.Column(db.Integer, nullable=True)
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='blogs')
    blogmetas = db.relationship('BlogMeta')  # Adjusted to use string for relationship
    comments = db.relationship('Comment', back_populates='blog')

class BlogMeta(db.Model):
    __tablename__ = 'blog_meta'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    keywords = db.Column(db.String(200))
    canonical = db.Column(db.String(200))
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)
    read_status = db.Column(db.Boolean, default=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    blogpost_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=True)
    blog = db.relationship('Blog', back_populates='comments')

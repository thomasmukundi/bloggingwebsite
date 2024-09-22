from flask import Blueprint, render_template, request, flash, redirect, url_for
import re
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_login import login_user, login_required, logout_user, current_user
from __init__ import db

auth = Blueprint('auth', __name__)

@auth.route('/auth/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password1 =  request.form.get('password1')
        password2 = request.form.get('password2')

        print(password1)
        user = User.query.filter_by(email=email).first() #checking for existing users with the same email address

        
        if user:
            flash('Email ALready Exists', category='error')
        if len(name) < 10:
            flash('Full name must be more than 9 characters', category='error')
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email format.', category='error')
        elif not email.endswith('@gmail.com'):
            flash('Email must be a Google mail.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters long.',category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')  
        else:
            new_user = User(name=name, email=email, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created successfully', category='success')
            return redirect(url_for('auth.login'))
          

    return render_template("signup.html")


@auth.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password =  request.form.get('password')
        

        user = User.query.filter_by(email=email).first() #checking for existing users with the same email address
            
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in Successfully!', category='success')
                login_user(user, remember=True)
                # check if its admin
                if email == 'kimathiroy84@gmail.com':
                    return redirect(url_for('routes.admin_dashboard'))  # Redirect to admin dashboard
                else:
                    return redirect(url_for('routes.user_dashboard'))
                
            else:
                flash('Incorrect Password, Try Again!', category='error')

        else:   
            flash('Email does not exist!', category='error')

    return render_template("login.html")



@auth.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.home'))



from app import app, db
from flask import render_template, flash, redirect, url_for, request, session
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
from urllib.parse import urlsplit

@app.route('/login', methods = ['GET', 'POST'])
def login():
    # If the user is already logged in, redirect to the index page
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # If the user is not logged in, display the login form and handle the login logic
    form = LoginForm()
    if form.validate_on_submit():
        # Query the database for a user with the provided username
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        
        # If the user does not exist or the password is incorrect, flash an error message and redirect back to the login page
        if user is None or not user.check_password(form.password.data):
            flash(f'Invalid username or password')
            return redirect(url_for('login'))
        # If the user exists and the password is correct, log the user in and redirect to the next page or the index page
        else:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc !='':
                next_page = url_for('index')
            return redirect(next_page)

    return render_template('login.html', form=form)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    # If the user is already logged in, redirect to the index page
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # If the user is not logged in, display the registration form and handle the registration logic
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a new user with the provided username, email, and password
        user = User(
            username = form.username.data,
            email = form.email.data
        )
        # Hash the password and set it for the userßß
        user.set_password(form.password.data)

        # Try to add the user to the database and commit the changes. 
        # If there is an error (e.g., username or email already exists), rollback the session and flash an error message.
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        except Exception:
            db.session.rollback()
            flash(f'Invalid registration')
            return redirect(url_for('register'))

    return render_template('register.html', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')
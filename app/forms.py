from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, EqualTo, ValidationError, Email

from app import db
from app.models import User
import sqlalchemy as sa

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min = 3, max = 20)])
    email = StringField('Email', validators = [DataRequired()])     # Assume fake emails for now
    password = PasswordField('Password', validators = [DataRequired(), Length(min = 8)])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # Custom validation functions to check if the username and email are already in use.
    # Any function in the form class that starts with "validate_" and is followed by the name of a field will be used as a custom validator for that field.
    def validate_username(self, username):
        # scalar is used to execute the query and return a single result, or None if no result is found.
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Username already in use.')
    
    def validate_email(self, email):
        # same as above, but checks for email instead of username
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Username already in use.')
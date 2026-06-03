from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email, Optional
from wtforms.widgets import CheckboxInput, ListWidget
from datetime import datetime

from app import db
from app.models import User, Category
import sqlalchemy as sa

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])     # Email validated
    phone_number = StringField('Phone Number', validators=[Length(max=20)])   # Assume fake phone numbers for now
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
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
            raise ValidationError('Email already in use.')

class HabitForm(FlaskForm):
    name = StringField('Habit Name', validators=[DataRequired(), Length(min=1, max=128)])
    description = TextAreaField('Description', validators=[Length(max=256)])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    frequency_type = SelectField('Frequency Type', validators=[DataRequired()], choices=[
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Interval', 'Interval')
    ])
    
    # Weekly fields
    weekly_days = SelectMultipleField('Days of Week', coerce=int, validators=[Optional()], choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ])
    
    # Monthly field
    monthly_day = SelectField('Day of Month', coerce=int, validators=[Optional()], choices=[(i, str(i)) for i in range(1, 32)])
    
    # Interval fields
    interval_start_date = StringField('Start Date (YYYY-MM-DD)', validators=[Optional()])
    interval_days = IntegerField('Days Interval', validators=[Optional()])
    
    active = BooleanField('Active', default=True)
    submit = SubmitField('Save Habit')

    def __init__(self, *args, **kwargs):
        super(HabitForm, self).__init__(*args, **kwargs)
        # Populate category choices dynamically
        self.category_id.choices = [(0, '-- Select Category --')] + [(c.id, c.name) for c in db.session.scalars(sa.select(Category)).all()]


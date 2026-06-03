from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
import sqlalchemy.orm as so
import sqlalchemy as sa
from flask_login import UserMixin
from datetime import datetime, date
from typing import List, Optional

# To create the database, run the following commands in the terminal:
# >>> from app import db
# >>> db.create_all()
# This only needs to be done once, and it will create the database file (app.db) in the project directory.

# To delete the database, run the following commands in the terminal:
# >>> from app import db
# >>> db.drop_all()

# using flask-migrate, to initialize the migration environment, run the following command in the terminal:
# >>> flask db init
# >>> flask db migrate -m "Initial migration"
# >>> flask db upgrade

# From now on, whenever we make changes to the models, we can run the following commands to apply the changes to the database:
# >>> flask db migrate -m "Description of the changes"
# >>> flask db upgrade

# Modelling Relationships:

# When modelling 1-M, the 1 side:
# - The 1 side will have a relationship field that is a list of the related objects (e.g., User has a list of Habits).
# - The 1 side will use back_populates to specify the attribute in the related model

# The M side:
# - The M side will have a foreign key field that references the 1 side (e.g., Habit has a user_id that references User.id).
# - The M side will have a relationship field that references the 1 side (e.g., Habit has a user field that references User).
# - The M side will use back_populates to specify the attribute in the related model

# If either side of the relationship is a MUST (e.g., each Habit MUST have a User), 
# we use cascade to "all, delete-orphan" so if the parent object is deleted, 
# all related child objects are also deleted 

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    first_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), nullable=True)
    last_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), nullable=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True, nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True, nullable=False)
    phone_number: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20), nullable=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(128), nullable=False)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    # Relationships
    # The User has a 1-M relationship with Habit.
    # back_populates is used to specify the attribute in Habit
    # Because each habit MUST have a user, we set cascade to "all, delete-orphan" to ensure that if a user is deleted, all their habits are also deleted.
    habits: so.Mapped[List['Habit']] = so.relationship('Habit', back_populates='user', cascade='all, delete-orphan')

    # This function takes the password as input and generates a hashed version of the password.
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    # This function takes a password as input and checks if it matches the hashed password stored in the password_hash field of the User model.
    def check_password(self, password: str):
        # The check_password_hash function from werkzeug.security takes the hashed password and the input password, hashes the input password, and compares it to the stored hash. 
        # If they match, it returns True; otherwise, it returns False.
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}, Email {self.email}, Phone {self.phone_number}, Created At {self.created_at}>'

class Habit(db.Model):
    __tablename__ = 'habits'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)

    # The user_id is a FK and has a M-1 relationship with User.
    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)

    name: so.Mapped[str] = so.mapped_column(sa.String(128), nullable=False)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=True)
    category_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, sa.ForeignKey('categories.id'), nullable=True)

    # For simplicity, we can store the frequency as a string (e.g., "daily", "weekly", "monthly" and "interval").
    frequency_type: so.Mapped[str] = so.mapped_column(sa.String(32), default='Daily')
    
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    # Relationships
    # The Habit has a M-1 relationship with User and Category, and a 1-M relationship with HabitSchedule and HabitLog.
    user: so.Mapped[User] = so.relationship('User', back_populates='habits')
    category: so.Mapped[Optional[Category]] = so.relationship('Category', back_populates='habits')
    schedules: so.Mapped[List['HabitSchedule']] = so.relationship('HabitSchedule', back_populates='habit', cascade='all, delete-orphan')
    logs: so.Mapped[List['HabitLog']] = so.relationship('HabitLog', back_populates='habit', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Habit {self.name} (User {self.user_id})>'

class Category(db.Model):
    __tablename__ = 'categories'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, nullable=False)

    # Relationships
    # The Category has a 1-M relationship with Habit.
    habits: so.Mapped[List['Habit']] = so.relationship('Habit', back_populates='category', cascade='all, delete-orphan')

    def __repr__(self):
        return f'{self.name}'


class HabitSchedule(db.Model):
    __tablename__ = 'habit_schedules'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    
    # The habit_id is a FK and has a M-1 relationship with Habit.
    habit_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('habits.id'), nullable=False)

    start_date: so.Mapped[Optional[date]] = so.mapped_column(sa.Date, nullable=True)
    interval_days: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, nullable=True)
    day_of_month: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, nullable=True)

    # Relationships
    # The HabitSchedule has a M-1 relationship with Habit and a 1-M relationship with ScheduleDayOfWeek.
    habit: so.Mapped[Habit] = so.relationship('Habit', back_populates='schedules')
    weekdays: so.Mapped[List['ScheduleDayOfWeek']] = so.relationship('ScheduleDayOfWeek', back_populates='schedule', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<HabitSchedule {self.id} for Habit {self.habit_id}>'


class ScheduleDayOfWeek(db.Model):
    __tablename__ = 'schedule_day_of_week'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    schedule_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('habit_schedules.id'), nullable=False)
    day: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)  # 0=Monday .. 6=Sunday or any chosen convention

    # Relationships
    # The ScheduleDayOfWeek has a M-1 relationship with HabitSchedule.
    schedule: so.Mapped[HabitSchedule] = so.relationship('HabitSchedule', back_populates='weekdays')

    def __repr__(self):
        return f'<ScheduleDayOfWeek {self.day} (Schedule {self.schedule_id})>'


class HabitLog(db.Model):
    __tablename__ = 'habit_logs'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)

    # The habit_id is a FK and has a M-1 relationship with Habit.
    habit_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('habits.id'), nullable=False)
    
    log_date: so.Mapped[date] = so.mapped_column(sa.Date, default=date.today, nullable=False)
    completed: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=True)

    # Relationships
    # The HabitLog has a M-1 relationship with Habit.
    habit: so.Mapped[Habit] = so.relationship('Habit', back_populates='logs')

    def __repr__(self):
        return f'<HabitLog {self.id} for Habit {self.habit_id} on {self.log_date}>'


# This is needed for Flask-Login to load the user from the database when the user is logged in.
@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
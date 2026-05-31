from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
import sqlalchemy.orm as so
import sqlalchemy as sa
from flask_login import UserMixin

# To create the database, run the following commands in the terminal:
# >>> from app import db
# >>> db.create_all()
# This only needs to be done once, and it will create the database file (app.db) in the project directory. 
# If you need to make changes to the database schema, you can use Flask-Migrate to handle database migrations. 
# Alternatively, you can delete the existing database and create a new one with the updated schema.

# To delete the database, run the following commands in the terminal:
# >>> from app import db
# >>> db.drop_all()

class User(db.Model, UserMixin):
    id: so.Mapped[int] = so.mapped_column(
        sa.Integer, 
        primary_key = True)

    username: so.Mapped[str] = so.mapped_column(
        sa.String(64),
        index = True,
        unique = True,
        nullable = False
    )
    email: so.Mapped[str] = so.mapped_column(
        sa.String(120),
        index = True,
        unique = True,
        nullable = False
    )
    password_hash: so.Mapped[str] = so.mapped_column(
        sa.String(128),
        nullable = False)

    # This function is used by Flask-Login to load a user from the database given their user ID.
    @login.user_loader
    def load_user(user_id: int):
        return db.session.get(User, user_id)
    
    # This function takes password as input, hashes it using the generate_password_hash function from werkzeug.security, 
    # and stores the hashed password in the password_hash field of the User model.
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    # This function takes a password as input and checks if it matches the hashed password stored in the password_hash field of the User model.
    def check_password(self, password: str):
        # The check_password_hash function from werkzeug.security takes the hashed password and the input password, hashes the input password, and compares it to the stored hash. 
        # If they match, it returns True; otherwise, it returns False.
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>, {self.email}, {self.password_hash}>'
    
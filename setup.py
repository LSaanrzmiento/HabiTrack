from datetime import datetime, timedelta, timezone
from app import app, db
from app.models import *

# To run this script:
# % flask shell
# >>> from setup_1 import reset_database
# >>> reset_database()
# >>> quit()

def reset_database():
    with app.app_context():
        try:
            db.drop_all()
            db.create_all()

            user = User(username='admin', email='admin@example.com')
            user.set_password('admin')

            # There are 2 ways of creating the relationships between the models:
            # 1. We can create the related objects and set the relationship fields in the constructor (e.g., habit = Habit(name='Study', user=user)).
            # 2. We can just set the relationship fields (e.g., habit.user = user).
            # In this example, we will use the first approach for simplicity.
            # No need to set the user_id field in the Habit constructor, because SQLAlchemy will automatically set it when we set the user field (e.g., habit.user = user).

            habit1 = Habit(name='Study', description='Study for 1 hour', frequency_type='Daily', user=user)
            habit2 = Habit(name='Exercise', description='Go to the gym for 30 minutes', frequency_type='Weekly', user=user)
            habit3 = Habit(name='Pay Bills', description='Pay all monthly bills', frequency_type='Monthly', user=user)
            habit4 = Habit(name='Do Laundry', description='Do the laundry', frequency_type='Interval', user=user)

            category1 = Category(name='Health')
            category2 = Category(name='Finance')
            category3 = Category(name='Personal Development')
        
            # We can also set the relationships after creating the objects (e.g., habit1.category = category3).
            habit1.category = category3
            habit2.category = category1
            habit3.category = category2

            # For the daily habit, we can set the start date to today and leave the interval_days and day_of_month as None.
            habit1schedule = HabitSchedule(habit=habit1, start_date=datetime.now(timezone.utc).date(), interval_days=None, day_of_month=None)

            # For the weekly habit, we can set the start date to today and leave the interval_days and day_of_month as None. 
            # We will also need to create ScheduleDayOfWeek objects to specify which days of the week the habit should be performed.
            habit2schedule = HabitSchedule(habit=habit2, start_date=datetime.now(timezone.utc).date(), interval_days=None, day_of_month=None)
            habit2scheduledays1 =ScheduleDayOfWeek(schedule=habit2schedule, day=1)  # Tuesday
            habit2scheduledays2 =ScheduleDayOfWeek(schedule=habit2schedule, day=4)  # Friday

            # For the monthly habit, we can set the start date to today and leave the interval_days as None. 
            # We will set the day_of_month to 1 to indicate that the habit should be performed on the first day of each month.
            habit3schedule = HabitSchedule(habit=habit3, start_date=datetime.now(timezone.utc).date(), interval_days=None, day_of_month=1)

            # For the interval habit, we can set the start date to today and set the interval_days to 3 to show that the habit should be performed every 3 days.
            habit4schedule = HabitSchedule(habit=habit4, start_date=datetime.now(timezone.utc).date(), interval_days=3, day_of_month=None)

            db.session.add_all([user, category1, category2, category3, habit1, habit2, habit3, habit4, habit1schedule, habit2schedule, habit3schedule, habit4schedule, habit2scheduledays1, habit2scheduledays2])

            db.session.commit()

            print("Database reset and sample data added successfully.")

            print("Database reset.")
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            raise
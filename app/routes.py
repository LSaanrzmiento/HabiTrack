from app import app, db
from flask import render_template, flash, redirect, url_for, request, session
from app.forms import LoginForm, RegistrationForm, HabitForm
from app.models import User, Habit, HabitLog, Category, HabitSchedule, ScheduleDayOfWeek
from flask_login import current_user, login_user, login_required, logout_user
from flask_wtf.csrf import generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
from urllib.parse import urlsplit
from datetime import datetime, timezone, timedelta


# Expose a csrf_token() function to templates for manual forms
@app.context_processor
def inject_csrf_token():
    try:
        return dict(csrf_token=generate_csrf)
    except Exception:
        return dict()


@app.route('/login', methods=['GET', 'POST'])
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
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # If the user is already logged in, redirect to the index page
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # If the user is not logged in, display the registration form and handle the registration logic
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a new user with the provided username, email, and password
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        # Hash the password and set it for the user
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

    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """
    Dashboard showing habits to do today or this week.
    Habits are filtered based on their frequency type and schedule.
    """
    habits = db.session.scalars(sa.select(Habit).where(Habit.user_id == current_user.id)).all()

    # Determine which view to render: 'today' (default) or 'week'
    selected_view = request.args.get('view', 'today')

    def is_due_on_date(habit, date):
        """Return True if habit is due on the provided date."""
        if not habit.active:
            return False

        if habit.frequency_type == 'Daily':
            return True

        if habit.frequency_type == 'Weekly':
            for schedule in habit.schedules:
                if db.session.scalar(sa.select(ScheduleDayOfWeek).where(ScheduleDayOfWeek.schedule_id == schedule.id, ScheduleDayOfWeek.day == date.weekday())):
                    return True
            return False

        if habit.frequency_type == 'Monthly':
            for schedule in habit.schedules:
                if schedule.day_of_month == date.day:
                    return True
            return False

        if habit.frequency_type == 'Interval':
            for schedule in habit.schedules:
                days_since_start = (date - schedule.start_date).days
                if days_since_start >= 0 and schedule.interval_days and days_since_start % schedule.interval_days == 0:
                    return True
            return False

        return False

    # Build a mapping of frequency -> list of tuples (habit, habit_log_or_None)
    habit_view = {'daily': [], 'weekly': [], 'monthly': [], 'interval': []}

    today = datetime.now(timezone.utc).date()

    if selected_view == 'today':
        for habit in habits:
            if is_due_on_date(habit, today):
                # Ensure a HabitLog exists for today
                existing_log = db.session.scalar(sa.select(HabitLog).where(HabitLog.habit_id == habit.id, HabitLog.log_date == today))
                if existing_log is None:
                    habit_log = HabitLog(habit=habit, log_date=today, completed=False)
                    db.session.add(habit_log)
                    db.session.commit()
                    existing_log = habit_log

                habit_log = db.session.scalar(sa.select(HabitLog).where(HabitLog.habit_id == habit.id, HabitLog.log_date == today))
                habit_view[habit.frequency_type.lower()].append((habit, habit_log))

    else:  # week view
        # Consider the next 7 days inclusive and build a per-day grid (including existing logs)
        week_dates = [today + timedelta(days=i) for i in range(7)]
        # week_grid: {date: [(habit, frequency_type, habit_log_or_None), ...]}
        week_grid = {d: [] for d in week_dates}
        for habit in habits:
            for d in week_dates:
                if is_due_on_date(habit, d):
                    existing_log = db.session.scalar(sa.select(HabitLog).where(HabitLog.habit_id == habit.id, HabitLog.log_date == d))
                    week_grid[d].append((habit, habit.frequency_type, existing_log))
        # Also prepare a flattened habit_view for backwards compatibility (not used for week table)
        for d, items in week_grid.items():
            for habit, freq, log in items:
                habit_view[freq.lower()].append((habit, None))

    # Total number of due habit entries returned (used by template to show empty state)
    total_due = sum(len(v) for v in habit_view.values())

    return render_template('index.html', habit_view=habit_view, selected_view=selected_view, week_dates=week_dates if selected_view == 'week' else None, week_grid=week_grid if selected_view == 'week' else None, today=today, total_due=total_due)


@app.route('/habit_log/toggle', methods=['POST'])
@login_required
def toggle_habit_log():
    """Toggle the completed state for a HabitLog for a given habit and date. Creates the log if missing."""
    habit_id = request.form.get('habit_id')
    log_date_str = request.form.get('log_date')  # Expected YYYY-MM-DD
    if not habit_id or not log_date_str:
        flash('Missing parameters')
        return redirect(request.referrer or url_for('index'))

    try:
        log_date = datetime.fromisoformat(log_date_str).date()
    except Exception:
        flash('Invalid date')
        return redirect(request.referrer or url_for('index'))

    # Fetch habit and ensure permission
    habit = db.session.get(Habit, int(habit_id))
    if habit is None or habit.user_id != current_user.id:
        flash('Habit not found')
        return redirect(request.referrer or url_for('index'))

    # Fetch or create HabitLog
    habit_log = db.session.scalar(sa.select(HabitLog).where(HabitLog.habit_id == habit.id, HabitLog.log_date == log_date))
    if habit_log is None:
        habit_log = HabitLog(habit=habit, log_date=log_date, completed=True)
    else:
        habit_log.completed = not habit_log.completed

    db.session.add(habit_log)
    db.session.commit()

    view = request.form.get('view', 'today')
    return redirect(url_for('index', view=view))


@app.route('/habits', methods=['GET', 'POST'])
@login_required
def habits():
    """Display and manage user's habits."""
    form = HabitForm()
    
    if form.validate_on_submit():
        # Create new habit
        habit = Habit(
            name=form.name.data,
            description=form.description.data if form.description.data else None,
            category_id=form.category_id.data if form.category_id.data != 0 else None,
            frequency_type=form.frequency_type.data,
            active=form.active.data,
            user_id=current_user.id
        )
        db.session.add(habit)
        db.session.flush()
        
        # Create schedules based on frequency type
        if form.frequency_type.data == 'Weekly' and form.weekly_days.data:
            schedule = HabitSchedule(habit=habit)
            db.session.add(schedule)
            db.session.flush()
            for day in form.weekly_days.data:
                schedule_day = ScheduleDayOfWeek(schedule=schedule, day=day)
                db.session.add(schedule_day)
        
        elif form.frequency_type.data == 'Monthly' and form.monthly_day.data:
            schedule = HabitSchedule(habit=habit, day_of_month=form.monthly_day.data)
            db.session.add(schedule)
        
        elif form.frequency_type.data == 'Interval' and form.interval_start_date.data and form.interval_days.data:
            try:
                start_date = datetime.fromisoformat(form.interval_start_date.data).date()
                schedule = HabitSchedule(habit=habit, start_date=start_date, interval_days=form.interval_days.data)
                db.session.add(schedule)
            except ValueError:
                flash('Invalid start date format')
                return render_template('habit_management.html', form=form, habits=db.session.scalars(sa.select(Habit).where(Habit.user_id == current_user.id)).all())
        
        db.session.commit()
        flash(f'Habit "{habit.name}" created successfully!')
        return redirect(url_for('habits'))
    
    # Get all habits for the current user
    habits_list = db.session.scalars(sa.select(Habit).where(Habit.user_id == current_user.id)).all()
    
    return render_template('habit_management.html', form=form, habits=habits_list)


@app.route('/habits/<int:habit_id>/delete', methods=['POST'])
@login_required
def delete_habit(habit_id):
    """Delete a habit."""
    habit = db.session.get(Habit, habit_id)
    if habit is None or habit.user_id != current_user.id:
        flash('Habit not found')
        return redirect(url_for('habits'))
    
    habit_name = habit.name
    db.session.delete(habit)
    db.session.commit()
    flash(f'Habit "{habit_name}" deleted!')
    return redirect(url_for('habits'))


@app.route('/habits/<int:habit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_habit(habit_id):
    """Edit an existing habit."""
    habit = db.session.get(Habit, habit_id)
    if habit is None or habit.user_id != current_user.id:
        flash('Habit not found')
        return redirect(url_for('habits'))
    
    form = HabitForm()
    
    if form.validate_on_submit():
        # Update habit
        habit.name = form.name.data
        habit.description = form.description.data if form.description.data else None
        habit.category_id = form.category_id.data if form.category_id.data != 0 else None
        habit.frequency_type = form.frequency_type.data
        habit.active = form.active.data
        
        # Clear existing schedules
        for schedule in habit.schedules:
            db.session.delete(schedule)
        
        # Create schedules based on frequency type
        if form.frequency_type.data == 'Weekly' and form.weekly_days.data:
            schedule = HabitSchedule(habit=habit)
            db.session.add(schedule)
            db.session.flush()
            for day in form.weekly_days.data:
                schedule_day = ScheduleDayOfWeek(schedule=schedule, day=day)
                db.session.add(schedule_day)
        
        elif form.frequency_type.data == 'Monthly' and form.monthly_day.data:
            schedule = HabitSchedule(habit=habit, day_of_month=form.monthly_day.data)
            db.session.add(schedule)
        
        elif form.frequency_type.data == 'Interval' and form.interval_start_date.data and form.interval_days.data:
            try:
                start_date = datetime.fromisoformat(form.interval_start_date.data).date()
                schedule = HabitSchedule(habit=habit, start_date=start_date, interval_days=form.interval_days.data)
                db.session.add(schedule)
            except ValueError:
                flash('Invalid start date format')
                return render_template('habit_edit.html', form=form, habit=habit)
        
        db.session.commit()
        flash(f'Habit "{habit.name}" updated successfully!')
        return redirect(url_for('habits'))
    
    # Pre-populate form with habit data
    if request.method == 'GET':
        form.name.data = habit.name
        form.description.data = habit.description
        form.category_id.data = habit.category_id or 0
        form.frequency_type.data = habit.frequency_type
        form.active.data = habit.active
        
        # Pre-populate frequency-specific fields
        if habit.frequency_type == 'Weekly' and habit.schedules:
            schedule = habit.schedules[0]
            form.weekly_days.data = [sd.day for sd in db.session.scalars(sa.select(ScheduleDayOfWeek).where(ScheduleDayOfWeek.schedule_id == schedule.id)).all()]
        
        elif habit.frequency_type == 'Monthly' and habit.schedules:
            form.monthly_day.data = habit.schedules[0].day_of_month
        
        elif habit.frequency_type == 'Interval' and habit.schedules:
            schedule = habit.schedules[0]
            form.interval_start_date.data = schedule.start_date.isoformat() if schedule.start_date else ''
            form.interval_days.data = schedule.interval_days
    
    return render_template('habit_edit.html', form=form, habit=habit)


@app.route('/progress')
@login_required
def progress():
    """Display habit progress and statistics."""
    habits_list = db.session.scalars(sa.select(Habit).where(Habit.user_id == current_user.id)).all()
    
    # Calculate completion stats for each habit
    habit_stats = []
    for habit in habits_list:
        logs = db.session.scalars(sa.select(HabitLog).where(HabitLog.habit_id == habit.id)).all()
        completed = sum(1 for log in logs if log.completed)
        total = len(logs)
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        habit_stats.append({
            'habit': habit,
            'completed': completed,
            'total': total,
            'completion_rate': completion_rate
        })
    
    return render_template('habit_progress.html', habit_stats=habit_stats)
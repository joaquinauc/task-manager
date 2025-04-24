from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit

import sqlalchemy as sa

from app import app, db
from app.forms import LoginForm, RegistrationForm, AddTaskForm, EmptyForm, EditTaskForm, SelectForm
from app.models import User, Task


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = db.first_or_404(sa.select(User).where(User.username == current_user.username))
    query = user.tasks.select().order_by(Task.id.desc())
    tasks = db.session.scalars(query).all()
    form = AddTaskForm()
    select_form = SelectForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            task = Task(title=form.task.data, author=current_user, progress=1)
            db.session.add(task)
            db.session.commit()
            return redirect(url_for('dashboard'))

    elif request.method == 'GET':
        updated = False
        for task in tasks:
            status = request.args.get(f'status{task.id}')
            priority = request.args.get(f'priority{task.id}')

            try:
                if status:
                    status = int(status)
                    if 1 <= status <= 3 and status != task.progress:
                        task.progress = status
                        updated = True

                elif priority:
                    priority = int(priority)
                    if 1 <= priority <= 3 and priority != task.priority:
                        updated = True
                        task.priority = priority

            except ValueError:
                print(f"Error: 'Task ID {task.id}' has an invalid status or priority value.")

        if updated:
            db.session.commit()
            return redirect(url_for('dashboard'))
    return render_template('dashboard.html', title='Dashboard', tasks=tasks, form=form, select_form=select_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/task/<id>-<title>', methods=['GET', 'POST'])
def task(id, title):
    form = EditTaskForm()
    select_form = SelectForm()
    task = db.session.scalar(sa.select(Task).where(Task.id == id, Task.title == title))

    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = request.get_json()
            task.due_date = data.get('due_date', task.due_date)
            db.session.commit()
        else:
            if form.validate_on_submit():
                task.title = form.title.data
                task.body = form.description.data
                task.progress = select_form.status.data
                task.priority = select_form.priority.data
                db.session.commit()
                return redirect(url_for('dashboard'))

    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.body
        select_form.status.data = str(task.progress)
        select_form.priority.data = str(task.priority)
    return render_template('task.html', title='Edit Task', form=form, task=task, select_form=select_form)


@app.route('/delete/<id>-<title>', methods=['GET', 'POST'])
def delete(title, id):
    form = EmptyForm()
    if form.validate_on_submit():
        task = db.session.scalar(sa.select(Task).where(Task.id == id, Task.title == title))
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('dashboard'))

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length

import sqlalchemy as sa
from wtforms.widgets.core import TextArea

from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Please enter your username.")])
    password = PasswordField('Password', validators=[DataRequired(message="Please enter your password.")])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')


class AddTaskForm(FlaskForm):
    task = StringField('New Task', validators=[DataRequired()])
    submit = SubmitField('Add Task')


class EditTaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(0, 140)])
    activity = StringField('Activities')
    check_done = BooleanField('Completed')
    submit = SubmitField('Apply')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class SelectForm(FlaskForm):
    status = SelectField('Task Status', choices=[(1, 'Pending'), (2, 'In Progress'), (3, 'Completed')])
    priority = SelectField('Priority', choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')])

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User
import datetime

def email_check(form, field):
    """
    Checks to see that the proposed email address is not already in use.
    """
    email = User.query.filter_by(email=str(form.email.data)).first()
    if email:
        raise ValidationError("That email address is already in use. Please choose another.")


def password_check(form, field):
    """
    Checks to see if the two password fields are equal.
    """
    if form.password.data != form.verify_password.data:
        raise ValidationError('Passwords must match.')


def username_check(form, field):
    """
    Checks to see that the proposed username is not already in use.
    """
    username = User.query.filter_by(username=str(form.username.data)).first()
    if username:
        raise ValidationError("That user name is already in use. Please choose another.")


def yob_check(form, field):
    """
    1. Checks to make sure the year of birth (YOB) can be converted into an integer.
    2. Checks to make sure the provided can be converted into a datetime object.
    3. Checks to make sure the proposed age is less than 125 years old.
    """
    try:
        yob = int(form.yob.data)
        if datetime.datetime.utcnow() - datetime.datetime(yob, 1, 1) > datetime.timedelta(days=45625):
            raise ValidationError("The year entered exceeds the maximum human life span.")
        elif datetime.datetime.utcnow() - datetime.datetime(yob, 1, 1) < datetime.timedelta(days=6570):
            raise ValidationError("Users under the age of 18 are not allowed to Galatea.")
    except:
        raise ValidationError("Please enter a valid, four-digit year of birth.")


class RegisterForm(FlaskForm):
    email = StringField('Email address', validators=[
        DataRequired(), 
        Email(), 
        Length(max=254),
        email_check
    ], render_kw={'style': 'width:50%;', 'placeholder': 'Email address'})
    password = PasswordField('Password', validators=[
        DataRequired()
    ], render_kw={'style': 'width:50%;', 'placeholder': 'Password'})
    verify_password = PasswordField('Verify password', validators=[
        DataRequired(),
        password_check
    ], render_kw={'style': 'width:50%;', 'placeholder': 'Verify password'})
    username = StringField('User name', validators=[
        DataRequired(),
        Length(max=100),
        username_check
    ], render_kw={'style': 'width:50%;', 'placeholder': 'User name'})
    yob = StringField('Year of birth', validators=[
        DataRequired(),
        yob_check,
        Length(min=4, max=4)
    ], render_kw={'style': 'width:45%;', 'placeholder': 'Year of birth'})
    gender = SelectField('Gender', choices=[
        ('1', 'Male'),
        ('2', 'Female')
    ], validators=[
        DataRequired(),
    ], render_kw={'style': 'width:50%;'})
    submit = SubmitField('Register >>', render_kw={'class': 'btn btn-primary btn-lg'})


class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[
        DataRequired(),
        Email()
    ], render_kw={'style': 'width:50%;', 'placeholder': 'Email address'})
    password = PasswordField('Password', validators=[
        DataRequired()
    ], render_kw={'style': 'width:50%;', 'placeholder':'Password'})
    submit = SubmitField('Log in >>', render_kw={'class': 'btn btn-primary btn-lg'})


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email address', validators=[
        DataRequired(),
        Email()
    ], render_kw={'style': 'width:50%;', 'placeholder': 'Email address'})
    submit = SubmitField('Request password reset >>', render_kw={'class': 'btn btn-primary btn-lg'})


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
        DataRequired()
    ], render_kw={'style': 'width:50%;', 'placeholder':'Password'})
    verify_password = PasswordField('Verify password', validators=[
        DataRequired(), 
        password_check
    ], render_kw={'style': 'width:50%;', 'placeholder':'Verify password'})
    submit = SubmitField('Reset password >>', render_kw={'class': 'btn btn-primary btn-lg'})
    
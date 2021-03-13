from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, DateTimeField, \
    TextAreaField, FileField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, regexp, NumberRange
from flask import session


class RegistrationForm(FlaskForm):
    name = StringField('Username',
                       validators=[DataRequired(), Length(min=2, max=40)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=6, max=40)])
    confirm_password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=6, max=40)])

    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=6, max=40)])
    submit = SubmitField('Sign Up')

import random
import requests

from flask import render_template, redirect, url_for, flash, request
from app import app, login_manager, bcrypt, db
from app.models import User, CourseName
from app.forms import RegistrationForm, LoginForm
from flask_login import current_user, login_user,logout_user


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))

        else:
            flash("unsucessful login", 'danger')
    if not form.validate_on_submit():
        flash("Enter valid details", 'warning')
    return render_template('login.html', title='login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        unique_id = (random.randint(100000000000, 10000000000000))
        print(form.email.data)

        user = User(unique_id=unique_id, username=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))
    else:

        return render_template('registration.html', title='Register', form=form)


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("logged out Sucessfullly", 'sucess')
        return redirect(url_for('home'))
    return redirect(url_for('login'))


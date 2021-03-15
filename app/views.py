import random
import requests
from config import Secrets
from flask import render_template, redirect, url_for, flash, request
from app import app, login_manager, bcrypt, db,client
from app.models import User
from app.forms import RegistrationForm, LoginForm
from flask_login import current_user, login_user,logout_user
from oauthlib.oauth2 import WebApplicationClient
import json

print(Secrets.GOOGLE_DISCOVERY_URL)

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


@app.route("/login/google")
def login_google():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri='{}/login/google/callback'.format(Secrets.URL),
        scope=["openid", "email", "profile"],
        prompt="select_account",

    )
    return redirect(request_uri)


@app.route("/login/google/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(Secrets.GOOGLE_CLIENT_ID, Secrets.GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]

    else:
        return "User email not available or not verified by Google.", 400

    # we can now insert the incoming data into the db
    user = User.query.filter_by(email=users_email).first()
    if user is None:
        user = User(unique_id=unique_id, username=users_name, email=users_email, image_file=picture)

        db.session.add(user)
        db.session.commit()

        requests.post("https://api.mailgun.net/v3/support.annapurna.tech/messages",
                      auth=("api", "key-179896d154b2bdb3c6b6d0201268f295"),
                      data={"from": "Annapurna <noreply@support.annapurna.tech>",
                            "to": [users_email],
                            "subject": "Welcome to annapurna {}".format(user.username),
                            # "text": "Please click the link {}".format(url),
                            "template": "welcome",
                            "h:X-Mailgun-Variables": json.dumps({"sitelink": "https://www.annapurna.tech"})

                            })
        login_user(user)
        return redirect(url_for('home'))
    else:
        login_user(user)

        return redirect(url_for('home'))



# Google Bs
def get_google_provider_cfg():
    return requests.get(Secrets.GOOGLE_DISCOVERY_URL).json()
import random
import requests
from config import Secrets
from flask import render_template, redirect, url_for, flash, request
from app import app, login_manager, bcrypt, db, client
from app.models import User, Property
from app.forms import RegistrationForm, LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from oauthlib.oauth2 import WebApplicationClient
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import json
from app.mailgun import sendMail

sq = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# @login_manager.unauthorized_handler
# def unauthorized():
#     return redirect(url_for('login'))


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            try:
                if not user.email_confirm:
                    flash('please Confirm your email id to continue', 'warning')
                    return redirect(url_for('login'))
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user)
                    next_page = request.args.get('next')
                    print(next_page)
                    return redirect(next_page) if next_page else redirect(url_for('home'))
            except:
                if user.password == 'Google_login':
                    flash('You have signed in with google before please user the same login method', 'warning')
                    return redirect(url_for('login'))

            else:
                return redirect(url_for("home"))

        else:
            flash("unsucessful login", 'danger')

    return render_template('login.html', title='login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    print(form.name.data)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if User.query.filter_by(email=form.email.data).first():
        flash('This email is already Registered', 'warning')
        return redirect(url_for('register'))
    if User.query.filter_by(username=form.name.data).first():
        flash('Username is taken', 'warning')
        return redirect(url_for('register'))
    if form.validate_on_submit():
        print('yes')
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        unique_id = (random.randint(100000000000, 10000000000000))
        print(form.email.data)

        user = User(unique_id=unique_id, username=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        token = sq.dumps(form.email.data, salt="itstosaltytonothavesaltinthesaltlake")
        url = "{}/confirm_email/".format(Secrets.URL) + token
        variables = {'url_email_confirm': '{}'.format(url)}
        print(variables)

        sendMail(usermail=str(form.email.data), subject='Welcome to Jamboreepalace {}'.format(form.name.data),
                 template='emailconfirm', variables=variables)

        return redirect(url_for('login'))

    else:
        print(form.errors)
        return render_template('register.html', title='Register', form=form)


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = sq.loads(token, salt="itstosaltytonothavesaltinthesaltlake", max_age=36000)
    except BadTimeSignature:
        return "404"
    except SignatureExpired:
        flash("Time expired", 'warning')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=email).first
    user().email_confirm = True
    email_email = user().email
    db.session.add(user())
    db.session.commit()

    return render_template('mail_confirm.html', user=user)


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
    testurl = '{}/login/google/callback'.format(Secrets.URL)
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=testurl,
        scope=["openid", "email", "profile"],
        prompt="select_account",

    )
    print(testurl)
    return redirect(request_uri)


@app.route("/login/google/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    print(code)

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
    print(token_url)

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(Secrets.GOOGLE_CLIENT_ID, Secrets.GOOGLE_CLIENT_SECRET),
    )
    print(Secrets.GOOGLE_CLIENT_ID, Secrets.GOOGLE_CLIENT_SECRET)
    print(token_response.json())
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

        # unique_id = 4548545785
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]

    else:
        return "User email not available or not verified by Google.", 400

    # we can now insert the incoming data into the db
    user = User.query.filter_by(email=users_email).first()
    if user is None:
        user = User(unique_id=unique_id, username=users_name, email=users_email, password="Google_login",profile_img=picture)

        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))

    else:
        login_user(user)

        return redirect(url_for('home'))


# Google Bs
def get_google_provider_cfg():
    return requests.get(Secrets.GOOGLE_DISCOVERY_URL).json()


@app.route('/enlist', methods=['GET', 'POST'])
@login_required
def enlist():
    return render_template('enlist.html')


@app.route('/enlist/property', methods=['GET', 'POST'])
def enlistProperty():
    if current_user.is_authenticated:
        if request.method == "POST":
            fname = request.form['fname']
            lname = request.form['lname']
            owner_name = fname + ' ' + lname
            property_name = request.form['vname']
            address = request.form['address']
            features = request.form['description']
            contact_manager = request.form['phone']
            contact_front = request.form['frontDeskContact']
            partitions = request.form['partitions']
            capacity = request.form['capacity']
            pan_number = request.form['panNo']
            best_price = request.form['bestPrice']
            owner_id = current_user.id
            enlistment_status = 'pending'

            enlistproperty = Property(owner_id=owner_id, owner_name=owner_name,
                                      property_name=property_name, address=address, features=features,
                                      contact_manager=contact_manager, contact_front=contact_front,
                                      partitions=partitions,
                                      capacity=capacity, pan_number=pan_number, best_price=best_price,
                                      enlistment_status=enlistment_status)
            db.session.add(enlistproperty)
            db.session.commit()
    return '200'


@app.route('/profile')
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user)


@app.route('/profile/previous_bookings')
@login_required
def prevBookings():
    return render_template('previousbookings.html')


@app.route('/profile/enlistment_application')
@login_required
def enlistApplication():
    properties = current_user.property
    enlist_application = Property.query.filter(
        Property.owner_id == current_user.id, Property.enlistment_status == 'pending').all()
    print(enlist_application)
    # for i in range(len(properties)):
    #     if properties.enlistment_status
    return render_template('enlistapp.html', properties=enlist_application)


@app.route('/profile/manageproperty')
@login_required
def manageProperty():
    return render_template('manage.html')


@app.route('/about')
def about():
    return render_template('register.html')


@app.route('/spaces', methods=['GET', 'POST'])
@login_required
def spaces():
    return 'pending'


@app.route('/contact')
def contact():
    return render_template('register.html')


@app.route('/property/<token>', methods=['get', 'post'])
@login_required
def individual_property(token):
    properties = current_user.property
    enlist_application = Property.query.filter(
        Property.owner_id == current_user.id, Property.owner_id == str(token)).all()
    print(enlist_application)
    return 'pending'

import hashlib
import os
import random
import requests
from flask_wtf import file
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename

from config import Secrets
from flask import render_template, redirect, url_for, flash, request, jsonify
from app import app, login_manager, bcrypt, db, client, ALLOWED_EXTENSIONS
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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if User.query.filter_by(email=form.email.data).first():
        flash('This email is already Registered', 'warning')
        return redirect(url_for('register'))
    if User.query.filter_by(username=form.name.data).first():
        flash('Username is taken', 'warning')
        return redirect(url_for('register'))
    if form.validate_on_submit():

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
        return render_template('registration.html', title='Register', form=form)


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
        user = User(unique_id=unique_id, username=users_name, email=users_email, password="Google_login",
                    profile_img=picture)

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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/enlist/property', methods=['GET', 'POST'])
def enlistProperty():
    if current_user.is_authenticated:
        if request.method == "POST":
            fname = request.form['fname']
            lname = request.form['lname']
            owner_name = fname + ' ' + lname
            property_name = request.form['vname']
            address = request.form['address']
            features = request.form['desc']
            contact_manager = request.form['phn']
            contact_front = request.form['fd-contact']
            partitions = request.form['partions']
            capacity = request.form['Capacity']
            pan_number = request.form['pno']
            best_price = request.form['bp']
            owner_id = current_user.id
            enlistment_status = 'pending'
            file = request.files['myFile']
            if contact_front == '':
                contact_front = None
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            enlistproperty = Property(owner_id=owner_id, owner_name=owner_name,
                                      property_name=property_name, address=address, features=features,
                                      contact_manager=contact_manager, contact_front=contact_front,
                                      partitions=partitions,
                                      capacity=capacity, pan_number=pan_number, best_price=best_price,
                                      image=str(filename),
                                      enlistment_status=enlistment_status)
            db.session.add(enlistproperty)
            db.session.commit()
            return jsonify({})
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
    print(type(enlist_application))
    # for i in range(len(properties)):
    #     if properties.enlistment_status
    return render_template('enlistapp.html', properties=enlist_application)


@app.route('/profile/manageproperty')
@login_required
def manageProperty():
    return render_template('manage.html')


@app.route('/about')
def about():
    return render_template('space_gallery.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/property/<token>', methods=['get', 'post'])
@login_required
def individual_property(token):
    properties = current_user.property
    enlist_application = Property.query.filter(
        Property.owner_id == current_user.id, Property.owner_id == str(token)).all()
    print(enlist_application)
    return 'pending'


@app.route('/api/location', methods=['POST'])
def location():
    lat = request.form['lat']
    long = request.form['long']
    key = "AIzaSyCFeIvoO8acKzK7czHvQoNnTl4ObJeajNo"
    url = "https://maps.googleapis.com/maps/api/geocode/json?latlng={0},{1}&key={2}".format(lat, long, key)
    print(url)
    i = requests.get(url)
    j = i.json()
    k = j['results'][5]['formatted_address'].split(',')[0]
    return jsonify({'city': k})


@app.route('/api/search', methods=['POST'])
def search_api():
    location = request.form['location']
    type_property = request.form['type']
    arrival_date = request.form['arrival']
    depature_date = request.form['depature']
    no_guests = request.form['guests']
    avilable = Property.query.filter_by(address=location).all()
    print(avilable[1].property_name)
    return 'kll'


@app.route('/spaces', methods=['GET'])
def spaces():
    location = request.args.get('location')
    type_property = request.args.get('type')
    arrival_date = request.args.get('arrival')
    depature_date = request.args.get('depature')
    no_guests = request.args.get('guests')
    avilable1 = Property.query.filter(Property.address == location).all()[:7]
    avilable2 = Property.query.filter(Property.address == location).all()[7:14]
    print(avilable1)
    return render_template('space_gallery.html', avilable1=avilable1, avilable2=avilable2)


@app.route('/spaces/<token>', methods=['get', 'post'])
def individualProperties(token):
    property = Property.query.filter(Property.id == token).first()
    print(property)
    return render_template('space.html',property = property)

# @app.route('/payu', methods=['POST', "GET"])
# def payu():
#
#
#
#     txnid = hashlib.md5(str((random.randint(100000, 999999) + current_user.email)).encode()).hexdigest()
#
#     hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
#     hash_string = ''
#     hashVarsSeq = hashSequence.split('|')
#
#     param_dict = {
#         'key': 'ZOwH3J89',
#         'txnid': txnid,
#         'amount': str(txn_amount),
#         'productinfo': str(test_type),
#         'firstname': order.name,
#         'email': current_user.email,
#         'phone': current_user.phone,
#         'surl': final_url + '/payu/success',
#         'furl': final_url + '/payu/gg',
#         'hash': '',
#         'service_provider': 'payu_paisa'
#
#     }
#     for i in hashVarsSeq:
#         try:
#             hash_string += str(param_dict[i])
#         except Exception:
#             hash_string += ''
#         hash_string += '|'
#     hash_string += 'LpoLYPU8dV'
#     hashh = hashlib.sha512(hash_string.encode()).hexdigest().lower()
#     param_dict['hash'] = hashh
#     return render_template('payu.html', param=param_dict)
#
# @app.route('/payu/success', methods=['POST', 'GET'])
# def payu_success():
#     order = TestOrder.query.filter_by(id=session['order_id']).first()
#     status = request.form["status"]
#     firstname = request.form["firstname"]
#     amount = request.form["amount"]
#     txnid = request.form["txnid"]
#     posted_hash = request.form["hash"]
#     key = request.form["key"]
#     productinfo = request.form["productinfo"]
#     email = request.form["email"]
#     salt = "LpoLYPU8dV"
#     retHashSeq = salt + '|' + status + '|||||||||||' + email + '|' + firstname + '|' + productinfo + '|' + amount + '|' + txnid + '|' + key
#     hashh = hashlib.sha512(retHashSeq.encode()).hexdigest().lower()
#     if hashh == posted_hash:
#         order.status_txn = 'success' + '  ,\u20B9' + session['amount']
#
#         db.session.commit()
#         pay_status = 1
#
#     return render_template('postpayment.html', status=pay_status, transaction_id=txnid)
#
#
# @app.route('/payu/gg', methods=['POST', 'GET'])
# def payu_fail():
#     order = TestOrder.query.filter_by(id=session['order_id']).first()
#     order.status_txn = 'fail' + '  ,\u20B9' + str(session['amount'])
#
#     db.session.commit()
#     pay_status = 0
#     return render_template('postpayment.html', status=pay_status, transaction_id=request.form['txnid'])
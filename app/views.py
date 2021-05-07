import hashlib
import os
import random
import requests
from flask_wtf import file
from sqlalchemy import inspect
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename

from config import Secrets
from flask import render_template, redirect, url_for, flash, request, jsonify
from app import app, login_manager, bcrypt, db, client, ALLOWED_EXTENSIONS
from app.models import User, Property, Bookings
from app.forms import RegistrationForm, LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from oauthlib.oauth2 import WebApplicationClient
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import json
from app.mailgun import sendMail
import datetime
from datetime import datetime, date

sq = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# @login_manager.unauthorized_handler
# def unauthorized():
#     return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(400)
def page_error(e):
    return render_template('400.html'), 400


@app.route('/')
@app.route('/home')
def home():
    null_query = Property.query.all()[-5:]
    return render_template('home.html', null_query=null_query)


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
            # file = request.files.getlist("myFile")
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
    user = current_user
    previous_booking = Bookings.query.filter(Bookings.user_id == current_user.id).all()
    previous_booking_list = []

    def object_as_dict(obj):
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}

    previous_booking_list = []
    for i in previous_booking:
        previous_booking_list.append(object_as_dict(i))
    for i in range(len(previous_booking_list)):
        property_details = Property.query.filter(Property.id == previous_booking_list[i]['property_id']).first()
        previous_booking_list[i].update(object_as_dict(property_details))

    print(previous_booking_list[i])
    return render_template('previousbookings.html', user=user, previous_booking_list=previous_booking_list)


@app.route('/profile/enlistment_application')
@login_required
def enlistApplication():
    enlist_application = Property.query.filter(
        Property.owner_id == current_user.id, Property.enlistment_status == 'pending').all()
    print(type(enlist_application))

    return render_template('enlistapp.html', properties=enlist_application)


@app.route('/profile/manageproperty')
@login_required
def manageProperty():
    properties = Property.query.filter(
        Property.owner_id == current_user.id, Property.enlistment_status == 'approved').all()
    return render_template('manage.html', properties=properties)


@app.route('/about')
def about():
    return render_template('space_gallery.html')


@app.route('/contact')
def contact():
    return render_template('testing.html')


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
    print(arrival_date)
    avilable1 = Property.query.filter(Property.address == location, Property.enlistment_status == 'approved').all()[:7]

    null_query = Property.query.filter(Property.enlistment_status == 'approved').all()[-5:]
    print(null_query)

    return render_template('space_gallery.html', avilable1=avilable1, null_query=null_query)


@app.route('/spaces/<token>', methods=['get', 'post'])
def individualProperties(token):
    property = Property.query.filter(Property.id == token).first()
    print(property)
    return render_template('space.html', property=property)


@app.route('/payu', methods=['POST', "GET"])
@login_required
def payu():
    if request.method == 'POST':
        date_format = "%m/%d/%Y"
        room_type = request.form['room']
        date_arrival = request.form['date-arrival']
        date_departure = request.form['date-departure']
        adults = request.form['adults']
        property_id = request.form['property_id']
        property_selected = Property.query.filter(Property.id == property_id).first()
        a = datetime.strptime(date_arrival, date_format)
        b = datetime.strptime(date_departure, date_format)
        days = b - a
        if days.days <= 0:
            txn_amount = property_selected.best_price
        else:
            billed_for_days = days.days
            txn_amount = billed_for_days * property_selected.best_price
        txnid = hashlib.md5(str((random.randint(100000, 999999) + current_user.id)).encode()).hexdigest()
        new_booking = Bookings(arrival_data=date_arrival, depature_data=date_departure, no_adults=adults,
                               user_id=current_user.id,
                               property_id=property_id, date_booking=datetime.today(), payment_id=txnid,
                               payment_status='pending', payment_amount=txn_amount)

        db.session.add(new_booking)

        db.session.commit()

        hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
        hash_string = ''
        hashVarsSeq = hashSequence.split('|')

        param_dict = {
            'key': 'ZOwH3J89',
            'txnid': str(txnid),
            'amount': str(txn_amount),
            'productinfo': str(property_selected.property_name),
            'firstname': current_user.username,
            'email': current_user.email,
            'phone': str(9949588645),
            'surl': str(Secrets.URL + '/payu/success'),
            'furl': str(Secrets.URL + '/payu/failed'),
            'hash': '',
            'service_provider': 'payu_paisa'

        }
        for i in hashVarsSeq:
            try:
                hash_string += str(param_dict[i])
            except Exception:
                hash_string += ''
            hash_string += '|'
        hash_string += 'LpoLYPU8dV'
        hashh = hashlib.sha512(hash_string.encode()).hexdigest().lower()
        param_dict['hash'] = hashh
    return render_template('payu.html', param=param_dict)


@app.route('/payu/success', methods=['POST', 'GET'])
def payu_success():
    status = request.form["status"]
    firstname = request.form["firstname"]
    amount = request.form["amount"]
    txnid = request.form["txnid"]
    posted_hash = request.form["hash"]
    key = request.form["key"]
    productinfo = request.form["productinfo"]
    email = request.form["email"]
    salt = "LpoLYPU8dV"
    order = Bookings.query.filter(Bookings.payment_id == txnid).first()
    property_selected = Property.query.filter(Property.id == order.property_id).first()
    retHashSeq = salt + '|' + status + '|||||||||||' + email + '|' + firstname + '|' + productinfo + '|' + amount + '|' + txnid + '|' + key
    hashh = hashlib.sha512(retHashSeq.encode()).hexdigest().lower()
    if hashh == posted_hash:
        order.payment_status = 'success'
        db.session.commit()
        pay_status = 1
        send_email_dict_variable = {
            "username": current_user.username,
            "property_name": str(productinfo),
            "no_adults": str(order.no_adults),
            "date": str(order.arrival_data),
            "location": str(property_selected.address),
            "capacity": str(property_selected.capacity),
            "phone": str(property_selected.contact_manager),
            "booking_id": str(order.payment_id)
        }
        print(type(send_email_dict_variable))
        sendMail(usermail=current_user.email, subject='Booking Confirmed', template='booking_confirm',
                 variables=send_email_dict_variable)
    else:
        pay_status = 0
    return render_template('postpayment.html', status=pay_status, transaction_id=txnid)


@app.route('/payu/failed', methods=['POST', 'GET'])
def payu_fail():
    txnid = request.form["txnid"]
    order = Bookings.query.filter(Bookings.payment_id == txnid).first()
    order.payment_status = 'failed'

    db.session.commit()
    pay_status = 0
    return render_template('postpayment.html', status=pay_status, transaction_id=request.form['txnid'])


@app.route('/api/testing', methods=['POST', 'GET'])
def testing():
    list = ['khammam', 'delhi', 'hyderbad', 'india', 'uk']
    return json.dumps(list)


@app.route('/admin/enlistment_status', methods=['POST', 'GET'])
def admin_enlist_status():
    return render_template('admin/enlist_status.html')


@app.route('/admin/property', methods=['POST', 'GET'])
def admin_property():
    return render_template('admin/other_prop.html')
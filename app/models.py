from app import db, login_manager
from flask_login import UserMixin


class User(db.Model, UserMixin):
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(120), unique=True, nullable='False')
    username = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    permission = db.Column(db.String(20), nullable=False, default='user')
    email_confirm = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(60), nullable=True, default='lol_google_login')
    property = db.relationship('Property', backref='owner')
    profile_img = db.Column(db.String(500), nullable=True)
    bookings = db.relationship('Bookings', backref='user_booked')

    def __repr__(self):
        return f"User('{self.unique_id}', '{self.username}', '{self.email}','{self.image_file}','{self.permission}','{self.email_confirm}','{self.password}')"


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner_name = db.Column(db.String(60))
    property_name = db.Column(db.String(60))
    address = db.Column(db.String(120))
    best_price = db.Column(db.Integer())
    pan_number = db.Column(db.Integer())
    partitions = db.Column(db.Integer())
    features = db.Column(db.String(120))
    contact_front = db.Column(db.Integer())
    contact_manager = db.Column(db.Integer())
    capacity = db.Column(db.Integer())
    enlistment_status = db.Column(db.String(20))
    bookees = db.relationship('Bookings', backref='property_owner')

    def __repr__(self):
        return f"Property('{self.id}','{self.owner_id}','{self.property_name}','{self.address}','{self.best_price}'," \
               f"'{self.pan_number}','{self.partitions}','{self.features}') "


class Bookings(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    property_id = db.Column(db.Integer(), db.ForeignKey('property.id'))
    payment_id = db.Column(db.String(60), nullable=False)
    payment_amount = db.Column(db.Integer(), nullable=False)
    payment_status = db.Column(db.String(20))
    date_booking = db.Column(db.DateTime)
    date_for_booking = db.Column(db.DateTime)
    partition_no = db.Column(db.Integer())

    def __repr__(self):
        return f"Bookings('booking_{self.id}','booking_{self.user_id}','{self.property_id}','{self.payment_id}'," \
               f"'{self.payment_amount}','{self.date_for_booking}','{self.date_for_booking}','{self.payment_status}','{self.partition_no}')"

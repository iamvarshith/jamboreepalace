from app import db, login_manager
from flask_login import UserMixin


class User(db.Model, UserMixin):
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    id = db.Column(db.Integer, primary_key=True)

    unique_id = db.Column(db.Integer(), unique=True, nullable=False)
    username = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    permission = db.Column(db.String(20), nullable=False, default='user')
    email_confirm = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(60), nullable=True, default='lol_google_login')

    def __repr__(self):
        return f"User('{self.unique_id}', '{self.username}', '{self.email}','{self.image_file}','{self.permission}','{self.email_confirm}','{self.password}')"


class CourseName(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courseName = db.Column(db.String(40), unique=True, nullable=False)
    courseId = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        return f"CourseName('{self.id}','{self.courseName}','{self.courseId}')"

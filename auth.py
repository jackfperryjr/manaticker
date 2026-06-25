from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

import db


class User(UserMixin):
    def __init__(self, row):
        self.id = str(row["id"])
        self.email = row["email"]


def load_user(user_id):
    row = db.get_user_by_id(int(user_id))
    return User(row) if row else None


def signup(email, password):
    if db.get_user_by_email(email):
        return None
    row = db.create_user(email, generate_password_hash(password))
    return User(row)


def authenticate(email, password):
    row = db.get_user_by_email(email)
    if not row or not check_password_hash(row["password_hash"], password):
        return None
    return User(row)

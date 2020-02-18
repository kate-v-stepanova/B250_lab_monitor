from flask import Blueprint, render_template, request, redirect
from flask_login import login_user, UserMixin, logout_user

from passlib.hash import sha256_crypt

login_page = Blueprint('login_page', __name__)


# creating a custom User class
class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id # id is equal to email
        self.email = email
        self.password = password

    @classmethod
    def get_user(self, email, password):
        from main import get_db
        rdb = get_db()
        encrypted_password = rdb.hget('users', email) or b''
        encrypted_password = encrypted_password.decode('utf-8')
        if encrypted_password == '':
            return None
        if sha256_crypt.verify(password, encrypted_password):
            # for now we use email as an id
            return User(email, email, password)
        return None

    @classmethod
    def get_by_id(self, email):
        # for now get user by email and use email as an id
        from main import get_db
        rdb = get_db()
        password = rdb.hget('users', email) or ''
        if password:
            return User(email, email, password)
        return None

    def get_id(self):
        return self.id


@login_page.route('/login', methods=['GET', 'POST'])
def login():
    error = "Don't have an account? You know whom to contact"
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.get_user(email, password)
        if user is not None:
            login_user(user, remember=True)
            return redirect('/')
        else:
            error = "Incorrect username or password"
    return render_template('login.html',
                           error=error)


@login_page.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/login')


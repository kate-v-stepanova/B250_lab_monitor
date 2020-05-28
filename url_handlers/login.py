from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, UserMixin, logout_user

from passlib.hash import sha256_crypt

login_page = Blueprint('login_page', __name__)


# creating a custom User class
class User(UserMixin):
    def __init__(self, id, email, password, activated=False):
        self.id = id # id is equal to email
        self.email = email
        self.password = password
        self.activated = activated

    @classmethod
    def get_user(self, email, password):
        from main import get_db
        rdb = get_db()
        encrypted_password = rdb.hget('users', email) or b''
        encrypted_password = encrypted_password.decode('utf-8')
        not_activated_users = [user.decode('utf-8') for user in rdb.smembers('not_activated_users')]

        if encrypted_password == '':
            return None
        if sha256_crypt.verify(password, encrypted_password):
            # for now we use email as an id
            return User(email, email, password, activated=email not in not_activated_users)
        return None

    @classmethod
    def get_by_id(self, email):
        # for now get user by email and use email as an id
        from main import get_db
        rdb = get_db()
        password = rdb.hget('users', email) or ''
        not_activated_users = rdb.smembers('not_activated_users')

        if password:
            return User(email, email, password, activated=email not in not_activated_users)
        return None

    def get_id(self):
        return self.id

    def change_password(self, new_password):
        from main import get_db
        rdb = get_db()
        self.password = sha256_crypt.hash(new_password)
        rdb.hmset('users', {self.email: self.password})
        rdb.srem('not_activated_users', self.email)
        self.activated = True


@login_page.route('/login', methods=['GET', 'POST'])
def login():
    error = "Don't have an account? You know whom to contact"
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email, password)
        user = User.get_user(email, password)
        print(user)
        if user is not None:
            login_user(user, remember=True)
            if not user.activated:
                print(user.activated)
                return render_template('user_details.html', error_message='Your account is not activated. To activate your account, please change the password')
            else:
                return redirect('/')
        else:
            error = "Incorrect username or password"
    return render_template('login.html',
                           error=error)


@login_page.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/login')


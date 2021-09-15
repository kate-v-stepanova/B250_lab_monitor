import pandas as pd
from flask import Blueprint, render_template, current_app, make_response, request
from flask_login import login_required, current_user
from passlib.hash import sha256_crypt
import smtplib
import datetime

user_details = Blueprint('user_details', __name__)


@user_details.route('/user_details', methods=['GET', 'POST'])
@login_required
def get_user_details():
    from main import get_db
    rdb = get_db()
    app_admins = rdb.smembers('app_admins')
    app_admins = current_app.config.get('APP_ADMINS') + [admin.decode('utf-8') for admin in app_admins]
    if current_user.email in app_admins:
        users = rdb.hgetall('users')
        users = [] if users is None else users.keys()
        users = [user.decode('utf-8') for user in users]
        return render_template('user_details.html', is_admin=True, users=users)
    return render_template('user_details.html')


@user_details.route('/user_details/create_user', methods=['POST'])
@login_required
def create_user():
    from main import get_db
    rdb = get_db()
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    error_message = ""
    if email is None:
        error_message += "<p>Email is empty</p>"
    if password is None:
        error_message += "<p>Password is empty</p>"
    if error_message:
        return make_response({'status': 'error', 'error': error_message}, 500)
    encrypted_password = sha256_crypt.hash(password)
    user_exists = rdb.hexists('users', email)
    if user_exists:
        error_message += '<p>User <b>{}</b> already exists</p>'.format(email)
    if error_message:
        return make_response({'status': 'error', 'error_message': error_message}, 500)

    rdb.hmset('users', {email: encrypted_password})
    rdb.sadd('not_activated_users', email)

    # # Notify user - shitty yahoo does not allow it
    # from_email = current_app.config.get('YAHOO_EMAIL')
    # to = email
    # subj = 'Your account on b250 web-site has been created'
    # date = datetime.date.today()
    # message_text = 'Your account on b250 web-site has been created by the administrator. \nUsername: {}\nOne-time password:{}\n\
    # Please note, when you login for the first time, you will be asked to change your password!'
    #
    # msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % (from_email, to, subj, date, message_text)
    #
    # username = from_email
    # password = current_app.config.get('YAHOO_PASS')
    #
    # # try:
    # server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
    # # server.ehlo()
    # server.starttls()
    # server.login(username, password)
    # server.sendmail(from_email, to, msg)
    # server.quit()
    # # except Exception as e:
    # #     return make_response({'status': 'error', 'error_message': str(e)}, 500)

    return make_response({'status': 'success'}, 200)


@user_details.route('/user_details/delete_user', methods=['POST'])
@login_required
def delete_user():
    from main import get_db
    rdb = get_db()

    data = request.get_json()
    email = data.get('email')

    rdb.hdel('users', email)
    rdb.srem('not_activated_users', email)
    return make_response({'status': 'success'}, 200)


@user_details.route('/user_details/change_password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    email = data.get('email')
    current_pass = data.get('current_pass')
    new_pass = data.get('new_pass')

    error_message = ""
    if email != current_user.email:
        error_message += "<p>User <b>{}</b> does not have permissions to change password for <b>{}</b></p>".format(
            email, email)

    user = current_user.get_user(email, current_pass)
    if user is None:
        error_message += "<p>Incorrect password</p>"
    if error_message != "":
        return make_response({'status': 'error', 'error_message': error_message}, 500)

    user.change_password(new_pass)
    return make_response({'status': 'success'}, 200)


@user_details.route('/user_details/make_admin', methods=['POST'])
@login_required
def make_admin():
    from main import get_db
    rdb = get_db()
    data = request.get_json()
    email = data.get('email')
    admin = data.get('admin', '')
    if admin == 'admin':
        rdb.sadd('app_admins', email)
    elif admin == 'not_admin':
        rdb.srem('app_admins', email)
    # else: do nothing
    return make_response({'status': 'success'}, 200)



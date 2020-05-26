import pandas as pd
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import current_app

user_details = Blueprint('user_details', __name__)


@user_details.route('/user_details', methods=['GET', 'POST'])
@login_required
def get_user_details():
    from main import get_db
    rdb = get_db()
    app_admins = current_app.config.get('APP_ADMINS')
    if current_user.email in app_admins:
        users = rdb.hgetall('users')
        users = [] if users is None else users.keys()
        users = [user.decode('utf-8') for user in users]
        print(users)
        return render_template('user_details.html', is_admin=True, users=users)
    return render_template('user_details.html')


@user_details.route('/delete_user', methods=['POST'])
def delete_user():
    from main import get_db
    rdb = get_db()



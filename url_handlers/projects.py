import pandas as pd
from flask import Blueprint, render_template
from flask_login import login_required

projects_page = Blueprint('projects', __name__)

@projects_page.route('/')
@login_required
def get_projects():
    from main import get_db
    rdb = get_db()
    projects = rdb.smembers('projects')
    projects = [p.decode('utf-8') for p in projects]
    return render_template('projects.html', projects=projects)

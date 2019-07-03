import pandas as pd
import json
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
    project_info = {}
    for project_id in projects:
        rdb_data = rdb.get("project_info_{}".format(project_id))
        if rdb_data is not None:
            project_info[project_id] = json.loads(rdb_data.decode('utf-8'))
    print(project_info)
    return render_template('projects.html', projects=projects, project_info=project_info)

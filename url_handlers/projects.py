import pandas as pd
import json
from flask import Blueprint, render_template, request, make_response, redirect
from flask_login import login_required

projects_page = Blueprint('projects', __name__)


@projects_page.route('/')
@login_required
def home_page():
    return redirect('/projects')


@projects_page.route('/projects')
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
    return render_template('projects.html', projects=projects, project_info=project_info)


@projects_page.route('/projects/search',  methods=['POST'])
@login_required
def search_projects():
    from main import get_db
    to_search = request.get_data()
    if to_search is None:
        return make_response({'status': 'error', 'error': 'No input received'})
    to_search = to_search.decode('utf-8').lower()

    rdb = get_db()
    projects_ids = rdb.smembers('projects')
    projects_ids = [proj.decode('utf-8') for proj in projects_ids]
    found = list(filter(lambda x:to_search in x.lower(), projects_ids))

    return make_response({'status': 'success', 'matching_projects': found}, 200)

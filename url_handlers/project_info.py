import pandas as pd
from flask import Blueprint, render_template, request
from flask_login import login_required
import json

project_page = Blueprint('project_page', __name__)

@project_page.route('/project_info/<project_id>', methods=['GET', 'POST'])
@login_required
def get_project_info(project_id):
    from main import get_db
    rdb = get_db()
    if request.method == "GET":
        rdb_data = rdb.get("project_info_{}".format(project_id))
        if rdb_data is not None:
            project_info = json.loads(rdb_data)
            rdb_data = rdb.get("samples_info_{}".format(project_id))
            if rdb_data is not None:
                samples_df = pd.read_msgpack(rdb_data)
                return render_template("project_info.html", project_id=project_id, project_info=project_info,
                                       samples=samples_df.to_dict())
            return render_template("project_info.html", project_id=project_id, project_info=project_info)

    else: # if request.method == "POST":
        rdb_data = rdb.get('project_info_{}'.format(project_id))
        if rdb_data is None:
            project_info = {'project_id': project_id}
        else:
            project_info = json.loads(rdb_data.decode('utf-8'))

        for key in request.form.keys():
            project_info[key] = request.form.get(key)
        rdb.set('project_info_{}'.format(project_id), json.dumps(project_info))
        return json.dumps(project_info)

    return render_template("project_info.html", project_id=project_id)
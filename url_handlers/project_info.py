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
        project_info = {}
        if rdb_data is not None:
            project_info = json.loads(rdb_data.decode('utf-8'))
        samples_info = {}
        rdb_data = rdb.get("sample_info_{}".format(project_id))
        if rdb_data is not None:
            samples_info = json.loads(rdb_data.decode('utf-8'))

        available_stats = []
        bc_split_stats = rdb.get('bc_split_{}'.format(project_id))
        if bc_split_stats is not None:
            available_stats.append('bc_split_stats')
        cutadapt_stats = rdb.get('cutadapt_stats_{}'.format(project_id))
        if cutadapt_stats is not None:
            available_stats.append('cutadapt_stats')
        diricore_stats = rdb.get('diricore_stats_{}'.format(project_id))
        if diricore_stats is not None:
            available_stats.append('diricore_stats')

        return render_template("project_info.html", project_id=project_id, project_info=project_info,
                                   samples=samples_info, available_stats=available_stats)

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



@project_page.route("/bc_split_stats/<project_id>", methods=["POST"])
def get_bc_stats(project_id):
    from main import get_db
    rdb = get_db()
    data = rdb.get('bc_split_{}'.format(project_id))
    if data is not None:
        df = pd.read_msgpack(data)
        df = df[['Barcode', 'Count']][:-1]
        series = []
        for i, row in df.iterrows():
            series.append({
                'name': row['Barcode'],
                'data': [row['Count']]
            })
        return json.dumps(series)

    return ""

@project_page.route("/cutadapt_stats/<project_id>", methods=["POST"])
def get_cutadapt_stats(project_id):
    from main import get_db
    rdb = get_db()
    data = rdb.get('cutadapt_stats_{}'.format(project_id))
    if data is not None:
        data = json.loads(data.decode('utf-8'))
        data = data[1]
        series = [
            {'name': 'No adapter', 'data': [data['total'] - data['with_adapter']], 'color': '#ff6666'},
            {'name': 'Passed', 'data': [data['passed']], 'color': '#53c68c'},
            {'name': 'Too short', 'data': [data['too_short']], 'color': '#ff9966'}
        ]
        return json.dumps(series)
    return ""

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
        transcript_regions = rdb.get('transcript_regions_{}'.format(project_id))
        if transcript_regions is not None:
            available_stats.append('transcript_regions')

        ucsc_link = rdb.get('ucsc_link_{}'.format(project_id))
        ucsc_link = ucsc_link.decode('utf-8') if ucsc_link else None

        analysis_list = []
        periodicity = rdb.get('{}_periodicity_heatmap'.format(project_id))
        if periodicity:
            analysis_list.append({
                'name': 'Periodicity',
                'link': "{}/periodicity/{}".format(request.base_url, project_id)
            })
            analysis_list.append({
                'name': 'Periodicity Heatmap',
                'link': "{}/periodicity_heatmap/{}".format(request.base_url, project_id)
            })

        reads_per_position = rdb.get("{}_reads_per_position".format(project_id))
        if reads_per_position:
            analysis_list.append({
                'name': 'Reads per position',
                'link': "{}/reads_per_position/{}".format(request.base_url, project_id)
            })

        ma_plot = rdb.smembers("contrasts_{}".format(project_id))
        if ma_plot:
            analysis_list.append({
                'name': "MA plot",
                'link': "{}/ma_plot/{}".format(request.base_url, project_id)
            })

        return render_template("project_info.html", project_id=project_id, project_info=project_info,
                                   samples=samples_info, available_stats=available_stats, ucsc_link=ucsc_link,
                               analysis_list=analysis_list)

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
        samples = sorted(list(df['Barcode'].unique()))
        result = {
            'samples': samples
        }
        series = []
        for i, row in df.iterrows():
            series.append({
                'name': row['Barcode'],
                'data': [row['Count']]
            })
        result['series'] = series
        return json.dumps(result)

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


@project_page.route("/transcript_regions/<project_id>", methods=["POST"])
def get_transcript_regions(project_id):
    from main import get_db
    rdb = get_db()
    data = rdb.get('transcript_regions_{}'.format(project_id))
    if data is not None:
        data = json.loads(data.decode('utf-8'))
        full_df = pd.DataFrame(data)
        samples = sorted(list(full_df['sample'].unique()))
        result = {
            'samples': samples,
        }

        series = []
        regions = ["5' UTR", "Start", "CDS", "3' UTR"]
        for region in regions:
            data = []
            for sample in samples:
                # should be just one value
                df = full_df.loc[(full_df['sample'] == sample) & (full_df['region'] == region)]
                data.append({
                    'y': df['reads'].tolist()[0],
                    'sample': sample,
                    'region': region
                })
            series.append({
                'name': region,
                'data': data
            })
        result['series'] = series
        return json.dumps(result)

    return ""

@project_page.route("/diricore_stats/<project_id>", methods=["POST"])
def get_diricore_stats(project_id):
    from main import get_db
    rdb = get_db()
    data = rdb.get('diricore_stats_{}'.format(project_id))
    if data is not None:
        data = json.loads(data.decode('utf-8'))
        full_df = pd.DataFrame(data)
        samples = sorted(list(full_df['sample'].unique()))
        result = {
            'samples': samples,
        }
        stats = ["rRNA_reads", "tRNA_reads", "No_HQ", "HQ_with_duplicates", "Unique_HQ"]
        series = []
        for stat in stats:
            data = []
            for sample in samples:
                df = full_df.loc[full_df['sample'] == sample]
                data.append({
                    'sample': sample,
                    'y': df.get(stat, [0]).tolist()[0],
                    'stat': stat,
                    'initial_reads': df['Initial_reads'].tolist()[0],
                })
            series.append({
                'name': stat,
                'data': data,
            })

        result['series'] = series
        return json.dumps(result)

    return ""

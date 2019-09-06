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

        # BASIC STATS
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
        rrna_genes = rdb.get('rrna_genes_{}'.format(project_id))
        if rrna_genes is not None:
            available_stats.append('rrna_genes')

        snoRNAs = rdb.get('{}_snoRNAs'.format(project_id))
        if snoRNAs is not None:
            available_stats.append('snoRNAs')

        ucsc_links = []
        try:
            ucsc_link = rdb.get('ucsc_link_{}'.format(project_id))
            ucsc_link = ucsc_link.decode('utf-8') if ucsc_link else None
            if ucsc_link:
                ucsc_links = [ucsc_link]
        except:
            ucsc_links = rdb.smembers('ucsc_link_{}'.format(project_id))
            if ucsc_links:
                ucsc_links = [ucsc.decode('utf-8') for ucsc in ucsc_links]

        # OTHER ANALYSIS
        analysis_list = []
        periodicity = rdb.get('{}_periodicity_heatmap'.format(project_id))
        if periodicity:
            analysis_list.append({
                'name': 'Periodicity',
                'link': "{}periodicity/{}".format(request.url_root, project_id)
            })
            analysis_list.append({
                'name': 'Periodicity Heatmap',
                'link': "{}periodicity_heatmap/{}".format(request.url_root, project_id)
            })

        reads_per_position = rdb.get("{}_reads_per_position".format(project_id))
        if reads_per_position:
            analysis_list.append({
                'name': 'Reads per position',
                'link': "{}reads_per_position/{}".format(request.url_root, project_id)
            })

        ma_plot = rdb.smembers("contrasts_{}".format(project_id))
        if ma_plot:
            analysis_list.append({
                'name': "MA plot",
                'link': "{}ma_plot/{}".format(request.url_root, project_id)
            })
        heatmap = rdb.exists("cpm_coding_{}".format(project_id))
        if heatmap:
            analysis_list.append({
                'name': "Heatmap",
                'link': "{}heatmap/{}".format(request.url_root, project_id)
            })
        translational_efficiency = rdb.exists("{}_rpkm_rna".format(project_id))
        if translational_efficiency:
            analysis_list.append({
                'name': "Translational Efficiency",
                'link': "{}translational_efficiency/{}".format(request.url_root, project_id)
            })

        analysis_info = rdb.get('{}_analysis_info'.format(project_id))
        if analysis_info is not None:
            analysis_info = analysis_info.decode('utf-8')

        return render_template("project_info.html", project_id=project_id, project_info=project_info,
                                samples=samples_info, available_stats=available_stats, ucsc_links=ucsc_links,
                               analysis_list=analysis_list, analysis_info=analysis_info)

    else:  # if request.method == "POST":
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
        total = int(df["Count"].sum())
        samples = sorted(list(df['Barcode'].unique()))
        result = {
            'samples': samples
        }
        series = []
        for i, row in df.iterrows():
            series.append({
                'name': row['Barcode'],
                'data': [row['Count']],
                'total': total
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
        full_df = full_df.fillna(0)
        samples = sorted(list(full_df['sample'].unique()))
        result = {
            'samples': samples,
        }
        stats = ["rrna", "trna", "lq_with_dup", "lq_unique", "hq_with_dup", "hq_unique"]
        series = []
        for stat in stats:
            data = []
            for sample in samples:
                df = full_df.loc[full_df['sample'] == sample]
                data.append({
                    'sample': sample,
                    'y': df.get(stat, [0]).tolist()[0],
                    'stat': stat,
                    'initial_reads': df['bc_split'].tolist()[0],
                })
            series.append({
                'name': stat,
                'data': data,
            })

        result['series'] = series
        return json.dumps(result)

    return ""


@project_page.route("/rrna_genes/<project_id>", methods=["POST"])
def get_rrna_genes(project_id):
    from main import get_db
    rdb = get_db()
    data = rdb.get("rrna_genes_{}".format(project_id))
    if data is not None:
        df = pd.read_msgpack(data)
        genes = list(df["gene_name"].unique())
        samples = sorted(list(df["sample"].unique()))
        series = []
        for gene in genes:
            data = []
            for sample in samples:
                df1 = df.loc[df['sample'] == sample]
                if len(df1.loc[df1["gene_name"] == gene]) == 0:
                    y = 0
                else:
                    y = df1.loc[df1["gene_name"] == gene]["gene_counts"].tolist()[0]
                data.append({
                    'sample': sample,
                    'y': y,
                    'gene': gene,
                })
            series.append({
                'name': gene,
                'data': data
            })

        result = {
            'samples': samples,
            'series': series
        }
        return json.dumps(result)
    return ""


@project_page.route("/snoRNAs/<project_id>", methods=["POST"])
def get_sno_rnas(project_id):
    from main import get_db
    rdb = get_db()
    data = rdb.get('{}_snoRNAs'.format(project_id))
    if data is not None:
        df = pd.read_msgpack(data)
        series = []
        samples = sorted(list(df['sample']))
        rna_types = list(df.columns)
        rna_types.remove('sample')
        for rna in rna_types:
            data = []
            for sample in samples:
                row = df.loc[df['sample'] == sample]
                data.append({
                    'sample': sample,
                    'y': row.get(rna, [0]).tolist()[0],
                    'group': rna,
                })
            series.append({
                'name': rna,
                'data': data
            })

        result = {
            'samples': samples,
            'series': series
        }
        return json.dumps(result)
    return ""

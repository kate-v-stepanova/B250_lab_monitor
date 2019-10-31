import pandas as pd
import numpy as np
from flask import Blueprint, render_template, request
from flask_login import login_required
import json

alignments = Blueprint('alignments', __name__)


@alignments.route('/alignments/<project_id>', methods=['GET', 'POST'])
@login_required
def get_alignments(project_id):
    from main import get_db
    rdb = get_db()

    list_of_samples = []
    rdb_data = rdb.get("sample_info_{}".format(project_id))
    if rdb_data is None:
        return render_template("alignments.html", error="No data found")

    samples_info = json.loads(rdb_data.decode('utf-8'))
    for sample in samples_info:
        list_of_samples.append(sample.get('sample'))

    bam_types = rdb.smembers('bam_types_{}'.format(project_id))

    trans = rdb.get('transcriptLength.txt')
    if not trans:
        return render_template("alignments.html", samples=list_of_samples, bam_types=bam_types, error="transcriptLength.txt not found!!")

    # import pdb; pdb.set_trace()
    list_of_genes = rdb.smembers('genes_{}'.format(project_id))
    if request.method == "GET":
        return render_template("alignments.html", samples=list_of_samples, bam_types=bam_types, genes=list_of_genes)

    selected_gene = request.form.get('gene')
    selected_samples = request.form.getlist('selected_samples')
    bam_type = request.form.get('bam_type')
    if bam_type is None:
        bam_type = 'hq_unique'

    trans = pd.read_msgpack(trans)
    trans = trans.loc[trans['gene_name'] == selected_gene]

    series = []
    error = ""
    for sample in selected_samples:
        rdb_data = rdb.get('alignment__{}__{}__{}'.format(project_id, bam_type, sample))
        if rdb_data is None:
            error += "No data found for sample {} ({})___".format(sample, bam_type)
            continue

        df = pd.read_msgpack(rdb_data)
        df = pd.merge(df, trans, on="transcript", how="inner")

        if len(df) == 0:
            error += "No reads in selected gene for sample {}___".format(sample)
            continue

        df = df.loc[df['start'] > df['5utr_len']]
        if len(df) == 0:
            error += "No reads in CDS for sample {}___".format(sample)

        df['dup'] = 1
        df['dup'] = df.groupby(['seq'])['dup'].transform('sum')
        df['start'] = df['start'] - df['5utr_len']
        df1 = pd.DataFrame()
        df1['pos'] = [i for i in range(1, trans['cds_len'].iloc[0] + 1)]
        df1['counts'] = 0
        for i, row in df.iterrows():
            pos = [i for i in range(row['start'], row['start'] + len(row['seq']) + 1)]
            df1.loc[df1['pos'].isin(pos), 'counts'] = df1.loc[df1['pos'].isin(pos), 'counts'] + row['dup']
        df1.columns = ['x', 'y']
        series.append({'name': sample, 'data': df1.to_dict('records'), 'turboThreshold': len(df1)})
    if error:
        return render_template("alignments.html", samples=list_of_samples, bam_types=bam_types,
                               selected_gene=selected_gene, bam_type=bam_type, selected_samples=selected_samples,
                               error=error, genes=list_of_genes)
    return render_template("alignments.html", samples=list_of_samples, bam_types=bam_types, selected_gene=selected_gene,
                           bam_type=bam_type, selected_samples=selected_samples, series=series, genes=list_of_genes)



import pandas as pd
import numpy as np
from flask import Blueprint, render_template, request
from flask_login import login_required
import json

translational_efficiency = Blueprint('translational_efficiency', __name__)


@translational_efficiency.route('/translational_efficiency/<project_id>', methods=['GET', 'POST'])
@login_required
def get_translational_efficiency(project_id):
    from main import get_db
    rdb = get_db()
    rp = rdb.get("{}_rpkm_rp".format(project_id))
    rna = rdb.get("{}_rpkm_rna".format(project_id))
    list_of_samples = []
    if rp is None or rna is None:
        return render_template("translational_efficiency.html", samples=list_of_samples,
                               error="No data for project: {}".format(project_id))
    rp_df = pd.read_msgpack(rp)
    rna_df = pd.read_msgpack(rna)
    samples = list(rp_df.columns)
    samples.remove('gene_name')
    list_of_samples = samples
    if request.method == "GET":
        return render_template("translational_efficiency.html", samples=list_of_samples)

    selected_samples = request.form.getlist('selected_samples')
    if not selected_samples:
        return render_template("translational_efficiency.html", samples=list_of_samples, error="No samples selected")

    apply_filter = request.form.get('apply_filter') == "True"
    min_y = request.form.get('min_y', -100)
    max_y = request.form.get('max_y', 100)
    min_y = int(min_y)
    max_y = int(max_y)
    plot_series = []
    for sample in selected_samples:
        gene_names = rp_df['gene_name'].tolist()
        rp = rp_df[sample].astype(float).tolist()
        rna = rna_df[sample].astype(float).tolist()
        df = pd.DataFrame(columns=['gene_name', 'x', 'y'])
        df['gene_name'] = gene_names
        df['rpkm_rna'] = rna
        df['rpkm_rp'] = rp
        df['log2(rp)'] = np.log2(df['rpkm_rp'])
        df['log2(rna)'] = np.log2(df['rpkm_rna'])
        df['x'] = df['log2(rna)']
        df['y'] = df['log2(rna)'] / df['log2(rp)']

        if apply_filter:
            df = df.loc[df['y'] >= min_y]
            df = df.loc[df['y'] <= max_y]
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna()
        series = {
            'name': sample,
            'data': df.to_dict('records')
        }
        plot_series.append(series)
    return render_template("translational_efficiency.html", samples=list_of_samples, selected_samples=selected_samples,
                           apply_filter=apply_filter, min_y=min_y, max_y=max_y, plot_series=plot_series)

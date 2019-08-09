import pandas as pd
from flask import Blueprint, render_template, request
from flask_login import login_required
import json

from utils.inchlib_clust import Cluster, Dendrogram

heatmap = Blueprint('heatmap', __name__)


@heatmap.route('/heatmap/<project_id>', methods=['GET', 'POST'])
@login_required
def get_heatmap(project_id):
    from main import get_db
    rdb = get_db()
    exists = rdb.exists('cpm_coding_{}'.format(project_id))
    if not exists:
        return render_template("heatmap.html", no_data=True, error="No data for the project {}".format(project_id))

    data = rdb.get('cpm_coding_{}'.format(project_id))
    df = pd.read_msgpack(data)
    samples = sorted(list(df.columns))
    samples.remove('gene_name')

    if request.method == "GET":
        return render_template("heatmap.html", samples=samples, selected_samples=samples)

    selected_samples = request.form.getlist('selected_samples')
    if not selected_samples:
        return render_template("heatmap.html", samples=samples, error="No samples selected")

    filter_by = request.form.get('filter_by')
    number_of_genes = int(request.form.get('number_of_genes'))
    list_of_genes = request.form.get('list_of_genes', '').split()

    if filter_by == "top_coding" or filter_by == "list_of_genes":
        data = rdb.get('cpm_coding_{}'.format(project_id))
        df = pd.read_msgpack(data)

    elif filter_by == "top_non_coding":
        data = rdb.get('cpm_non_coding_{}'.format(project_id))
        df = pd.read_msgpack(data)

    if filter_by == "top_coding" or filter_by == "top_non_coding":
        df = df[:number_of_genes]

    elif filter_by == "list_of_genes":
        df1 = None
        # should be ok for ~100-200 genes
        for gene in list_of_genes:
            row = df.loc[df['gene_name'] == gene]
            df1 = row if df1 is None else df1.append(row, ignore_index=True)
        df = df1

    df = df[['gene_name'] + selected_samples]
    for sample in selected_samples:
        df[sample] = df[sample].round(2)

    df.loc[-1] = ['gene_name'] + selected_samples
    df.index = df.index + 1
    df.sort_index(inplace=True)

    cluster = Cluster()
    cluster.read_data(rows=df.values.tolist(), header=True)
    cluster.cluster_data()
    dendrogram = Dendrogram(cluster)
    plot_data = dendrogram.create_cluster_heatmap()
    plot_data = json.dumps(plot_data)

    csv_data = df.to_csv(sep=",", header=False, index=False)
    return render_template("heatmap.html", samples=samples, selected_samples=selected_samples,
                           number_of_genes=number_of_genes, filter_by=filter_by, list_of_genes=list_of_genes,
                           plot_data=plot_data, csv_data=csv_data)
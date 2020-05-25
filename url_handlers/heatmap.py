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
        return render_template("heatmap.html", samples=samples, first_group=[], second_group=[])

    first_group = request.form.getlist('first_group')
    if not first_group:
        return render_template("heatmap.html", samples=samples, error="No samples selected")

    second_group = request.form.getlist('second_group')

    filter1 = request.form.get('filter1')
    filter2 = request.form.get('filter2')

    number_of_genes1 = int(request.form.get('number_of_genes1'))
    number_of_genes2 = int(request.form.get('number_of_genes2'))

    list_of_genes = request.form.get('list_of_genes', '').split()
    include_non_coding = request.form.get('include_non_coding', "") == "True"

    if include_non_coding:
        data = rdb.get('cpm_non_coding_{}'.format(project_id))
        df = pd.read_msgpack(data)
    else:
        data = rdb.get('cpm_coding_{}'.format(project_id))
        df = pd.read_msgpack(data)

    if filter1 == 'list_of_genes':
        df1 = None
        for gene in list_of_genes:
            row = df.loc[df['gene_name'] == gene]
            df1 = row if df1 is None else df1.append(row, ignore_index=True)

            # input for clustering: header + df
            data = [['gene_name'] + first_group] + df1.values.tolist()

            cluster = Cluster()
            cluster.read_data(rows=data, header=True)
            cluster.cluster_data()
            dendrogram = Dendrogram(cluster)
            plot_data = dendrogram.create_cluster_heatmap()
            plot_data = json.dumps(plot_data)

            csv_data = df1.to_csv(sep=",", header=True, index=False)
            return render_template("heatmap.html", plot_data=plot_data, first_group=first_group, samples=samples,
                                   list_of_genes=list_of_genes, number_of_genes1=number_of_genes1, filter1=filter1,
                                   number_of_genes2=number_of_genes2, include_non_coding=include_non_coding,
                                   csv_data=csv_data, filter2=filter2)

    # select samples
    df1 = df[['gene_name'] + first_group]

    # round to 2 decimals
    for sample in first_group:
        df1[sample] = df1[sample].round(2)

    # sort by variance
    if filter1 == 'least':
        df1 = df1.reindex(df1.var(axis=1).sort_values(ascending=True).index)  # 1 2 3
    else:
        df1 = df1.reindex(df1.var(axis=1).sort_values(ascending=False).index)  # 3 2 1

    # select top genes (or all if number_of_genes is 0)
    if number_of_genes1 != 0:
        df1 = df1[:number_of_genes1]

    if not second_group:
        # input for clustering: header + df
        data = [['gene_name'] + first_group] + df1.values.tolist()

        cluster = Cluster()
        cluster.read_data(rows=data, header=True)
        cluster.cluster_data()
        dendrogram = Dendrogram(cluster)
        plot_data = dendrogram.create_cluster_heatmap()
        plot_data = json.dumps(plot_data)
        csv_data = df1.to_csv(sep=",", header=True, index=False)

        return render_template("heatmap.html", plot_data=plot_data, first_group=first_group, samples=samples,
                   list_of_genes=list_of_genes, number_of_genes1=number_of_genes1, include_non_coding=include_non_coding,
                   filter1=filter1, number_of_genes2=number_of_genes2, csv_data=csv_data, filter2=filter2)

    # if second group
    df2 = df[['gene_name'] + first_group + second_group]

    # pairwise comparisons
    df22 = None
    for sample1 in first_group:
        for sample2 in second_group:
            df2_var = df[[sample1, sample2]].var(axis=1)
            df22 = df2_var if df22 is None else df22 + df2_var
    # average variance
    df22 = df22 / len(second_group)
    # sort by variance
    ascending = filter2 == 'least'
    df22 = df2.reindex(df22.sort_values(ascending=ascending).index)  # 3 2 1

    if number_of_genes2 != 0:
        df22 = df22[:number_of_genes2]

    # not changing genes
    common_genes = list(set(df22['gene_name'].tolist()) & set(df1['gene_name'].tolist()))

    all_genes = set(df22['gene_name'].tolist() + df1['gene_name'].tolist())
    common_genes = set(set(df22['gene_name'].tolist()) & set(df1['gene_name'].tolist()))
    our_genes = set(df1['gene_name'].tolist()) - common_genes

    if len(our_genes) == 0:
        error = "No common genes found between 2 groups. Try to increase the number of genes"
        return render_template("heatmap.html", first_group=first_group, second_group=second_group, samples=samples,
               list_of_genes=list_of_genes, number_of_genes1=number_of_genes1, include_non_coding=include_non_coding,
               filter1=filter1, number_of_genes2=number_of_genes2, filter2=filter2, error=error)

    final_df = df2.loc[df2['gene_name'].isin(our_genes)]
    for sample in first_group + second_group:
        final_df[sample] = final_df[sample].round(2)

    # input for clustering: header + df
    data = [['gene_name'] + first_group + second_group] + final_df.values.tolist()

    cluster = Cluster()
    cluster.read_data(rows=data, header=True)
    cluster.cluster_data()
    dendrogram = Dendrogram(cluster)
    plot_data = dendrogram.create_cluster_heatmap()
    plot_data = json.dumps(plot_data)
    csv_data = final_df.to_csv(sep=",", header=True, index=False)

    return render_template("heatmap.html", samples=samples, first_group=first_group, second_group=second_group,
                           number_of_genes1=number_of_genes1, number_of_genes2=number_of_genes2, filter1=filter1,
                           filter2=filter2, list_of_genes=list_of_genes, include_non_coding=include_non_coding,
                           plot_data=plot_data, csv_data=csv_data, common_genes=len(final_df))

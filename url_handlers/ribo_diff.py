import pandas as pd
import numpy as np
from flask import Blueprint, render_template, request
from flask_login import login_required
import json

ribo_diff = Blueprint('ribo_diff', __name__)


@ribo_diff.route('/ribo_diff/<project_id>', methods=['GET', 'POST'])
@login_required
def get_ribo_diff(project_id):
    from main import get_db
    rdb = get_db()

    list_of_samples = []
    rdb_data = rdb.get("sample_info_{}".format(project_id))
    if rdb_data is None:
        return render_template("ribodiff.html", error="No data found")

    samples_info = json.loads(rdb_data.decode('utf-8'))
    for sample in samples_info:
        list_of_samples.append(sample.get('sample'))

    if request.method == "GET":
        return render_template("ribodiff.html", samples=list_of_samples)

    coding_genes = request.form.get('coding_genes') == "True"
    ctrl_sample = request.form.get('ctrl_sample')
    treated_sample = request.form.get('treated_sample')
    contrast = "{}_vs_{}".format(treated_sample, ctrl_sample)
    rr = rdb.get('te_{}_{}'.format(project_id, contrast))

    if not rr:
        return render_template("ribodiff.html", samples=list_of_samples, ctrl_sample=ctrl_sample,
                               treated_sample=treated_sample, error="No data for contrast {}".format(contrast),
                               coding_genes=coding_genes)
    df = pd.read_msgpack(rr)
    df = df.dropna()
    df = df.loc[~df['gene_id'].str.startswith("MT-")]
    df = df.loc[~df['gene_id'].str.startswith("HIST")]

    if coding_genes:
        df = df.loc[~df['gene_id'].str.startswith("ENSG")]

    df['log2_RNA'] = np.log2(df['cntRnaMean'].astype(float))
    df['log2_RP'] = np.log2(df['cntRiboMean'].astype(float))
    df['x'] = df['log2_RNA']
    df['y'] = df['logFoldChangeTE']

    sig_df = df.loc[df['padj'] <= 0.05]

    nonsig_df = df.loc[df['padj'] > 0.05]

    plot_series = [{'name': "All genes: {}".format(len(df)), 'data': nonsig_df.to_dict('records')},
                   {'name': "Significant genes (pval >= 0.05): {}".format(len(sig_df)), 'data': sig_df.to_dict('records')}]

    return render_template("ribodiff.html", samples=list_of_samples, ctrl_sample=ctrl_sample,
                           treated_sample=treated_sample, coding_genes=coding_genes, plot_series=plot_series)

    # rp = rdb.get("{}_rpkm_rp".format(project_id))
    # rna = rdb.get("{}_rpkm_rna".format(project_id))
    # list_of_samples = []
    # if rp is None or rna is None:
    #     return render_template("translational_efficiency.html", samples=list_of_samples,
    #                            error="No data for project: {}".format(project_id))
    # rp_df = pd.read_msgpack(rp)
    # rna_df = pd.read_msgpack(rna)
    # samples = list(rp_df.columns)
    # samples.remove('gene_name')
    # list_of_samples = samples
    # if request.method == "GET":
    #     return render_template("translational_efficiency.html", samples=list_of_samples)
    #
    # selected_samples = request.form.getlist('selected_samples')
    # if not selected_samples:
    #     return render_template("translational_efficiency.html", samples=list_of_samples, error="No samples selected")
    #
    # apply_filter = request.form.get('apply_filter') == "True"
    # min_y = request.form.get('min_y', -100)
    # max_y = request.form.get('max_y', 100)
    # min_y = int(min_y)
    # max_y = int(max_y)
    # plot_series = []
    # for sample in selected_samples:
    #     gene_names = rp_df['gene_name'].tolist()
    #     rp = rp_df[sample].astype(float).tolist()
    #     rna = rna_df[sample].astype(float).tolist()
    #     df = pd.DataFrame(columns=['gene_name', 'x', 'y'])
    #     df['gene_name'] = gene_names
    #     df['rpkm_rna'] = rna
    #     df['rpkm_rp'] = rp
    #     df['log2(rp)'] = np.log2(df['rpkm_rp'])
    #     df['log2(rna)'] = np.log2(df['rpkm_rna'])
    #     df['x'] = df['log2(rna)']
    #     df['y'] = df['log2(rna)'] / df['log2(rp)']
    #
    #     if apply_filter:
    #         df = df.loc[df['y'] >= min_y]
    #         df = df.loc[df['y'] <= max_y]
    #     df = df.replace([np.inf, -np.inf], np.nan)
    #     df = df.dropna()
    #     series = {
    #         'name': sample,
    #         'data': df.to_dict('records')
    #     }
    #     plot_series.append(series)
    # return render_template("translational_efficiency.html", samples=list_of_samples, selected_samples=selected_samples,
    #                        apply_filter=apply_filter, min_y=min_y, max_y=max_y, plot_series=plot_series)

#
#
# @translational_efficiency.route('/translational_efficiency/<project_id>', methods=['GET', 'POST'])
# @login_required
# def get_translational_efficiency(project_id):
#     from main import get_db
#     rdb = get_db()
#     rp = rdb.get("{}_rpkm_rp".format(project_id))
#     rna = rdb.get("{}_rpkm_rna".format(project_id))
#     list_of_samples = []
#     if rp is None or rna is None:
#         return render_template("translational_efficiency.html", samples=list_of_samples,
#                                error="No data for project: {}".format(project_id))
#     rp_df = pd.read_msgpack(rp)
#     rna_df = pd.read_msgpack(rna)
#     samples = list(rp_df.columns)
#     samples.remove('gene_name')
#     list_of_samples = samples
#     if request.method == "GET":
#         return render_template("translational_efficiency.html", samples=list_of_samples)
#
#     selected_samples = request.form.getlist('selected_samples')
#     if not selected_samples:
#         return render_template("translational_efficiency.html", samples=list_of_samples, error="No samples selected")
#
#     apply_filter = request.form.get('apply_filter') == "True"
#     min_y = request.form.get('min_y', -100)
#     max_y = request.form.get('max_y', 100)
#     min_y = int(min_y)
#     max_y = int(max_y)
#     plot_series = []
#     for sample in selected_samples:
#         gene_names = rp_df['gene_name'].tolist()
#         rp = rp_df[sample].astype(float).tolist()
#         rna = rna_df[sample].astype(float).tolist()
#         df = pd.DataFrame(columns=['gene_name', 'x', 'y'])
#         df['gene_name'] = gene_names
#         df['rpkm_rna'] = rna
#         df['rpkm_rp'] = rp
#         df['log2(rp)'] = np.log2(df['rpkm_rp'])
#         df['log2(rna)'] = np.log2(df['rpkm_rna'])
#         df['x'] = df['log2(rna)']
#         df['y'] = df['log2(rna)'] / df['log2(rp)']
#
#         if apply_filter:
#             df = df.loc[df['y'] >= min_y]
#             df = df.loc[df['y'] <= max_y]
#         df = df.replace([np.inf, -np.inf], np.nan)
#         df = df.dropna()
#         series = {
#             'name': sample,
#             'data': df.to_dict('records')
#         }
#         plot_series.append(series)
#     return render_template("translational_efficiency.html", samples=list_of_samples, selected_samples=selected_samples,
#                            apply_filter=apply_filter, min_y=min_y, max_y=max_y, plot_series=plot_series)

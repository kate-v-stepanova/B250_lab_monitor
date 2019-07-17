import pandas as pd
from flask import Blueprint, render_template, request
from flask_login import login_required

fc_heatmap = Blueprint('fc_heatmap', __name__)


@fc_heatmap.route('/fc_heatmap/<project_id>', methods=['GET', 'POST'])
@login_required
def get_fc_heatmap(project_id):
    from main import get_db
    rdb = get_db()
    exists = rdb.exists('fc_coding_{}'.format(project_id))
    if not exists:
        return render_template("fc_heatmap.html", no_data=True, error="No data for the project {}".format(project_id))

    filter_by = request.form.get('filter_by', "top_50_coding")

    df = rdb.get('fc_coding_{}'.format(project_id))
    df = pd.read_msgpack(df)
    df = df.dropna()

    df = df[:50]
    x_categories = sorted(list(df.columns))
    x_categories.remove('gene_name')
    y_categories = sorted(list(df['gene_name']))

    df_hm = None
    for contrast in x_categories:
        df1 = df[[contrast, "gene_name"]]
        df1["contrast"] = contrast
        df1 = df1.rename({contrast: "value", "gene_name": "y", "contrast": "x"}, axis="columns")
        df1 = df1[["x", "y", "value"]]
        if df_hm is None:
            df_hm = df1
        else:
            df_hm = df_hm.append(df1, ignore_index=True)

    df_hm = df_hm.sort_values(['x', 'y'])
    z = []
    for gene in y_categories:
        df = df_hm.loc[df_hm["y"] == gene]
        z.append(list(df["value"]))
    z_max = df_hm['value'].max()
    z_min = df_hm['value'].min()
    z_max = max(abs(z_max), abs(z_min))

    return render_template("fc_heatmap.html", x_categories=x_categories, y_categories=y_categories, z=z, z_max=z_max)


    # if method == "K-means":
    #     df = pd.read_msgpack(rdb.get('fc_{}'.format(project_id)))
    #
    #     # # TODO: cluster
    #     gene_names = df['gene_name']
    #     print(df)
    #     df = df.drop("gene_name", axis=1)
    #     kmeans = KMeans(n_clusters=5, random_state=0).fit(df)
    #     labels = kmeans.labels_
    #     print(labels)
    #     df['cluster'] = labels
    #     df['gene_name'] = gene_names
    #     df = df.sort_values(by=['cluster'])
    #     shapes = ["circle", "square", "diamond", "triangle", "triangle-down"]
    #     colors = ['#b3e6ff', '#ffe6b3', '#ccffb3', '#ffb3b3', '#d699ff', 'black', 'grey']
    #     plot_series = []
    #     for cluster in set(labels):
    #         c_df = df.loc[df['cluster' == cluster]]
    #         plot_series.append({
    #             'name': "Cluster {}".format(cluster),
    #             'length': len(c_df),
    #             'data': c_df.to_dict(c_df)
    #         })


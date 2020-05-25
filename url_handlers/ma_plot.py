import pandas as pd
from flask import Blueprint, render_template, request
from flask_login import login_required

ma_plot = Blueprint('ma_plot', __name__)

@ma_plot.route('/ma_plot/<project_id>', methods=['GET', 'POST'])
@login_required
def get_ma_plot(project_id):
    from main import get_db
    rdb = get_db()
    contrasts = rdb.smembers("contrasts_{}".format(project_id))
    contrasts = sorted([c.decode('utf-8') for c in contrasts])

    if request.method == "GET":
        no_data = len(contrasts) == 0 # if no contrasts, no_data will be True
        #
        # df = pd.read_msgpack(bi_df)
        return render_template("ma_plot.html", contrasts=contrasts, no_data=no_data)

    contrast = request.form.get('contrast')
    apply_filters = request.form.get('apply_filters') == "true" # is not None
    pval = request.form.get('pval')
    fc = request.form.get('fc')
    min_counts = request.form.get('min_counts')
    max_counts = request.form.get('max_counts')
    filters = {
        'pval': pval,
        'fc': fc,
        'min_counts': min_counts,
        'max_counts': max_counts,
    }
    bi_df = rdb.get('ma_plot_all_{}_{}'.format(project_id, contrast))
    if not bi_df:
        return render_template("ma_plot.html", error="No data for the contrast {}".format(contrast),
                               selected_contrast=contrast, contrasts=contrasts, apply_filters=apply_filters,
                               filters=filters)
    df = pd.read_msgpack(bi_df)
    # columns: ['baseMean', 'log2FoldChange', 'lfcSE', 'stat', 'pvalue', 'padj', 'transcript']
    df = df.rename({'baseMean': 'x', 'log2FoldChange': 'y'}, axis='columns')
    df = df.fillna('')
    if apply_filters:
        if pval != '':
            pval = float(pval)
            df = df.loc[df["pvalue"] <= pval]
        if fc != '':
            fc = float(fc)
            df = df.loc[(df["y"] <= fc) & (df["y"] >= -1 * fc)]
        if min_counts != '':
            min_counts = int(min_counts)
            df = df.loc[df["x"] >= min_counts]
        if max_counts != '':
            max_counts = int(max_counts)
            df = df.loc[df["x"] <= max_counts]

    plot_series = {'name': contrast.replace('__', ' '),
                   'data': df.to_dict('records')}
    return render_template("ma_plot.html", contrasts=contrasts, selected_contrast=contrast, plot_series=plot_series,
                           apply_filters=apply_filters, genes=len(df), filters=filters)

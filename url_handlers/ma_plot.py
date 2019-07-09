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
        return render_template("ma_plot.html", contrasts=contrasts, no_data=no_data)

    contrast = request.form.get('contrast')

    pval = request.form.get('pval')
    fc = request.form.get('fc')
    bi_df = rdb.get('ma_plot_{}_{}'.format(project_id, contrast))
    if not bi_df:
        return render_template("ma_plot.html", error="No data for the contrast {}".format(contrast), pval=pval, fc=fc,
                               selected_contrast=contrast, contrasts=contrasts)
    df = pd.read_msgpack(bi_df)
    # columns: ['baseMean', 'log2FoldChange', 'lfcSE', 'stat', 'pvalue', 'padj', 'transcript']
    df = df.rename({'baseMean': 'x', 'log2FoldChange': 'y'}, axis='columns')
    plot_series = {'name': contrast.replace('__', ' '),
                   'data': df.to_dict('records')}
    return render_template("ma_plot.html", contrasts=contrasts, selected_contrast=contrast, pval=pval, fc=fc,
                           plot_series=plot_series)

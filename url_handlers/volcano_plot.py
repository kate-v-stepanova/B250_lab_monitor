import pandas as pd
import math
from flask import Blueprint, render_template, request
from flask_login import login_required
import json


volcano_plot = Blueprint('volcano_plot', __name__)


@volcano_plot.route('/volcano_plot/<project_id>', methods=['GET', 'POST'])
@login_required
def get_volcano_plot(project_id):
    from main import get_db
    rdb = get_db()
    contrasts = rdb.smembers('contrasts_{}'.format(project_id))
    contrasts = sorted([c.decode('utf-8') for c in contrasts])
    if request.method == 'GET':
        return render_template("volcano_plot.html", contrasts=contrasts)

    #  dash lines
    left = float(request.form.get('left'))
    right = float(request.form.get('right'))
    bottom = float(request.form.get('bottom'))

    left_line = round(math.log2(left), 3)
    right_line = round(math.log2(right), 3)
    bottom_line = -round(math.log10(bottom), 3)

    # else: (if request is POST) #
    contrast = request.form.get('contrast')
    if contrast is None:
        return render_template("volcano_plot.html", contrasts=contrasts, error='Contrast is not selected')

    # else: (if contrast is not None) #
    data = rdb.get('volcano_{}_{}'.format(project_id, contrast))
    if data is None:
        return render_template("volcano_plot.html", contrasts=contrasts, error='No data found for contrast: {}'.format(contrast))

    # else: (if data is not None) #
    data = json.loads(data)
    df = pd.DataFrame(data)

    df = df.round(decimals=3)

    df['-log10(pval)'] = -1 * df['pvalue'].apply(lambda x: math.log10(x))

    df['fc'] = 2 ** df['log2FoldChange']
    df = df.drop('padj', axis=1)
    df.columns = ['x', 'pvalue', 'gene', 'y', 'fc']
    df = df.round(decimals=3)

    # thresholds
    left_df = df.loc[(df['fc'] <= left) & (df['pvalue'] <= bottom)]
    right_df = df.loc[(df['fc'] >= right) & (df['pvalue'] <= bottom)]
    bottom_df = df[~df.isin(left_df) & ~df.isin(right_df)].dropna()

    # series
    plot_series = [{
        'name': contrast,
        'data': list(bottom_df.dropna().T.to_dict().values()),
        'turboThreshold': len(bottom_df),
        'marker': {
            'symbol': 'circle',
            'radius': 5,
        },
        'color': 'grey',
    },
        {
            'name': contrast,
            'data': list(left_df.dropna().T.to_dict().values()),
            'turboThreshold': len(left_df),
            'color': 'blue',
            'marker': {
                'symbol': 'circle',
                'radius': 5,
            },
        },
        {
            'name': contrast,
            'data': list(right_df.dropna().T.to_dict().values()),
            'turboThreshold': len(right_df),
            'color': 'red',
            'marker': {
                'symbol': 'circle',
                'radius': 5,
            },
        }]

    return render_template('volcano_plot.html', contrasts=contrasts, selected_contrast=contrast, plot_series=plot_series,
                           right=right_line, left=left_line, bottom=bottom_line, selected_thresholds={
                               'left': left,
                               'right': right,
                               'bottom': bottom,
                           })







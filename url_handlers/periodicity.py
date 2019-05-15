import os
import glob

import pandas as pd
from flask import Blueprint, render_template

periodicity = Blueprint('periodicity', __name__)

@periodicity.route('/periodicity/<dataset_id>')
def get_periodicity(dataset_id):
    from main import get_db
    rdb = get_db()

    result = rdb.get('{}_periodicity_heatmap'.format(dataset_id))
    if not result:
        return "No data for dataset {} found".format(dataset_id)

    full_df = pd.read_msgpack(result)
    samples = full_df['sample'].unique()

    plots1 = {}
    plots2 = {}

    for sample in samples:
        ends = full_df['end'].unique()
        lengths = full_df['length'].unique()
        region1 = "Distance from start (nt)"
        region2 = "Distance from stop (nt)"
        region1_df = full_df.loc[(full_df['sample'] == sample) & (full_df['region'] == region1)]
        region2_df = full_df.loc[(full_df['sample'] == sample) & (full_df['region'] == region2)]
        for end in ends:
            series1 = []
            series2 = []
            for length in lengths:
                df1 = region1_df.loc[(region1_df['length'] == length) & (region1_df['end'] == end)]
                # x = distance, y = count
                df1.columns = ['length', 'x', 'y', 'region', 'end', 'sample']
                df1 = df1.sort_values(by=['end', 'length', 'x'])
                series1.append({
                    'name': 'Length: {} nt'.format(length),
                    'data': df1.to_dict('records')
                })
                df2 = region2_df.loc[(region2_df['length'] == length) & (region2_df['end'] == end)]
                df2.columns = ['length', 'x', 'y', 'region', 'end', 'sample']
                df2 = df2.sort_values(by=['end', 'length', 'x'])
                series2.append({
                    'name': 'Length: {} nt'.format(length),
                    'data': df2.to_dict('records')
                })
            key = "{}_{}".format(sample, end.replace("' ", '_'))
            plots1[key] = series1
            plots2[key] = series2
    return render_template("periodicity.html", plot_names=list(plots1.keys()), series1=plots1, series2=plots2, dataset_id=dataset_id)

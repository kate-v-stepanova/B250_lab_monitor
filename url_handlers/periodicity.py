import pandas as pd
from flask import Blueprint, render_template
from flask_login import login_required

periodicity = Blueprint('periodicity', __name__)

@periodicity.route('/periodicity/<project_id>')
@login_required
def get_periodicity(project_id):
    from main import get_db
    rdb = get_db()

    result = rdb.get('{}_periodicity_heatmap'.format(project_id))
    if not result:
        return "No data for dataset {} found".format(project_id)

    full_df = pd.read_msgpack(result)
    full_df = full_df.sort_values(by=['end', 'length', 'dist'])
    full_df = full_df.replace({'sample': '.'}, '_') # javascript doesn't like dots
    full_df['end'] = full_df['end'].str.replace("' ", 'p ') # javascript doesn't like single quotes

    samples = list(full_df['sample'].unique())
    lengths = list(full_df['length'].unique())

    start_5p_plots = {}
    start_3p_plots = {}
    stop_5p_plots = {}
    stop_3p_plots = {}
    for sample in samples:
        # make 4 plots
        start_5p_df = full_df.loc[(full_df['region'] == "Distance from start (nt)") &
                                  (full_df['end'] == "5p end") &
                                  (full_df['sample'] == sample)]
        stop_5p_df = full_df.loc[(full_df['region'] == "Distance from stop (nt)") &
                                  (full_df['end'] == "5p end") &
                                  (full_df['sample'] == sample)]
        start_3p_df = full_df.loc[(full_df['region'] == "Distance from start (nt)") &
                                  (full_df['end'] == "3p end") &
                                  (full_df['sample'] == sample)]
        stop_3p_df = full_df.loc[(full_df['region'] == "Distance from stop (nt)") &
                                  (full_df['end'] == "3p end") &
                                  (full_df['sample'] == sample)]
        # columns
        start_5p_df.columns = ['length', 'x', 'y', 'region', 'end', 'sample']
        stop_5p_df.columns = ['length', 'x', 'y', 'region', 'end', 'sample']
        start_3p_df.columns = ['length', 'x', 'y', 'region', 'end', 'sample']
        stop_3p_df.columns = ['length', 'x', 'y', 'region', 'end', 'sample']

        # series per length
        for length in lengths:
            if sample not in start_5p_plots:
                start_5p_plots[sample] = []
                stop_5p_plots[sample] = []
                start_3p_plots[sample] = []
                stop_3p_plots[sample] = []
            start_5p_plots[sample].append({
                'name': "Length: {} nt".format(length),
                'data': start_5p_df.loc[start_5p_df['length'] == length].to_dict('records')
            })
            stop_5p_plots[sample].append({
                'name': "Length: {} nt".format(length),
                'data': stop_5p_df.loc[stop_5p_df['length'] == length].to_dict('records')
            })
            start_3p_plots[sample].append({
                'name': "Length: {} nt".format(length),
                'data': start_3p_df.loc[start_3p_df['length'] == length].to_dict('records')
            })
            stop_3p_plots[sample].append({
                'name': "Length: {} nt".format(length),
                'data': stop_3p_df.loc[stop_3p_df['length'] == length].to_dict('records')
            })

    return render_template("periodicity.html", project_id=project_id, plot_names=samples, start_5p_plots=start_5p_plots,
                           start_3p_plots=start_3p_plots, stop_5p_plots=stop_5p_plots, stop_3p_plots=stop_3p_plots)

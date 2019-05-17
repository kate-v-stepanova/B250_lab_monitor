import pandas as pd
from flask import Blueprint, render_template

periodicity_heatmap = Blueprint('periodicity_heatmap', __name__)

@periodicity_heatmap.route('/periodicity_heatmap/<dataset_id>')
def get_periodicity_heatmap(dataset_id):
    from main import get_db
    rdb = get_db()

    result = rdb.get('{}_periodicity_heatmap'.format(dataset_id))
    if not result:
        return "No data for dataset {} found".format(dataset_id)

    full_df = pd.read_msgpack(result)
    # columns: ['length', 'dist', 'count', 'region', 'end', 'sample']
    # ['length', 'dist', 'count', 'region', 'end', 'sample']

    full_df.columns = ['y', 'x', 'value', 'region', 'end', 'sample']
    full_df = full_df.replace({'sample': '.'}, '_')
    full_df = full_df.replace({'end': "' "}, "p ")
    full_df = full_df.sort_values(by=['x', 'y'])
    samples = list(full_df['sample'].unique())
    start_3p_plots = {}
    start_5p_plots = {}
    stop_3p_plots = {}
    stop_5p_plots = {}
    for sample in samples:
        ## make 4 plots
        start_5p_df = full_df.loc[(full_df['region'] == "Distance from start (nt)") &
                                  (full_df['end'] == "5' end") &
                                  (full_df['sample'] == sample)]
        stop_5p_df = full_df.loc[(full_df['region'] == "Distance from stop (nt)") &
                                  (full_df['end'] == "5' end") &
                                  (full_df['sample'] == sample)]
        start_3p_df = full_df.loc[(full_df['region'] == "Distance from start (nt)") &
                                  (full_df['end'] == "3' end") &
                                  (full_df['sample'] == sample)]
        stop_3p_df = full_df.loc[(full_df['region'] == "Distance from stop (nt)") &
                                  (full_df['end'] == "3' end") &
                                  (full_df['sample'] == sample)]

        # getting plots
        start_5p_plots[sample] = start_5p_df.to_dict('records')
        start_3p_plots[sample] = start_3p_df.to_dict('records')
        stop_5p_plots[sample] = stop_5p_df.to_dict('records')
        stop_3p_plots[sample] = stop_3p_df.to_dict('records')

    return render_template("periodicity_heatmap.html", dataset_id=dataset_id, start_5p_plots=start_5p_plots,
                           stop_5p_plots=stop_5p_plots, start_3p_plots=start_3p_plots, stop_3p_plots=stop_3p_plots, samples=samples)

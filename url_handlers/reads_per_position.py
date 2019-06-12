from flask import Blueprint, render_template
from flask_login import login_required
import pandas as pd

reads_per_position = Blueprint('reads_per_position', __name__)

@reads_per_position.route('/reads_per_position/<project_id>')
@login_required
def get_reads_per_position(project_id):
    # this import has to be here
    from main import get_db
    rdb = get_db()

    key = "{}_reads_per_position".format(project_id)
    binary_data = rdb.get(key)
    if binary_data is None:
        return "NO DATA for project {}".format(project_id)
    df = pd.read_msgpack(binary_data)

    plot_names = []
    plot_series = {}
    categories = {}
    gene_lengths = {
        'RNA18S5': 1869,
        'RNA28S5': 5070,
        'RNA5-8S5': 153,
    }

    genes = gene_lengths.keys()
    samples = df.get('sample').unique()
    print(samples)
    print(df.columns)
    for gene in genes:
        gene_length = gene_lengths.get(gene)
        for sample in samples:
            current_df = df.loc[(df['gene'] == gene) & (df['sample'] == sample)]
            print(len(current_df))
            if current_df.empty:
                continue

            series_df = pd.DataFrame(columns=['x', 'y', 'reads_info'], index=range(1, gene_length+1))
            series_df['x'] = range(1, gene_length+1)
            series_df['y'] = 0
            series_df['reads_info'] = ''
            plot_name = "{}_{}".format(gene, sample)
            plot_names.append(plot_name)
            categories[plot_name] = list(range(1, gene_length+1))
            for row_id, row in current_df.iterrows():
                position = row['start']
                series_df.loc[position, 'x'] = position
                series_df.loc[position, 'y'] = row['counts']
                series_df.loc[position, 'reads_info'] = row['reads_info'].replace(',', '<br> • ')
            plot_series[plot_name] = {
                'name': plot_name,
                'data': series_df.to_dict('records')
            }
    return render_template("reads_per_position.html", plot_names=plot_names, plot_series=plot_series,
                           categories=categories, project_id=project_id)

import os
import glob
from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

base_dir = "/Users/b250-admin/analysis/"


@app.route('/reads_per_position/<dataset_id>')
def hello_world(dataset_id):
    print(dataset_id)
    input_files = glob.glob(os.path.join(base_dir, dataset_id, 'rrna_positions/*_reads_per_position.txt'))
    plot_names = []
    plot_series = {}
    categories = {}
    gene_lengths = {
        'RNA18S5': 1869,
        'RNA28S5': 5070,
        'RNA5-8S5': 153,
        'RNA5-8S5-2': 153,
    }
    print(input_files)
    for input_file in input_files:
        df = pd.read_csv(input_file, sep='\t')
        filename = os.path.basename(input_file)
        plot_name = filename.replace('_reads_per_position.txt', '')
        sample_name, gene_name = plot_name.rsplit('_', 1)
        plot_names.append(plot_name)
        gene_length = gene_lengths[gene_name]
        categories[plot_name] = list(range(1, gene_length+1))

        series_df = pd.DataFrame(columns=['x', 'y', 'reads_info'], index=range(1, gene_length+1))
        series_df['x'] = range(1, gene_length+1)
        series_df['y'] = 0
        series_df['reads_info'] = ''
        for row_id, row in df.iterrows():
            position = row['start']
            series_df.loc[position, 'x'] = position
            series_df.loc[position, 'y'] = row['counts']
            series_df.loc[position, 'reads_info'] = row['reads_info'].replace(',', '<br> • ')
        plot_series[plot_name] = {
            'name': plot_name,
            'data': series_df.to_dict('records')
        }
    print(plot_series)
    return render_template("layout.html", plot_names=plot_names, plot_series=plot_series, categories=categories)

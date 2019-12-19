import pandas as pd
import numpy as np
from flask import Blueprint, render_template, request
from flask_login import login_required
import json

liquid_nitrogen = Blueprint('liquid_nitrogen', __name__)


@liquid_nitrogen.route('/liquid_nitrogen', methods=['GET', 'POST'])
@login_required
def get_liquid_nitrogen():
    from main import get_db
    y_pos = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    rdb = get_db()
    towers = [tower.decode('utf-8') for tower in rdb.smembers('towers')]
    series = {}
    for tower in towers:
        data = rdb.get(tower)
        data = json.loads(data)
        df = pd.DataFrame(data)
        df = df.fillna('null')
        df = df.drop(['Drawer', 'passage no.'], axis='columns')
        racks = df['Rack'].unique()
        print(df)
        for rack in racks:
            rack_series = []
            for y in y_pos:
                for x in range(1, 11):
                    df1 = df.loc[(df['Rack'] == rack) & (df['y'] == y) & (df['x'].astype(int) == x)]
                    if len(df1) == 0:
                        rack_series.append({
                            'pos': '{}{}'.format(y, x),
                            'Rack': rack,
                            'x': x - 1,
                            'y': y_pos.index(y),
                            'value': 0,
                            'color': '#FFFFFF',
                        })
                    else:
                        df1['pos'] = df1['y'].astype(str) + df1['x'].astype(str)
                        df1['y'] = y_pos.index(y)
                        df1['x'] = df1['x'] - 1
                        color = '#FFFFFF'
                        if df1.iloc[0]['value'] == 1:
                            color = '#F4796E' # red
                        elif df1.iloc[0]['value'] == 2:
                            color = '#EEF287' # yellow
                        df1['color'] = color
                        rack_series.append(df1.iloc[0].to_dict())
            key = 'Rack{}'.format(rack)
            series[key] = rack_series
    cell_lines = rdb.get('cell_lines')
    cell_lines = json.loads(cell_lines)
    cell_lines = pd.DataFrame(cell_lines)
    cell_lines.index = cell_lines['ID']
    cell_lines = cell_lines.to_dict('index')
    print(cell_lines)
    return render_template('liquid_nitrogen.html', series=series, cell_lines=cell_lines)

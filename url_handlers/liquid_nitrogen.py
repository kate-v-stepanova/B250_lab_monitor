import pandas as pd
from flask import Blueprint, render_template, request, make_response
from flask_login import login_required
import json

liquid_nitrogen = Blueprint('liquid_nitrogen', __name__)


@liquid_nitrogen.route('/liquid_nitrogen', methods=['GET', 'POST'])
@login_required
def get_liquid_nitrogen():
    # Rack colors and values:
    # empty: white - 0, full: red - 1, to approve: yellow - 2
    from main import get_db
    y_pos = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    rdb = get_db()
    towers = [tower.decode('utf-8') for tower in rdb.smembers('towers')]
    series = {}
    to_approve = rdb.get('to_approve')
    if to_approve is not None:
        to_approve = json.loads(to_approve)
        to_approve = pd.DataFrame(to_approve)
    else:
        to_approve = pd.DataFrame(columns=['tower', 'Position', 'Rack', 'x', 'y', 'Responsible Person', 'Date', 'comments',
                                           'prev_cell_line', 'prev_responsible', 'prev_comments', 'prev_date'])

    to_approve = to_approve.fillna('')
    for tower in towers:
        data = rdb.get(tower)
        if data is None:
            return render_template('liquid_nitrogen.html', error='No data found')
        data = json.loads(data)
        df = pd.DataFrame(data)
        df = df.fillna('null')
        racks = df['Rack'].astype(str).unique()
        for rack in racks:
            rack_series = []
            for y in y_pos:
                for x in range(1, 11):
                    # if y == 'J' and x == 10 and str(rack) == '5':
                    #     import pdb; pdb.set_trace()
                    approved = to_approve.loc[(to_approve['tower'] == tower) & (to_approve['Rack'].astype(str) == rack) &
                                              (to_approve['y'] == y) & (to_approve['x'].astype(int) == x)]
                    df1 = df.loc[(df['Rack'].astype(str) == rack) & (df['y'] == y) & (df['x'].astype(int) == x)]

                    if len(approved) != 0:
                        rack_series.append({
                            'pos': '{}{}'.format(y, x),
                            'Rack': rack,
                            'x': x-1,
                            'y': y_pos.index(y),
                            'value': 2, # means to approve
                            'color': '#EEF287', # yellow

                            'Responsible person': approved.iloc[0]['Responsible person'],
                            'ID': approved.iloc[0]['cell_line'],
                            'Date': approved.iloc[0]['Date'],
                            'status': 'to_confirm',

                            'prev_cell_line': approved.iloc[0]['prev_cell_line'], # cell_line_IDs
                            'prev_responsible': approved.iloc[0]['prev_responsible'],
                            'prev_comments': approved.iloc[0]['prev_comments'],
                            'prev_date': approved.iloc[0]['prev_date'],
                        })
                    elif len(df1) != 0:
                        df1['pos'] = df1['y'].astype(str) + df1['x'].astype(str)
                        df1['y'] = y_pos.index(y)
                        df1['x'] = df1['x'] - 1
                        df1['color'] = '#F4796E' # red
                        df1['value'] = 1 # means confirmed

                        rack_series.append(df1.iloc[0].to_dict())
                    else:
                        rack_series.append({
                            'pos': '{}{}'.format(y, x),
                            'Rack': rack,
                            'x': x - 1,
                            'y': y_pos.index(y),
                            'value': 0, # means empty
                            'color': '#FFFFFF',
                            'Tower': tower,
                        })
            key = '{}_Rack{}'.format(tower, rack)
            series[key] = rack_series
    cell_lines = rdb.get('cell_lines')
    if cell_lines is None:
        return render_template('liquid_nitrogen.html', error='No data found')

    cell_lines = json.loads(cell_lines)
    cell_lines = pd.DataFrame(cell_lines)
    cell_lines = cell_lines.fillna('')
    cell_lines.index = cell_lines['ID']
    cell_lines = cell_lines.to_dict('index')
    cell_lines_dropdown = [{'value': 'add_new', 'text': 'Add new'}]
    for key in cell_lines.keys():
        cell_lines_dropdown.append({
            'value': key,
            'text': key,
        })
    return render_template('liquid_nitrogen.html', series=series, cell_lines=cell_lines, cell_lines_dropdown=cell_lines_dropdown)


@liquid_nitrogen.route('/remove_from_rack', methods=['POST'])
@login_required
def remove_from_rack():
    from main import get_db
    data = request.get_json()
    print(data)
    return ""


@liquid_nitrogen.route('/liquid_nitrogen/update_rack', methods=['POST'])
@login_required
def add_cell_line():
    from main import get_db
    data = request.get_json()
    rdb = get_db()
    to_approve = rdb.get('to_approve')
    if to_approve is None:
        to_approve = pd.DataFrame(columns=['tower', 'pos', 'Rack', 'x', 'y', 'Responsible person', 'Date', 'Comments',
                                           'cell_line', 'prev_cell_line', 'prev_responsible', 'prev_comments', 'prev_date'])
    else:
        to_approve = json.loads(to_approve)
        to_approve = pd.DataFrame(to_approve)

    tower = data.get('tower')
    tower_data = rdb.get(tower)

    if tower_data is not None:
        tower_data = json.loads(tower_data)
        tower_data = pd.DataFrame(tower_data)
        current_pos_data = tower_data.loc[(tower_data['Rack'] == data.get('Rack')) & (tower_data['y'] == data.get('y')) &
                                          (tower_data['x'] == data.get('x'))]
        if len(current_pos_data) != 0:
            data['prev_cell_line'] = current_pos_data.iloc[0]['ID']
            data['prev_responsible'] = current_pos_data.iloc[0]['']

    # if there is already something on that position, then ...
    to_overwrite = to_approve.loc[(to_approve['Rack'] == data.get('Rack')) & (to_approve['tower'] == data.get('tower')) &
                                  (to_approve['pos'] == data.get('pos'))]
    # ... then drop it and ...
    if len(to_overwrite) != 0:
        to_approve = to_approve.drop(to_overwrite.index)
    # ... and add the new data
    to_approve = to_approve.append(data, ignore_index=True)

    # save to db
    try:
        rdb.set('to_approve', json.dumps(to_approve.to_dict('list')))
    except Exception as e:
        return make_response({'status': 'error', 'error': str(e)}, 500)

    return make_response({'status': 'success'}, 200)


@liquid_nitrogen.route('/liquid_nitrogen/create_cell_line', methods=['POST'])
@login_required
def create_cell_line():
    from main import get_db
    rdb = get_db()
    new_cell_line = request.get_json()
    cell_lines = rdb.get('cell_lines')
    if cell_lines is not None:
        cell_lines = json.loads(cell_lines)
        df = pd.DataFrame(cell_lines)
    else:
        df = pd.DataFrame(columns=new_cell_line.keys())
    # if cell line already exists - name not unique
    if len(df.loc[df['Cell line'] == new_cell_line.get('Cell line')]) != 0:
        return make_response({'status': 'error', 'error': 'Cell line {} already exists'.format(new_cell_line.get('Cell line'))}, 200)
    # ID not unique
    if len(df.loc[df['ID'] == new_cell_line.get('ID')]) != 0:
        return make_response({'status': 'error', 'error': 'Cell line {} already exists'.format(new_cell_line.get('ID'))}, 200)

    df = df.append(new_cell_line, ignore_index=True)
    try:
        rdb.set('cell_lines', json.dumps(df.to_dict('list')))
    except Exception as e:
        return make_response({'status': 'error', 'error': str(e)}, 500)

    return make_response({'status': 'success'}, 200)


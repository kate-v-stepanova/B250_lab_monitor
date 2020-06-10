import pandas as pd
from flask import Blueprint, render_template, request, make_response, current_app
from flask_login import login_required, current_user
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
        to_approve = pd.DataFrame(columns=['tower', 'pos', 'Rack', 'x', 'y', 'Responsible person', 'Date', 'Comments', 'cell_line',
                                           'prev_cell_line', 'prev_responsible', 'prev_comments', 'prev_date', 'status'])

    to_approve = to_approve.loc[to_approve['status'] == 'pending']
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
                            'color': '#ffcc00', # yellow

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
                        df1['x'] = df1['x'].astype(int) - 1
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

    liquid_nitrogen_admins = current_app.config.get('LIQUID_NITROGEN_ADMINS')
    if liquid_nitrogen_admins is None:
        liquid_nitrogen_admins = []

    if current_user.email in liquid_nitrogen_admins:
        to_approve = to_approve[['tower', 'Rack', 'pos', 'cell_line', 'prev_cell_line', 'Comments', 'Date', 'Responsible person']]
        to_approve_data = to_approve.to_dict('records')
        return render_template('liquid_nitrogen.html', series=series, cell_lines_dropdown=cell_lines_dropdown,
                               cell_lines=json.dumps(cell_lines).replace("""\xa0""", " "), to_approve=to_approve_data, admin=True)

    return render_template('liquid_nitrogen.html', series=series, cell_lines=json.dumps(cell_lines).replace("""\xa0""", " "),
                           cell_lines_dropdown=cell_lines_dropdown)


@liquid_nitrogen.route('/liquid_nitrogen/update_rack', methods=['POST'])
@login_required
def add_cell_line():
    from main import get_db
    data = request.get_json()
    if 'status' not in data.keys():
        data['status'] = 'pending'
    rdb = get_db()
    to_approve = rdb.get('to_approve')
    if to_approve is None:
        to_approve = pd.DataFrame(columns=['tower', 'pos', 'Rack', 'x', 'y', 'Responsible person', 'Date', 'Comments',
                                           'cell_line', 'prev_cell_line', 'prev_responsible', 'prev_comments', 'prev_date', 'status'])
    else:
        to_approve = json.loads(to_approve)
        to_approve = pd.DataFrame(to_approve)
        # to_approve['status'] = 'pending'

    to_approve = to_approve.loc[to_approve['status'] == 'pending']

    tower = data.get('tower')
    tower_data = rdb.get(tower)

    if tower_data is not None:
        tower_data = json.loads(tower_data)
        tower_data = pd.DataFrame(tower_data)
        current_pos_data = tower_data.loc[(tower_data['Rack'] == data.get('Rack')) & (tower_data['y'] == data.get('y')) &
                                          (tower_data['x'] == data.get('x'))]
        if len(current_pos_data) != 0:
            data['prev_cell_line'] = current_pos_data.iloc[0]['ID']
            data['prev_responsible'] = current_pos_data.iloc[0]['Responsible person']

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


@liquid_nitrogen.route('/liquid_nitrogen/search', methods=['POST'])
@login_required
def search():
    from main import get_db
    rdb = get_db()
    to_search = request.get_data()
    if to_search is None:
        return make_response({'status': 'error', 'error': 'No input received'})
    to_search = to_search.decode('utf-8').upper()

    to_approve = rdb.get('to_approve')
    if to_approve is not None:
        to_approve = json.loads(to_approve)
        to_approve = pd.DataFrame(to_approve)
    else:
        to_approve = pd.DataFrame(columns=['cell_line', 'prev_cell_line'])


    cell_lines = rdb.get('cell_lines')
    cell_lines = json.loads(cell_lines)
    cell_lines = pd.DataFrame(cell_lines)
    cell_lines = cell_lines.fillna('')


    # search by ID or name
    found = cell_lines.loc[(cell_lines['ID'].str.upper().str.contains(to_search)) | (cell_lines['Cell line'].str.upper().str.contains(to_search))]

    results_df = None

    towers = [tower.decode('utf-8') for tower in rdb.smembers('towers')]
    for tower in towers:
        data = rdb.get(tower)
        if data is None:
            continue
        data = json.loads(data)
        df = pd.DataFrame(data)
        df = pd.merge(df, found, on='ID')
        if len(df) == 0:
            continue

        df['tower'] = tower
        df['status'] = 'confirmed'
        if results_df is None:
            results_df = df
        else:
            results_df = results_df.append(df, ignore_index=True)
    found2 = to_approve.loc[(to_approve['cell_line'].str.upper().str.contains(to_search)) |
                            (to_approve['prev_cell_line'].str.upper().str.contains(to_search))]

    found2 = pd.merge(found2, cell_lines, left_on='cell_line', right_on='ID')
    found2['status'] = 'to approve'

    # results_df = results_df.loc[~results_df['ID'].isin(found2['ID'].tolist())]
    if results_df is not None:
        results_df = results_df.append(found2, ignore_index=True)
    else:
        results_df = found2

    results_df = results_df.fillna('')

    results_df = results_df[['ID', 'Cell line', 'tower', 'Rack', 'pos', 'Responsible person', 'Date', 'status']]
    results_df['Rack'] = results_df['Rack'].astype(int)

    html_result = '<table class="table table-hover table-sm" id="table_search"><tr>'
    for column in results_df.columns:
        html_result += '<th>{}</th>'.format(column)

    html_result += '</tr>'

    for index, row in results_df.iterrows():
        if row['status'] == 'to approve':
            html_result += '<tr class="table-warning">'
        else:
            html_result += '<tr>'
        for column in results_df:
            html_result += '<td>{}</td>'.format(row[column])
    html_result += '</tr>'
    html_result += '</table>'

    return make_response({'status': 'success', 'html_result': html_result}, 200)


@liquid_nitrogen.route('/liquid_nitrogen/upload', methods=['POST'])
@login_required
def upload():
    data = request.form.get('lq_file')
    return make_response({'status': 'success'}, 200)


@liquid_nitrogen.route('/liquid_nitrogen/approve_decline', methods=['POST'])
@login_required
def approve_decline():
    from main import get_db
    rdb = get_db()
    data = request.get_data()
    if data is None:
        return make_response({'status': 'error', 'error': 'no data received'}, 200)
    data = json.loads(data.decode('utf-8'))
    action = data.get('action')

    requests = rdb.get('to_approve')
    if requests is None:
        return make_response({'status': 'error', 'error': 'No records in the database'}, 200)
    requests = json.loads(requests)
    requests = pd.DataFrame(requests)
    req = requests.loc[(requests['tower'] == data.get('tower')) & (requests['Rack'] == data.get('Rack')) &
                       (requests['pos'] == data.get('pos'))]
    if len(req) == 0:
        return make_response({'status': 'error', 'error': 'Cant find a record in the database'}, 200)

    tower_data = rdb.get(req['tower'].tolist()[0])
    if tower_data is None:
        tower_df = pd.DataFrame(columns=['ID', 'Rack', 'Date', 'Responsible person', 'Comments', 'pos', 'x', 'y'])
    else:
        tower_df = pd.DataFrame(json.loads(tower_data))

    if action == 'approve':
        requests.loc[req.index, 'status'] = 'approved'
        rdb.set('to_approve', json.dumps(requests.to_dict('list')))

        pos = tower_df.loc[(tower_df['Rack'] == data.get('Rack')) & (tower_df['pos'] == data.get('pos'))]
        if len(pos) == 0:

            # if added to a new position
            if not req['prev_cell_line'].tolist()[0]:
                to_append = req[['cell_line', 'Rack', 'Date', 'Responsible person', 'Comments', 'pos', 'x', 'y']]
                to_append.columns = ['ID', 'Rack', 'Date', 'Responsible person', 'Comments', 'pos', 'x', 'y']
                tower_df = tower_df.append(to_append, ignore_index=True)

                rdb.set(data.get('tower'), json.dumps(tower_df.to_dict('list')))
                return make_response({'status': 'success', 'info': 'Request has been approved'}, 200)

            # if requested from a postion
            else:
                return make_response({'status': 'error', 'error': 'You cant request from a current positon, because it is empty'}, 200)

        else: # len(pos) == 1:
            # remove from pos
            if not req['cell_line'].tolist()[0]:
                tower_df = tower_df.drop(pos.index)
                rdb.set(data.get('tower'), json.dumps(tower_df.to_dict('list')))
                return make_response({'status': 'success', 'info': 'Request has been approved'}, 200)

            else:
                return make_response({'status': 'error', 'error': 'Some logic is wrong'}, 200)

    elif action == 'decline':
        requests.loc[req.index, 'status'] = 'declined'
        rdb.set('to_approve', json.dumps(requests.to_dict('list')))
        return make_response({'status': 'success', 'info': 'Request has been declined'}, 200)
    else:
        make_response({'status': 'error', 'error': 'Unknown action "{}"'.format(action)}, 200)

    return make_response({'status': 'success'}, 200)



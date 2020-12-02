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
    to_approve = to_approve.fillna('')
    towers = set(towers + to_approve['tower'].tolist())

    user_requests = to_approve.loc[to_approve['Responsible person'] == current_user.email]
    user_requests = user_requests[['tower', 'Rack', 'pos', 'cell_line', 'prev_cell_line', 'Comments', 'Date', 'Responsible person', 'status']]
    user_requests = user_requests[::-1] # reverse order
    if len(user_requests) > 10:
        user_requests = user_requests[:10]
    to_approve = to_approve.loc[to_approve['status'] == 'pending']
    for tower in towers:
        data = rdb.get(tower)
        racks = []
        if data is not None:
            data = json.loads(data)
            df = pd.DataFrame(data)
            df = df.fillna('null')
            racks += set(list(df['Rack'].astype(str).unique()) + list(to_approve.loc[to_approve['tower'] == tower, 'Rack'].astype(str).unique()))
        else:
            racks += to_approve['Rack'].astype(str).unique()
            df = pd.DataFrame(columns=['Comments', 'Date', 'ID', 'Rack', 'Responsible person', 'pos', 'x', 'y'])
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
    cell_lines['tubes_available'] = cell_lines['tubes_available'].fillna(0)

    available_cell_lines = cell_lines.loc[cell_lines['tubes_available'].astype(int) != 0]
    available_cell_lines = available_cell_lines[['ID', 'Cell line', 'tubes_available']]
    available_cell_lines = available_cell_lines.to_dict('records')

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

    users = rdb.hgetall('users')
    users = [] if users is None else users.keys()
    users = [user.decode('utf-8') for user in users]

    to_approve = to_approve[
        ['tower', 'Rack', 'pos', 'cell_line', 'prev_cell_line', 'Comments', 'Date', 'Responsible person']]
    to_approve_data = to_approve.to_dict('records')
    if current_user.email in liquid_nitrogen_admins:
        user_requests = user_requests.to_dict('records')

        return render_template('liquid_nitrogen.html', series=series, cell_lines_dropdown=cell_lines_dropdown,
                               cell_lines=json.dumps(cell_lines).replace("""\xa0""", " "), to_approve=to_approve_data,
                               admin=True, users=users, current_user=current_user.email, available_cell_lines=available_cell_lines,
                               user_requests=user_requests)
    else:

        user_requests = user_requests.to_dict('records')
        return render_template('liquid_nitrogen.html', series=series, cell_lines_dropdown=cell_lines_dropdown, to_approve=to_approve_data,
                               cell_lines=json.dumps(cell_lines).replace("""\xa0""", " "), user_requests=user_requests,
                               admin=False, users=users, current_user=current_user.email, available_cell_lines=available_cell_lines)

    # return render_template('liquid_nitrogen.html', series=series, cell_lines=json.dumps(cell_lines).replace("""\xa0""", " "),
    #                        cell_lines_dropdown=cell_lines_dropdown)


@liquid_nitrogen.route('/liquid_nitrogen/update_rack', methods=['POST'])
@login_required
def update_rack():
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

    to_approve = to_approve.loc[to_approve['status'] == 'pending']
    tower = data.get('tower')
    tower_data = rdb.get(tower)

    if tower_data is not None:
        tower_data = json.loads(tower_data)
        tower_data = pd.DataFrame(tower_data)

    pos = data.get('pos')
    if type(pos) == str:
        pos = [pos]

    # if there is already something on that positions, then ...
    to_overwrite = to_approve.loc[(to_approve['Rack'] == data.get('Rack')) & (to_approve['tower'] == data.get('tower')) &
                                  (to_approve['pos'].isin(pos))]
    # ... then drop it and ...
    if len(to_overwrite) != 0:
        to_approve = to_approve.drop(to_overwrite.index)
    # ... and add the new data

    for p in pos:
        cur_data = data
        cur_data['pos'] = p
        cur_data['y'] = p[0]
        cur_data['x'] = int(p[1:])
        if tower_data is not None:
            current_pos_data = tower_data.loc[(tower_data['Rack'].astype(int) == int(data.get('Rack', 0))) & \
                                              (tower_data['pos'] == p)]
            if len(current_pos_data) != 0:
                cur_data['prev_cell_line'] = current_pos_data.iloc[0]['ID']
                cur_data['prev_responsible'] = current_pos_data.iloc[0]['Responsible person']

        to_approve = to_approve.append(cur_data, ignore_index=True)
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
    df['tubes_available'] = df['tubes_available'].fillna(0)
    # todo: later
    # # if name exists but id is different
    # if len(df.loc[df['Cell line'] == new_cell_line.get('Cell line')]) != 0:
    #     existing = df.loc[df['Cell line'] == new_cell_line.get('Cell line')]
    #     if new_cell_line.get('ID')

    # if exists - overwrite
    if len(df.loc[df['ID'] == new_cell_line.get('ID')]) != 0:
        for key in new_cell_line.keys():
            df.loc[df['ID'] == new_cell_line.get('ID'), key] = new_cell_line[key]
    else:
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
    cell_line_ids = found['ID'].tolist()
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

    found2 = to_approve.loc[(to_approve['cell_line'].isin(cell_line_ids)) |
                            (to_approve['prev_cell_line'].isin(cell_line_ids))]

    empty = found2.loc[found2['cell_line'] == '']
    found2.loc[empty.index, 'cell_line'] = found2.loc[empty.index, 'prev_cell_line']

    found2 = pd.merge(found2, cell_lines, left_on='cell_line', right_on='ID')
    found2['status'] = 'pending'


    # results_df = results_df.loc[~results_df['ID'].isin(found2['ID'].tolist())]
    if results_df is not None:
        results_df = results_df.append(found2, ignore_index=True)
    else:
        results_df = found2

    results_df = results_df.fillna('')

    results_df = results_df[['ID', 'Cell line', 'tower', 'Rack', 'pos', 'Responsible person', 'Date', 'status']]
    results_df['Rack'] = results_df['Rack'].astype(int)

    results_df = results_df.drop_duplicates(['tower', 'Rack', 'pos'], keep='last')

    html_result = '<table class="table table-hover table-sm" id="table_search"><tr>'
    for column in results_df.columns:
        html_result += '<th>{}</th>'.format(column)

    html_result += '<th></th><th></th></tr>'

    for index, row in results_df.iterrows():
        if row['status'] == 'pending':
            html_result += '<tr class="table-warning" id="{}_{}_{}">'.format(row['tower'], row['Rack'], row['pos'])
        else:
            html_result += '<tr id="{}_{}_{}">'.format(row['tower'], row['Rack'], row['pos'])
        for column in results_df:
            if column == 'status':
                span_class = ''
                if row['status'] == 'pending':
                    span_class = 'badge badge-warning'
                elif row['status'] == 'approved' or row['status'] == 'confirmed':
                    span_class = 'badge badge-success'
                elif row['status'] == 'declined':
                    span_class = 'badge badge-danger'
                html_result += '<td class="{}"><span class="{}">{}</span></td>'.format(column.replace(' ', '_'),
                                                                                       span_class, row[column])
            else:
                html_result += '<td class="{}">{}</td>'.format(column.replace(' ', '_'), row[column])

        html_result += '<td><button type="button" class="btn btn-sm btn-outline-primary" id="edit_search">Edit</button></td>'
        if row['status'] != 'pending':
            html_result += '<td><button type="button" class="btn btn-sm btn-outline-secondary request_search" id="request_search">Request</button></td>'
        else:
            html_result += '<td></td>'

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

        pos = tower_df.loc[(tower_df['Rack'].astype(str) == str(data.get('Rack', '0'))) & (tower_df['pos'] == data.get('pos'))]
        if len(pos) == 0:

            # if added to a new position
            if not req['prev_cell_line'].tolist()[0]:
                to_append = req[['cell_line', 'Rack', 'Date', 'Responsible person', 'Comments', 'pos', 'x', 'y']]
                to_append.columns = ['ID', 'Rack', 'Date', 'Responsible person', 'Comments', 'pos', 'x', 'y']
                tower_df = tower_df.append(to_append, ignore_index=True)

                rdb.set(data.get('tower'), json.dumps(tower_df.to_dict('list')))

                requests.loc[req.index, 'status'] = 'approved'
                rdb.set('to_approve', json.dumps(requests.to_dict('list')))
                return make_response({'status': 'success', 'info': 'Request has been approved'}, 200)

            # if requested from a postion
            else:
                return make_response({'status': 'error', 'error': 'You cant request from a current positon, because it is empty'}, 200)

        else: # len(pos) == 1:
            # remove from pos
            tower_df = tower_df.drop(pos.index)
            rdb.set(data.get('tower'), json.dumps(tower_df.to_dict('list')))
            # change status
            requests.loc[req.index, 'status'] = 'approved'
            rdb.set('to_approve', json.dumps(requests.to_dict('list')))
            return make_response({'status': 'success', 'info': 'Request has been approved'}, 200)

    elif action == 'decline':
        requests.loc[req.index, 'status'] = 'declined'
        rdb.set('to_approve', json.dumps(requests.to_dict('list')))
        # update number of available tubes
        cell_lines = rdb.get('cell_lines')
        cell_lines = json.loads(cell_lines)
        cell_df = pd.DataFrame(cell_lines)
        curr_cell_line = cell_df.loc[cell_df['ID'] == data.get('cell_line_id')]
        cell_df.loc[cell_df['ID'] == data.get('cell_line_id'), 'tubes_available'] = \
            curr_cell_line['tubes_available'].astype(int) + 1
        rdb.set('cell_lines', json.dumps(cell_df.to_dict('list')))
        return make_response({'status': 'success', 'info': 'Request has been declined'}, 200)
    elif action == 'cancel':
        # update number of available tubes
        cell_lines = rdb.get('cell_lines')
        cell_lines = json.loads(cell_lines)
        cell_df = pd.DataFrame(cell_lines)
        curr_cell_line = cell_df.loc[cell_df['ID'] == data.get('cell_line_id')]
        cell_df.loc[cell_df['ID'] == data.get('cell_line_id'), 'tubes_available'] = \
            curr_cell_line['tubes_available'].astype(int) + 1
        rdb.set('cell_lines', json.dumps(cell_df.to_dict('list')))

        # remove from requests
        requests = requests.drop(req.index)
        if len(requests) == 0:
            rdb.delete('to_approve')
        else:
            rdb.set('to_approve', json.dumps(requests.to_dict('list')))
        return make_response({'status': 'success', 'info': 'Request has been cancelled'}, 200)
    else:
        make_response({'status': 'error', 'error': 'Unknown action "{}"'.format(action)}, 200)

    return make_response({'status': 'success'}, 200)


@liquid_nitrogen.route('/liquid_nitrogen/export_data', methods=['POST'])
@login_required
def export_data():
    from main import get_db
    rdb = get_db()
    cell_lines = rdb.get('cell_lines')
    cell_lines = json.loads(cell_lines)
    cell_lines = pd.DataFrame(cell_lines)
    cell_lines = cell_lines.fillna('')

    to_approve = rdb.get('to_approve')
    to_approve = json.loads(to_approve)
    to_approve = pd.DataFrame(to_approve)
    to_approve = to_approve.fillna('')
    to_approve = pd.merge(to_approve, cell_lines, left_on='cell_line', right_on='ID')
    to_approve = to_approve[['ID', 'Cell line', 'Rack', 'tower', 'pos', 'Media (Freezing Medium)', 'transfected plasmid',
                             'selection', 'Typ', 'Date', 'Responsible person', 'Biosafety level S1/S2', 'Comments',
                             'Mycoplasma checked', 'Source', 'status']]
    to_approve.columns = ['ID', 'Cell line', 'Rack', 'Tower', 'Position', 'Media (Freezing Medium)', 'transfected plasmid',
                          'selection', 'Typ', 'Date', 'Responsible person', 'Biosafety level S1/S2', 'Comments',
                          'Mycoplasma checked', 'Source', 'status']

    towers = [tower.decode('utf-8') for tower in rdb.smembers('towers')]
    full_df = None
    for tower in towers:
        data = rdb.get(tower)

        data = json.loads(data)
        df = pd.DataFrame(data)
        df = df.fillna('')
        df['Tower'] = tower

        if full_df is None:
            full_df = df
        else:
            full_df = full_df.append(df)

    full_df = pd.merge(full_df, cell_lines, on='ID')
    full_df['Position'] = full_df['pos']
    full_df = full_df.drop(['pos', 'x', 'y'], axis='columns')

    full_df['status'] = 'confirmed'
    full_df = full_df.append(to_approve, ignore_index=True)
    full_df = full_df[['ID', 'Cell line', 'Rack', 'Tower', 'Position', 'Media (Freezing Medium)', 'transfected plasmid',
                             'selection', 'Typ', 'Date', 'Responsible person', 'Biosafety level S1/S2', 'Comments',
                             'Mycoplasma checked', 'Source', 'status']]
    content = full_df.to_csv(sep=";", index=False)
    return make_response({'status': 'success', 'csv_content': content}, 200)


@liquid_nitrogen.route('/liquid_nitrogen/get_cell_line_info', methods=['POST'])
@login_required
def get_cell_line_info():
    from main import get_db
    rdb = get_db()
    data = request.get_data()
    if data is None:
        return make_response({'status': 'error', 'error': 'no data received'}, 200)
    data = json.loads(data.decode('utf-8'))

    cell_line_id = data.get('cell_line_id')
    to_approve = rdb.get('to_approve')
    if to_approve is not None:
        to_approve = json.loads(to_approve)
        to_approve = pd.DataFrame(to_approve)
    else:
        to_approve = pd.DataFrame(columns=['tower', 'pos', 'Rack', 'x', 'y', 'Responsible person', 'Date', 'Comments',
                       'cell_line', 'prev_cell_line', 'prev_responsible', 'prev_comments', 'prev_date', 'status'])
    results = None
    found = to_approve.loc[(to_approve['cell_line'] == cell_line_id) | (to_approve['prev_cell_line'] == cell_line_id)]
    if len(found) != 0:
        found = found[['tower', 'Rack', 'pos', 'status']]
        results = found.to_dict('records')

    towers = [tower.decode('utf-8') for tower in rdb.smembers('towers')]
    for tower in towers:
        data = rdb.get(tower)
        if data is None:
            continue
        data = json.loads(data)
        df = pd.DataFrame(data)
        found2 = df.loc[df['ID'] == cell_line_id]
        if len(found2) != 0:
            found2['tower'] = tower
            found2 = found2[['tower', 'Rack', 'pos', 'status']]
            if results is None:
                results = found2.to_dict('records')
            else:
                results.append(found2.to_dict('records'))
    if results is None:
        results = []
    return make_response({'status': 'success', 'results': results}, 200)


@liquid_nitrogen.route('/liquid_nitrogen/delete_cell_line', methods=['POST'])
@login_required
def delete_cell_line():
    from main import get_db
    rdb = get_db()
    data = request.get_data()
    if data is None:
        return make_response({'status': 'error', 'error': 'no data received'}, 200)
    data = json.loads(data.decode('utf-8'))
    cell_line_id = data.get('cell_line_id')

    to_approve = rdb.get('to_approve')

    if to_approve is not None:
        to_approve = json.loads(to_approve)
        to_approve = pd.DataFrame(to_approve)
    else:
        to_approve = pd.DataFrame(columns=['tower', 'pos', 'Rack', 'x', 'y', 'Responsible person', 'Date', 'Comments',
                       'cell_line', 'prev_cell_line', 'prev_responsible', 'prev_comments', 'prev_date', 'status'])

    found = to_approve.loc[to_approve['cell_line'] == cell_line_id]
    to_approve = to_approve.drop(found.index)
    rdb.set('to_approve', json.dumps(to_approve.to_dict('list')))

    towers = [tower.decode('utf-8') for tower in rdb.smembers('towers')]
    for tower in towers:
        data = rdb.get(tower)
        if data is None:
            continue
        data = json.loads(data)
        df = pd.DataFrame(data)
        found = df.loc[df['ID'] == cell_line_id]
        if len(found) != 0:
            df = df.drop(found.index)
            rdb.set(tower, json.dumps(df.to_dict('list')))

    cell_lines = rdb.get('cell_lines')

    if cell_lines is not None:
        cell_lines = rdb.get('cell_lines')
        cell_lines = json.loads(cell_lines)
        cell_lines = pd.DataFrame(cell_lines)
        found = cell_lines.loc[cell_lines['ID'] == cell_line_id]
        cell_lines = cell_lines.drop(found.index)
        rdb.set('cell_lines', json.dumps(cell_lines.to_dict('list')))

    return make_response({'status': 'success', 'info': 'Cell line has been removed from the DB. All associated positions have been cleared'}, 200)

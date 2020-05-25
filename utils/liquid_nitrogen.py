import os
import click
import pandas as pd
import redis
import json

localhost = "172.22.24.88" # local
remote_host = "172.22.25.100" # remote
home = "192.168.0.157"
port = "6379"


@click.group()
def cli():
    # do nothing
    pass

def rows_from_range(row):
    df = pd.DataFrame(columns=row.index)
    if row['x1'] is not None:
        for i in range(row['x1'], row['x2'] + 1):
            row['x'] = i
            df = df.append(row)
    return df


@cli.command()
@click.option('--remote/--local', default=False)
@click.option('--host', '-h', 'host')
@click.argument('filename')
@click.argument('tower') # example: tower7
def upload(remote, host, filename, tower):
    if os.path.isfile(filename):
        df = pd.read_csv(filename, sep=";")
        import pdb; pdb.set_trace()
        df = df.drop(['Unnamed: 16', 'Unnamed: 4'], axis=1)
        # df1 = df.drop(['Rack', 'Drawer', 'Position', 'passage no.', 'Unnamed: 16', 'Date', 'Responsible person',
        #               'Comments'], axis='columns')
        df1 = df.drop(['Rack', 'Position', 'Tower', 'Date', 'Responsible person', 'Comments'], axis='columns')

        df1 = df1.fillna('')
        df1 = df1.drop_duplicates('ID')
        data = df1.to_dict('list')
        data = json.dumps(data)
        if host is None:
            host = remote_host if remote else localhost
        rdb = redis.StrictRedis(host)
        rdb.set('cell_lines', data)

        # locations
        df2 = df[['ID', 'Rack', 'Position', 'Date', 'Responsible person', 'Comments']]
        pos = df2['Position'].str.split('-', expand=True)
        y = pos[0].str[0] # e.g. A, B, C...
        x1 = pos[0].str[1:] #
        x2 = pos[1]
        df2['y'] = y.fillna('')
        df2['x1'] = x1.fillna(0).astype(int)
        df2['x2'] = x2.fillna(0).astype(int)
        df2['x'] = 0
        df3 = pd.DataFrame(columns=df2.columns)
        for i, row in df2.iterrows():
            df3 = df3.append(rows_from_range(row))
        df3 = df3.drop(['x1', 'x2', 'Position'], axis='columns')
        df3['Rack'] = df3['Rack'].fillna(0)
        df3['Rack'] = df3['Rack'].astype(int)
        df3['pos'] = df3['y'].astype(str) + df3['x'].astype(str)
        data = df3.to_dict('list')
        data = json.dumps(data)
        rdb.set(tower, data)
        rdb.sadd('towers', tower)

    else:
        print("File does not exist? {}".format(filename))


if __name__ == '__main__':
    cli()

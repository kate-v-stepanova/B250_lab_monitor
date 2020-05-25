import os
import glob

import click
import redis
import pandas as pd


@click.group()
def cli():
    # do nothing
    pass

BASE_DIR = "/icgc/dkfzlsdf/analysis/OE0532"

@cli.command()
@click.argument('project_id')
@click.option('--remote/--local', default=False)
def reads_per_position(project_id, remote):
    """
    Reads the data from *_reads_per_position.txt files,
    aggregates all samples into one DataFrame,
    converts it to pandas binary string and saves to Redis.
    This will update an existing record, or create a new one if does not exist.
    """
    # default host: 127.0.0.1, default port: 6379.
    # to change, use redis.StrictRedis(host=HOST, port=PORT)
    # but we are not going to change this

    if remote:
        rdb = redis.StrictRedis(host="172.22.54.5")
    else:
        rdb = redis.StrictRedis("localhost")

    rdb.sadd('projects', project_id)

    rrna_positions_dir = "analysis/output/rrna_positions"
    path = os.path.join(BASE_DIR, project_id, rrna_positions_dir, '*_reads_per_position.txt')
    input_files = glob.glob(path)
    if not input_files:
        print("No input files found: {}".format(path))
        exit(0)
    full_df = None
    for input_file in input_files:
        df = pd.read_csv(input_file, sep='\t')
        filename = os.path.basename(input_file)
        plot_name = filename.replace('_reads_per_position.txt', '')
        sample_name, gene_name = plot_name.rsplit('_', 1)
        df['sample'] = sample_name
        df['gene'] = gene_name
        if full_df is None:
            full_df = df
        else:
            full_df = full_df.append(df, ignore_index=True)
    key = "{}_reads_per_position".format(project_id)

    # save a binary string
    print("Saving key to redis: {}".format(key))
    rdb.set(key, full_df.to_msgpack())

@cli.command()
@click.argument('project_id')
@click.option('--remote/--local', default=False)
def periodicity(project_id, remote):
    if remote:
        rdb = redis.StrictRedis(host="172.22.54.5")
    else:
        rdb = redis.StrictRedis("172.22.24.88")
    projects = rdb.smembers('projects')
    if project_id not in projects:
        rdb.sadd('projects', project_id)
    path = os.path.join(BASE_DIR, project_id, 'analysis/output/periodicity/*.heatmap.tsv')
    input_files = glob.glob(path)
    if not input_files:
        print("No input files found: {}".format(path))
        exit(0)
    full_df = None
    for input_file in input_files:
        df = pd.read_csv(input_file, sep='\t')
        samplename = os.path.basename(input_file).replace('.heatmap.tsv', '').replace('.', '_')
        df['sample'] = samplename
        if full_df is None:
            full_df = df
        else:
            full_df = full_df.append(df, ignore_index=True)
    key = "{}_periodicity_heatmap".format(project_id)

    if rdb.exists(key):
        rdb.delete(key)
    rdb.set(key, full_df.to_msgpack())


@cli.command()
@click.argument('project_id')
def copy_periodicity(project_id):
    remote = redis.StrictRedis('172.22.54.5')
    local = redis.StrictRedis('172.22.24.88')
    import pdb; pdb.set_trace()
    key = "{}_periodicity_heatmap".format(project_id)
    dt = pd.read_msgpack(remote.get(key))
    local.set(key, pd.to_msgpack(dt))

if __name__ == '__main__':
    cli()
